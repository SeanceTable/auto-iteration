Drop your mix of files directly into this directory (text, binaries, images,
already-compressed archives, whatever you want). Subdirectories are fine.

The agent will not modify anything in here. The harness enumerates
`corpus/**` on every run, so adding or removing files between runs is safe but
will change the size target — if you do that mid-loop, record it in
findings.md and treat it as a new baseline.
