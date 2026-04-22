# autozip — Karpathy-style autoresearch loop for .zip compression (Can be converted to Any Project!)

A single-machine, single-metric autonomous research loop adapted from
[karpathy/autoresearch](https://github.com/karpathy/autoresearch). Instead of
training a language model and minimizing `val_bpb`, an AI agent edits a single
file (`compress.py`) trying to minimize the total compressed size of the files
in `./corpus/`, subject to one hard constraint: the output must remain a valid
`.zip` readable by a standard `unzip` tool.

## The loop (what the agent does)

Starting from a clean baseline (stock `zipfile.ZIP_DEFLATED`, default level), the
agent repeats forever:

1. Read the current `compress.py` (baseline + all previously-confirmed wins
   already re-applied — see step 5).
2. Form a hypothesis about a change that might shrink the archive further.
3. Apply the change, then run `python run_experiment.py`, which:
   - compresses `./corpus/` into `output.zip`,
   - validates it with the system `unzip -t` and a byte-for-byte round-trip check,
   - prints the total compressed size.
4. Append the outcome to `findings.md` under **Positives** (smaller AND valid)
   or **Negatives** (bigger, equal, or broken), with a short note on *why* the
   agent thinks it did or didn't work.
5. **Revert `compress.py` to `baseline/compress.py`**, then re-apply every patch
   in `confirmed_wins/` in numeric order. If this experiment was a positive, its
   diff was already saved as the next `confirmed_wins/NNNN_*.patch` before the
   reset.
6. Go back to step 1.

This is the "reset each run, re-apply confirmed wins" variant. The code grows,
but only through reviewed positives. Every negative is fully discarded from the
code — but its reasoning is preserved forever in `findings.md`.

## The metric

`total_compressed_bytes` of `output.zip`. Lower is better. Ties do not advance.
If `unzip -t` fails or round-trip differs from the original, the run is a
Negative regardless of size.

## Files

- `corpus/` — **you drop files here.** The agent does not modify this directory.
- `compress.py` — **the file the agent edits.** Defines one function:
  `compress(input_dir: str, output_zip_path: str) -> None`.
- `run_experiment.py` — fixed harness. Do not modify.
- `baseline/compress.py` — the pristine baseline. Used for resets. Do not modify.
- `confirmed_wins/` — numbered `.patch` files, one per confirmed positive, applied
  in order on top of baseline before each new experiment.
- `program.md` — instructions the agent reads. Edited by the human.
- `findings.md` — append-only log of every experiment. Edited by the agent.

## Quick start

```bash
# 1. Drop a mix of files into ./corpus/ (text, binaries, images, etc.)
cp ~/some-files/* ./corpus/

# 2. Sanity-check the baseline works
python run_experiment.py

# 3. Point your coding agent at program.md and let it go.
Example: export AUTOZIP_MODEL=devstral-small-2:24b
# 4.
python3 agent.py
```
