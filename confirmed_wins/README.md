# confirmed_wins/

One `.patch` file per confirmed positive experiment. Applied in numeric order
on top of `baseline/compress.py` before each new experiment.

Filename format: `NNNN_<short_name>.patch` (zero-padded, monotonic).

Generate with:
```
diff -u baseline/compress.py compress.py > confirmed_wins/NNNN_<name>.patch
```

Apply with:
```
patch -p0 compress.py < confirmed_wins/NNNN_<name>.patch
```
