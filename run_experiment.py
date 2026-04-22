"""
run_experiment.py — fixed harness. Do NOT modify.

Runs one experiment: imports compress() from compress.py, runs it on ./corpus/,
validates the output, and prints a single line of machine-parseable results.

The agent parses these two lines from stdout:

    total_compressed_bytes: <int>
    valid: <true|false>

If valid == false, the run is a Negative regardless of size.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from pathlib import Path

CORPUS_DIR = Path(__file__).parent / "corpus"
OUTPUT_ZIP = Path(__file__).parent / "output.zip"


def file_hashes(root: Path) -> dict[str, str]:
    """Map relative-path -> sha256 for every file under root."""
    out = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            full = Path(dirpath) / name
            rel = str(full.relative_to(root)).replace("\\", "/")
            h = hashlib.sha256()
            with open(full, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            out[rel] = h.hexdigest()
    return out


def main() -> int:
    if not CORPUS_DIR.is_dir():
        print(f"ERROR: corpus directory not found: {CORPUS_DIR}", file=sys.stderr)
        print("total_compressed_bytes: -1")
        print("valid: false")
        return 1

    corpus_files = list(CORPUS_DIR.rglob("*"))
    corpus_files = [p for p in corpus_files if p.is_file()]
    if not corpus_files:
        print(f"ERROR: corpus directory is empty: {CORPUS_DIR}", file=sys.stderr)
        print("total_compressed_bytes: -1")
        print("valid: false")
        return 1

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    # --- 1. Run the agent's compress() ---
    try:
        # Fresh import so edits to compress.py are picked up each invocation.
        sys.path.insert(0, str(Path(__file__).parent))
        if "compress" in sys.modules:
            del sys.modules["compress"]
        import compress as compress_mod  # noqa: E402

        t0 = time.monotonic()
        compress_mod.compress(str(CORPUS_DIR), str(OUTPUT_ZIP))
        elapsed = time.monotonic() - t0
    except Exception:
        print("ERROR: compress() raised an exception:", file=sys.stderr)
        traceback.print_exc()
        print("total_compressed_bytes: -1")
        print("valid: false")
        return 1

    if not OUTPUT_ZIP.exists():
        print("ERROR: compress() did not produce output.zip", file=sys.stderr)
        print("total_compressed_bytes: -1")
        print("valid: false")
        return 1

    size = OUTPUT_ZIP.stat().st_size

    # --- 2. Validate with the system unzip (strict .zip constraint) ---
    try:
        result = subprocess.run(
            ["unzip", "-tq", str(OUTPUT_ZIP)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        unzip_ok = result.returncode == 0
    except FileNotFoundError:
        # If the system has no `unzip`, fall back to Python's zipfile.testzip().
        # The agent should note this in findings.md if it matters.
        try:
            with zipfile.ZipFile(OUTPUT_ZIP) as zf:
                unzip_ok = zf.testzip() is None
        except Exception:
            unzip_ok = False
    except subprocess.TimeoutExpired:
        unzip_ok = False

    if not unzip_ok:
        print(f"total_compressed_bytes: {size}")
        print("valid: false")
        print("reason: unzip -t failed", file=sys.stderr)
        return 0

    # --- 3. Round-trip check: extract and compare sha256s ---
    with tempfile.TemporaryDirectory() as tmp:
        try:
            with zipfile.ZipFile(OUTPUT_ZIP) as zf:
                zf.extractall(tmp)
        except Exception:
            print(f"total_compressed_bytes: {size}")
            print("valid: false")
            print("reason: extraction failed", file=sys.stderr)
            traceback.print_exc()
            return 0

        original = file_hashes(CORPUS_DIR)
        extracted = file_hashes(Path(tmp))

        if original != extracted:
            missing = set(original) - set(extracted)
            extra = set(extracted) - set(original)
            mismatched = {
                k for k in original.keys() & extracted.keys()
                if original[k] != extracted[k]
            }
            print(f"total_compressed_bytes: {size}")
            print("valid: false")
            print(
                f"reason: round-trip mismatch "
                f"(missing={len(missing)}, extra={len(extra)}, "
                f"mismatched={len(mismatched)})",
                file=sys.stderr,
            )
            return 0

    # --- 4. Success ---
    print(f"total_compressed_bytes: {size}")
    print("valid: true")
    print(f"elapsed_seconds: {elapsed:.3f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
