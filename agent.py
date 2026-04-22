"""
agent.py — local autonomous runner for the autozip loop.

This is a purpose-built agent runner, not a general-purpose coding agent. It
implements the Karpathy-style loop as a tight state machine, which works
dramatically better with local models than a free-form "be autonomous" prompt.

The loop:
  1. Build a prompt containing: program.md rules, current compress.py,
     recent findings.md, current best size, and a menu of candidate ideas
     not yet tried.
  2. Ask the local model for ONE hypothesis + the full rewritten compress.py,
     returned as strict JSON.
  3. Apply the rewrite to compress.py.
  4. Run run_experiment.py, parse the two-line result.
  5. Classify Positive / Negative, append to findings.md with the model's
     stated reasoning + the measured outcome.
  6. If Positive: save a unified diff to confirmed_wins/, update BEST.md.
  7. Reset compress.py to baseline + all confirmed wins re-applied.
  8. Loop.

Backend: Ollama HTTP API at localhost:11434 by default. Any OpenAI-compatible
local server works — edit OLLAMA_URL and MODEL below, or set env vars
AUTOZIP_OLLAMA_URL and AUTOZIP_MODEL.

Dependencies: Python 3.10+, `requests` (pip install requests). Optional:
`patch` command-line tool for applying diffs on reset (falls back to pure
Python if absent).

Usage:
    # In one terminal:
    ollama serve

    # In another:
    ollama pull devstral-small:24b      # or qwen2.5-coder:14b, etc.
    AUTOZIP_MODEL=devstral-small:24b python agent.py

Stop with Ctrl-C. All state is on disk (findings.md, confirmed_wins/,
BEST.md), so you can resume at any time.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: install dependencies with `pip install requests`", file=sys.stderr)
    sys.exit(1)


# ------------------------------- configuration ------------------------------

ROOT = Path(__file__).parent.resolve()
COMPRESS_PY = ROOT / "compress.py"
BASELINE_PY = ROOT / "baseline" / "compress.py"
HARNESS = ROOT / "run_experiment.py"
FINDINGS = ROOT / "findings.md"
BEST_MD = ROOT / "BEST.md"
WINS_DIR = ROOT / "confirmed_wins"
PROGRAM_MD = ROOT / "program.md"
RUN_LOG = ROOT / "run.log"

OLLAMA_URL = os.environ.get("AUTOZIP_OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("AUTOZIP_MODEL", "devstral-small:24b")
# Cap the model's output; full compress.py rewrites are small.
MAX_TOKENS = int(os.environ.get("AUTOZIP_MAX_TOKENS", "4096"))
# Temperature: low but not zero. Zero causes loops of identical hypotheses.
TEMPERATURE = float(os.environ.get("AUTOZIP_TEMPERATURE", "0.4"))
# How many recent findings entries to include in each prompt. Trimmed to keep
# context small on local models.
FINDINGS_TAIL_CHARS = 6000
# Cap on consecutive failed/crashed experiments before we stop and shout.
MAX_CONSECUTIVE_CRASHES = 5


# Candidate hypotheses seeded for the agent. Local models struggle to invent
# from scratch but are fine at picking from a menu and implementing one
# cleanly. The agent may also invent its own; the menu is a floor, not a ceiling.
IDEA_MENU = """\
- Raise compresslevel (try 9 if not already at 9).
- Skip DEFLATE on already-compressed extensions (.gz, .zip, .jpg, .jpeg, .png,
  .mp4, .webp, .7z, .xz, .bz2, .mp3, .avif) by using ZIP_STORED for them.
- Use ZIP_BZIP2 for files that compress poorly with DEFLATE but not already
  compressed (some text corpora benefit).
- Use ZIP_LZMA for large text files (better ratio than DEFLATE, at cost of
  CPU; widely readable by modern unzip).
- Sort files by extension before adding, so similar files are adjacent in the
  archive — DEFLATE's 32KB window can't cross file boundaries in .zip, so
  this specifically does NOT help standard zip (log as Negative with that
  reason if tried).
- For each file, try multiple methods (STORED, DEFLATED, BZIP2, LZMA), keep
  the smallest result. Per-file best-of-N. More CPU, often smaller archive.
- Use zlib.compressobj directly with strategy=Z_FILTERED for mostly-numeric
  binary data, Z_HUFFMAN_ONLY for already-LZ-compressed data.
- Tune zlib wbits and memLevel to max values for the DEFLATE path.
- Write archive entries with compresslevel per-file, choosing the level that
  minimizes each entry rather than using a global level.
- Detect already-compressed files by heuristic (entropy estimate on first N
  KB) rather than by extension, for files with misleading names.
"""

SYSTEM_PROMPT = """\
You are an autonomous research agent optimizing a .zip compression function.

You will be shown the current compress.py, a research log (findings.md) of
past experiments, the current best archive size, and a menu of candidate
ideas. Your job, each turn, is to propose exactly ONE change to compress.py,
explain why you think it will help, and return the full rewritten file.

Strict rules:
1. Output valid JSON only, matching this schema exactly:
   {
     "hypothesis": "one short sentence stating the change and why",
     "why_should_help": "one or two sentences of concrete reasoning",
     "new_compress_py": "the complete new contents of compress.py"
   }
   No prose outside the JSON. No markdown code fences. Just the JSON object.

2. The new compress.py must:
   - define compress(input_dir: str, output_zip_path: str) -> None
   - use only the Python standard library
   - produce a .zip readable by the system `unzip` utility
   - round-trip every input file byte-for-byte on extraction

3. Make ONE change per turn. Do not stack multiple ideas. You will have many
   turns; be patient.

4. Do not repeat hypotheses already in findings.md. Read the log and pick
   something genuinely different. If you're running out of ideas, combine
   two previously-separate positives into one refined version, or try a
   hypothesis from the menu that hasn't been tried.

5. The harness validates strictly. If your code breaks the archive or fails
   round-trip, the experiment is a Negative — which is fine, it's data. But
   don't do it carelessly.
"""


# ----------------------------- small utilities ------------------------------

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def tail(text: str, n_chars: int) -> str:
    if len(text) <= n_chars:
        return text
    return "... [truncated earlier entries] ...\n" + text[-n_chars:]


def next_experiment_number() -> int:
    """Scan findings.md for the highest NNNN experiment number and return +1."""
    if not FINDINGS.exists():
        return 1
    nums = re.findall(r"^### (\d{4})\b", read(FINDINGS), flags=re.MULTILINE)
    if not nums:
        return 1
    return max(int(n) for n in nums) + 1


def next_win_number() -> int:
    """Scan confirmed_wins/ for the highest NNNN and return +1."""
    existing = sorted(WINS_DIR.glob("[0-9]*.patch"))
    if not existing:
        return 1
    nums = []
    for p in existing:
        m = re.match(r"(\d{4})_", p.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def sanitize_filename(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s).strip("_").lower()
    return s[:60] or "experiment"


def current_best_size() -> int | None:
    """Parse BEST.md for the current best. Returns None if not yet established."""
    if not BEST_MD.exists():
        return None
    m = re.search(r"Best:\s*([\d_,]+)", read(BEST_MD))
    if not m:
        return None
    try:
        return int(m.group(1).replace("_", "").replace(",", ""))
    except ValueError:
        return None


# --------------------------- harness interaction ----------------------------

def run_harness() -> tuple[int, bool, str]:
    """Run run_experiment.py and parse its output.

    Returns (total_bytes, valid, reason). total_bytes is -1 on crash.
    """
    try:
        with open(RUN_LOG, "w") as log:
            proc = subprocess.run(
                [sys.executable, str(HARNESS)],
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=str(ROOT),
                timeout=600,
            )
    except subprocess.TimeoutExpired:
        return -1, False, "harness timed out"

    text = RUN_LOG.read_text(encoding="utf-8", errors="replace")
    size_m = re.search(r"^total_compressed_bytes:\s*(-?\d+)", text, flags=re.MULTILINE)
    valid_m = re.search(r"^valid:\s*(true|false)", text, flags=re.MULTILINE)

    if not size_m or not valid_m:
        # Crash — harness didn't print its sentinel lines.
        tail_lines = "\n".join(text.splitlines()[-20:])
        return -1, False, f"harness crashed; tail:\n{tail_lines}"

    size = int(size_m.group(1))
    valid = valid_m.group(1) == "true"
    reason_m = re.search(r"^reason:\s*(.+)", text, flags=re.MULTILINE)
    reason = reason_m.group(1) if reason_m else ""
    return size, valid, reason


# ----------------------- reset + re-apply wins cycle ------------------------

def reset_to_baseline_plus_wins() -> None:
    """Copy baseline/compress.py over compress.py, then apply every patch in
    confirmed_wins/ in numeric order."""
    shutil.copy2(BASELINE_PY, COMPRESS_PY)
    patches = sorted(WINS_DIR.glob("[0-9]*.patch"))
    for patch_path in patches:
        apply_patch(patch_path)


def apply_patch(patch_path: Path) -> None:
    """Apply a unified diff to compress.py. Prefer system `patch`; fall back
    to pure Python for portability."""
    # Try system patch first.
    if shutil.which("patch") is not None:
        result = subprocess.run(
            ["patch", "-p0", "-s", "-i", str(patch_path), str(COMPRESS_PY)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return
    # Fallback: our patches are whole-file replacements wrapped as diffs.
    # The simplest recovery is to extract the "+" lines, since we know how we
    # generate them (see save_win_as_patch below — we save whole-file replace).
    _pure_python_apply(patch_path)


def _pure_python_apply(patch_path: Path) -> None:
    """Very simple unified-diff applier sufficient for whole-file replacements."""
    lines = patch_path.read_text(encoding="utf-8").splitlines(keepends=True)
    # Find the first hunk header.
    i = 0
    while i < len(lines) and not lines[i].startswith("@@"):
        i += 1
    if i == len(lines):
        raise RuntimeError(f"no hunk in patch {patch_path}")
    # Collect '+' and ' ' lines (context), which together form the new file.
    new_lines = []
    for line in lines[i + 1:]:
        if line.startswith("+") and not line.startswith("+++"):
            new_lines.append(line[1:])
        elif line.startswith(" "):
            new_lines.append(line[1:])
        elif line.startswith("-"):
            continue
        elif line.startswith("@@"):
            continue
    COMPRESS_PY.write_text("".join(new_lines), encoding="utf-8")


def save_win_as_patch(win_number: int, short_name: str) -> Path:
    """Save the current compress.py as a unified diff against baseline."""
    patch_path = WINS_DIR / f"{win_number:04d}_{sanitize_filename(short_name)}.patch"
    # Use system diff if available for a proper unified format. It's fine if
    # the return code is 1 (= files differ).
    if shutil.which("diff") is not None:
        result = subprocess.run(
            ["diff", "-u", str(BASELINE_PY), str(COMPRESS_PY)],
            capture_output=True,
            text=True,
        )
        patch_path.write_text(result.stdout, encoding="utf-8")
    else:
        # Fallback: fabricate a whole-file-replacement diff.
        baseline_lines = BASELINE_PY.read_text().splitlines(keepends=True)
        new_lines = COMPRESS_PY.read_text().splitlines(keepends=True)
        hunk = ["--- baseline/compress.py\n", "+++ compress.py\n",
                f"@@ -1,{len(baseline_lines)} +1,{len(new_lines)} @@\n"]
        hunk += ["-" + ln for ln in baseline_lines]
        hunk += ["+" + ln for ln in new_lines]
        patch_path.write_text("".join(hunk), encoding="utf-8")
    return patch_path


# ------------------------------- logging ------------------------------------

def append_finding(
    experiment_num: int,
    is_positive: bool,
    hypothesis: str,
    reasoning: str,
    prev_best: int | None,
    size: int,
    valid: bool,
    reason: str,
    patch_filename: str | None,
) -> None:
    header = "Positive" if is_positive else "Negative"
    size_str = f"{size:_}" if size >= 0 else "crashed"
    delta = ""
    if prev_best is not None and size >= 0:
        diff = size - prev_best
        pct = (diff / prev_best) * 100
        sign = "+" if diff >= 0 else ""
        delta = f" ({sign}{diff:_}, {sign}{pct:.3f}%)"

    block = [
        f"### {experiment_num:04d} — {hypothesis[:80]}",
        f"- Class: {header}",
        f"- Hypothesis: {hypothesis}",
        f"- Why (predicted): {reasoning}",
        f"- Result: total_compressed_bytes = {size_str}{delta}, valid = {valid}",
    ]
    if reason:
        block.append(f"- Harness note: {reason}")
    if patch_filename:
        block.append(f"- Patch: confirmed_wins/{patch_filename}")
    block.append("")  # trailing newline

    with open(FINDINGS, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(block) + "\n")


def update_best(experiment_num: int, size: int, wins_count: int) -> None:
    BEST_MD.write_text(
        "# BEST.md\n\n"
        "Current best `total_compressed_bytes`. Updated by the agent after every\n"
        "confirmed positive.\n\n"
        f"- Best: {size:_}\n"
        f"- At experiment: {experiment_num:04d}\n"
        f"- Confirmed wins stacked: {wins_count}\n",
        encoding="utf-8",
    )


# ------------------------------ model call ----------------------------------

def call_model(user_prompt: str) -> dict:
    """Call Ollama's chat endpoint with strict JSON output."""
    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",  # Ollama enforces JSON output when this is set.
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    content = data["message"]["content"]
    # Ollama with format=json returns a string that is valid JSON.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Some models leak markdown fences despite format=json; strip them.
        stripped = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE)
        return json.loads(stripped)


def build_user_prompt(prev_best: int | None) -> str:
    program = read(PROGRAM_MD)
    current = read(COMPRESS_PY)
    findings = read(FINDINGS) if FINDINGS.exists() else "(empty)"
    findings_trimmed = tail(findings, FINDINGS_TAIL_CHARS)
    best_str = f"{prev_best:_}" if prev_best is not None else "(not yet established)"

    return f"""\
## program.md (the rules)

{program}

## Current best archive size

{best_str} bytes.

## Current compress.py (baseline + all confirmed wins already applied)

```python
{current}
```

## Recent findings.md (most recent entries)

{findings_trimmed}

## Candidate idea menu (pick one not yet tried, or invent your own)

{IDEA_MENU}

## Your task this turn

Propose exactly ONE change. Return JSON as specified in the system prompt.
"""


# --------------------------------- main loop --------------------------------

def run_loop() -> None:
    ensure_setup()

    prev_best = current_best_size()
    if prev_best is None:
        print("[setup] Running baseline to establish starting size...")
        size, valid, reason = run_harness()
        if not valid or size < 0:
            print(f"[fatal] Baseline failed: {reason}", file=sys.stderr)
            sys.exit(1)
        update_best(0, size, 0)
        # Seed findings.md with the baseline entry if not already there.
        if "0000" not in (read(FINDINGS) if FINDINGS.exists() else ""):
            append_finding(
                experiment_num=0,
                is_positive=False,
                hypothesis="baseline",
                reasoning="starting point",
                prev_best=None,
                size=size,
                valid=True,
                reason="",
                patch_filename=None,
            )
        prev_best = size
        print(f"[setup] Baseline = {size:_} bytes.")

    consecutive_crashes = 0

    while True:
        exp_num = next_experiment_number()
        print(f"\n=== Experiment {exp_num:04d} (best = {prev_best:_} bytes) ===")

        # --- ask the model ---
        prompt = build_user_prompt(prev_best)
        try:
            result = call_model(prompt)
        except Exception as e:
            print(f"[error] model call failed: {e}", file=sys.stderr)
            time.sleep(5)
            continue

        hypothesis = str(result.get("hypothesis", "")).strip()
        reasoning = str(result.get("why_should_help", "")).strip()
        new_code = result.get("new_compress_py", "")

        if not hypothesis or not new_code or "def compress" not in new_code:
            print(f"[skip] model returned malformed response: keys={list(result)}")
            append_finding(
                exp_num, False,
                hypothesis or "(malformed model response)",
                reasoning or "(none)",
                prev_best, -1, False,
                "model output missing required fields",
                None,
            )
            reset_to_baseline_plus_wins()
            continue

        print(f"[hypothesis] {hypothesis}")

        # --- apply ---
        write(COMPRESS_PY, new_code)

        # --- run harness ---
        size, valid, reason = run_harness()
        if size < 0:
            consecutive_crashes += 1
            print(f"[negative] crash: {reason.splitlines()[0] if reason else 'unknown'}")
        else:
            consecutive_crashes = 0
            print(f"[result] size={size:_} valid={valid} "
                  f"(delta={size - prev_best:+_})")

        # --- classify ---
        is_positive = valid and size >= 0 and size < prev_best
        patch_filename = None

        if is_positive:
            win_num = next_win_number()
            patch_path = save_win_as_patch(win_num, hypothesis)
            patch_filename = patch_path.name
            update_best(exp_num, size, win_num)
            prev_best = size
            print(f"[POSITIVE] -> saved {patch_filename}; new best = {size:_}")

        append_finding(
            exp_num, is_positive, hypothesis, reasoning,
            None if exp_num == 0 else (prev_best if is_positive else prev_best),
            size, valid, reason, patch_filename,
        )

        # --- reset + re-apply ---
        reset_to_baseline_plus_wins()

        # Sanity re-verify: the rebuilt compress.py should still hit prev_best.
        if is_positive:
            check_size, check_valid, _ = run_harness()
            if not check_valid or check_size != prev_best:
                print(f"[warning] reset mismatch: expected {prev_best:_}, "
                      f"got {check_size:_} (valid={check_valid}). "
                      f"Removing latest patch.", file=sys.stderr)
                patch_path.unlink(missing_ok=True)
                reset_to_baseline_plus_wins()
                # Revert prev_best to what it was before this "win".
                prev_best = current_best_size() or prev_best

        if consecutive_crashes >= MAX_CONSECUTIVE_CRASHES:
            print(f"[fatal] {consecutive_crashes} consecutive crashes; "
                  f"stopping. Check the model and findings.md.", file=sys.stderr)
            sys.exit(2)


def ensure_setup() -> None:
    for p in [COMPRESS_PY, BASELINE_PY, HARNESS, PROGRAM_MD]:
        if not p.exists():
            print(f"[fatal] missing required file: {p}", file=sys.stderr)
            sys.exit(1)
    if not any(ROOT.joinpath("corpus").iterdir()):
        print("[fatal] corpus/ is empty. Drop files into corpus/ first.",
              file=sys.stderr)
        sys.exit(1)
    WINS_DIR.mkdir(exist_ok=True)
    if not FINDINGS.exists():
        FINDINGS.write_text("# findings.md\n\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\n[stopped] interrupted by user. State is on disk; resume by "
              "re-running agent.py.", file=sys.stderr)
