# program.md

You are an autonomous research agent. Your job is to iteratively find ways to
shrink `output.zip` further, while never breaking the archive.

## The one file you may edit

`compress.py`. Nothing else. Do not touch `run_experiment.py`, `baseline/`,
`corpus/`, or this file.

## The hard constraint

`output.zip` must remain a valid `.zip` readable by the system `unzip` utility.
The harness checks this with `unzip -t` followed by a byte-for-byte round-trip
of every file's sha256. If either check fails, the experiment is a Negative no
matter how small the archive is.

> **Human:** to loosen this later (e.g. allow zstd, 7z, custom formats), edit
> the validation step in `run_experiment.py` and update this section. Start
> strict.

## The metric

`total_compressed_bytes` from the harness. Lower is better. Ties do not count
as wins.

## Setup (do this once, before the loop)

1. `git checkout -b autozip/<tag>` from current master.
2. Read in-scope files in full for context:
   - `README.md`
   - `run_experiment.py` — understand exactly what the harness measures and
     enforces. Do not modify.
   - `baseline/compress.py` — the pristine baseline.
   - `compress.py` — the current working version (baseline + confirmed wins).
   - `confirmed_wins/` — every patch already applied, in order.
3. Verify `./corpus/` is not empty. If it is, stop and tell the human to drop
   files into `./corpus/`.
4. Run the baseline once to record the starting size:
   `python run_experiment.py > run.log 2>&1`
   Read `total_compressed_bytes` from run.log. If `findings.md` does not exist,
   create it with a header and a "Baseline" entry recording this size.
5. Confirm setup with the human once. After that, do not stop.

## The experiment loop

Repeat forever:

1. **Hypothesize.** Pick one specific change you believe will reduce
   `total_compressed_bytes` without breaking validation. Examples of fair game:
   - Raising `compresslevel` (1-9 for DEFLATE).
   - Per-file method selection: skip re-compressing already-compressed files
     (`.jpg`, `.png`, `.zip`, `.gz`, `.mp4`, etc.) by using `ZIP_STORED` for
     them — DEFLATE on incompressible data can *grow* the output.
   - Sorting files by extension or by content similarity so DEFLATE's 32KB
     sliding window sees related bytes back-to-back.
   - Using `ZIP_BZIP2` or `ZIP_LZMA` (both in the zip spec, both readable by
     standard `unzip` on most systems — verify per experiment).
   - Preprocessing transforms that are reversible inside the archive (e.g.
     concatenation via solid-archive tricks are *not* standard .zip, so those
     are out under the strict constraint).
   - Tuning zlib directly via `zlib.compressobj` with custom `wbits`, `memLevel`,
     and `strategy` (e.g. `Z_FILTERED` for mostly-numeric data, `Z_HUFFMAN_ONLY`
     for already-LZ-compressed data).
   One change per experiment. Don't stack multiple ideas — you won't learn
   which one helped.

2. **Apply.** Edit `compress.py` directly. Keep the change minimal and readable.

3. **Run.** `python run_experiment.py > run.log 2>&1` (redirect everything; do
   NOT use tee or let output flood your context).

4. **Read results.** `grep "^total_compressed_bytes:\|^valid:" run.log`.
   If the grep output is empty or malformed, the run crashed. Run
   `tail -n 50 run.log` to read the traceback and attempt a fix. If you can't
   fix it after a few tries, revert the change and log it as a Negative with
   the crash reason.

5. **Classify and log.** Append to `findings.md`:
   - **Positive** if `valid: true` AND `total_compressed_bytes` is *strictly
     less than* the previous best.
   - **Negative** otherwise (bigger, equal, invalid, or crashed).

   Every entry must include:
   - Experiment number (monotonically increasing).
   - One-line hypothesis.
   - The change (a minimal diff or description).
   - The measured `total_compressed_bytes` and `valid` values.
   - A one- or two-sentence note on *why* you think it did or didn't work.
     This "why" is the most valuable part of the log — it's what makes the
     journal worth keeping across resets.

6. **Save the patch (positives only).** If the experiment was a Positive,
   save a diff against `baseline/compress.py` into
   `confirmed_wins/NNNN_<short_name>.patch`, where NNNN is zero-padded and one
   greater than the highest-numbered existing patch. Use:
   `diff -u baseline/compress.py compress.py > confirmed_wins/NNNN_<name>.patch`

7. **Reset.** Regardless of outcome:
   - `cp baseline/compress.py compress.py` — revert to pristine baseline.
   - For every file in `confirmed_wins/` in numeric order, apply it:
     `patch -p0 compress.py < confirmed_wins/NNNN_*.patch`
   - After the last patch, `compress.py` is now: baseline + all confirmed wins
     (including this experiment's, if it was a positive).
   - Run the harness one more time to verify the rebuilt `compress.py` still
     produces a valid archive at the expected size. If not, the latest patch
     conflicts with an earlier one — revert the newest patch, log the conflict
     as a Negative in `findings.md`, and continue.

8. **Loop.** Go to step 1. Pick a different hypothesis, ideally one informed by
   the `findings.md` history (what classes of changes have been working, what
   haven't, what hasn't been tried yet).

## NEVER STOP

Once the loop has begun, do not pause to ask the human if you should continue.
Do not ask "should I keep going?" or "is this a good stopping point?". The
human might be asleep or away. You are autonomous. If you run out of ideas,
think harder: re-read `findings.md` for untried combinations, read the DEFLATE
RFC 1951, read the ZIP APPNOTE.TXT, try combining ideas from previous
near-misses, try more radical approaches within the constraint. The loop runs
until the human interrupts you, period.

## One rule about the code

Keep `compress.py` a single self-contained file using only the Python standard
library. No third-party packages. This keeps the experiments reproducible and
keeps the arena honest. If you believe a third-party library would unlock a
large win, log that belief as a Negative with the note "blocked by
stdlib-only rule" and move on — do not install anything.
