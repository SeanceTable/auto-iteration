# SETUP.md — running autozip fully offline on Windows + WSL2

Target: Windows host, Ubuntu in WSL2, NVIDIA GPU passed through, Ollama as the
inference backend, one of the recommended coding models running locally.

## 1. Prerequisites in WSL2

```bash
# Inside your WSL2 Ubuntu shell:
python3 --version          # need 3.10+
pip install requests        # only Python dep the agent needs
sudo apt-get install -y unzip patch   # harness uses `unzip -t`; agent uses `patch`
```

Verify GPU passthrough works in WSL:
```bash
nvidia-smi
```
You should see your GPU listed. If you see "command not found", install the
NVIDIA driver on Windows (not inside WSL — WSL inherits it) and make sure
you're on a recent Windows build.

## 2. Install Ollama in WSL

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The installer sets up a systemd service in recent distros. Start it:

```bash
# Either run in the foreground in its own terminal:
ollama serve

# Or, if systemd is active in your WSL distro:
sudo systemctl start ollama
```

Verify:
```bash
curl http://localhost:11434/api/tags    # should return JSON, empty on first install
```

## 3. Pull a model

Pick based on your VRAM. Q4_K_M quantization unless noted.

| VRAM available | Recommended model | Pull command |
| --- | --- | --- |
| 16 GB+ | Devstral Small 24B (best for agentic edit loops) | `ollama pull devstral-small:24b` |
| 10–12 GB | Qwen2.5-Coder 14B | `ollama pull qwen2.5-coder:14b` |
| 8 GB | Qwen2.5-Coder 7B | `ollama pull qwen2.5-coder:7b` |

Check the exact model tag on [ollama.com/library](https://ollama.com/library)
since names shift. If a newer Qwen3-Coder build is available in your size
class, use it — it's generally a straight upgrade.

Sanity-check the model responds:
```bash
ollama run devstral-small:24b "write a python function that returns 42"
```

## 4. Drop your files into corpus/

```bash
cd autozip
cp ~/some-test-files/* corpus/
ls corpus/
```

A good mix: a couple of text files (logs, source code, markdown), a couple of
binaries (exe, so, small database), an already-compressed file (.jpg, .gz,
.mp4) so the agent has something to learn about. Aim for roughly 10–100 MB
total — small enough that each experiment finishes in seconds.

## 5. Sanity-run the baseline

```bash
python3 run_experiment.py
```

You should see two lines:
```
total_compressed_bytes: 12345678
valid: true
```

If not, fix that before starting the agent — the harness is the ground truth.

## 6. Launch the agent

```bash
# Tell the agent which model to use:
export AUTOZIP_MODEL=devstral-small:24b
# (optional) point at a different Ollama host:
# export AUTOZIP_OLLAMA_URL=http://localhost:11434

python3 agent.py
```

You'll see something like:

```
[setup] Running baseline to establish starting size...
[setup] Baseline = 12_345_678 bytes.

=== Experiment 0001 (best = 12_345_678 bytes) ===
[hypothesis] Skip DEFLATE on already-compressed extensions; use ZIP_STORED.
[result] size=12_298_104 valid=true (delta=-47_574)
[POSITIVE] -> saved 0001_skip_deflate_on_already_compressed_extensions.patch;
            new best = 12_298_104

=== Experiment 0002 (best = 12_298_104 bytes) ===
...
```

Stop with Ctrl-C any time. All state is persisted on disk — re-running
`python3 agent.py` resumes from where it left off (reads `BEST.md`, appends
to `findings.md`, continues numbering from the highest existing experiment).

## 7. What to watch for

- **The model starts repeating itself.** This is the main failure mode with
  local models. Check `findings.md` — if the last ten experiments are all
  variations of "try compresslevel=9", bump `AUTOZIP_TEMPERATURE` up to 0.6
  or 0.7 to inject more variance, or edit `IDEA_MENU` in `agent.py` to add
  fresh hypotheses it hasn't tried. Raising temperature too high will cause
  JSON malformation — the sweet spot is usually 0.4–0.7.

- **JSON decode errors** are rare with `format: json` enforced but can
  happen on very long rewrites. The agent logs these as Negatives and
  continues; no action needed unless they dominate the log.

- **VRAM pressure.** If `ollama ps` shows the model swapping, throughput
  drops dramatically. Either drop to a smaller model or close other GPU
  workloads.

- **Harness timeouts.** Default is 10 minutes per experiment. If the model
  picks ZIP_LZMA on a huge corpus it can exceed that — shrink the corpus or
  raise the timeout in `agent.py` (search for `timeout=600`).

## 8. Stopping well

The loop runs forever by design (that's the Karpathy spirit). Good stopping
heuristics:

- After N hours, check `findings.md` — if the last ~20 experiments are all
  Negatives, you've probably hit the local maximum for this model + corpus.
- If the compression ratio has gone from, say, 60% to 40% and plateaued, the
  marginal gains aren't worth the wall clock.
- If the model is clearly stuck in a loop, Ctrl-C, prune `findings.md` to
  remove the loop, and restart with a higher temperature.

## 9. Upgrading to a smarter model later

Nothing about the harness or agent assumes Ollama specifically. The agent
speaks the Ollama chat API, but any OpenAI-compatible local server (LM Studio,
llama.cpp server, vLLM, etc.) works if you edit `call_model()` in `agent.py`
to match its request shape — usually a 5-line change. If you want to try a
frontier-hosted model for a few hundred experiments to see what you'd find
with more capable reasoning, swapping `call_model()` to point at the Anthropic
or OpenAI API is straightforward; but you specifically asked for fully offline,
so I've kept the default honest to that.
