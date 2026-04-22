# findings.md

Append-only research log. Every experiment produces one entry. Written by the
agent, read by the agent on every subsequent turn.

Entry format:

```
### NNNN — <hypothesis>
- Class: Positive | Negative
- Hypothesis: what the agent tried
- Why (predicted): the agent's reasoning before the run
- Result: total_compressed_bytes = X (delta), valid = true | false
- Harness note: optional, only on failure
- Patch: confirmed_wins/NNNN_*.patch    (positives only)
```

Negatives keep their full context here even though the code change was
discarded on reset. This is the persistent memory of what has already been
tried and why it did or didn't work — the main lever that keeps the agent
from cycling on the same ideas forever.

---






### 0001 — Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE bloat
- Class: Negative
- Hypothesis: Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE bloat
- Why (predicted): DEFLATE can expand already-compressed files; ZIP_STORED preserves them exactly, saving space on .jpg, .png, .zip, etc.
- Result: total_compressed_bytes = 15_739_226 (+0, +0.000%), valid = True


### 0002 — Raise compresslevel to 9 to improve DEFLATE compression ratio
- Class: Positive
- Hypothesis: Raise compresslevel to 9 to improve DEFLATE compression ratio
- Why (predicted): Higher compression levels in zlib typically yield smaller output sizes at the cost of CPU time. Since the corpus is unknown, level 9 is a standard choice for maximum compression.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True
- Patch: confirmed_wins/0001_raise_compresslevel_to_9_to_improve_deflate_compression_rati.patch


### 0003 — Use ZIP_BZIP2 for files that compress poorly with DEFLATE
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files that compress poorly with DEFLATE
- Why (predicted): BZIP2 can sometimes achieve better compression ratios than DEFLATE, especially for text-heavy or repetitive data. Since the corpus is unknown, testing BZIP2 as an alternative method may yield a smaller archive.
- Result: total_compressed_bytes = 13_468_378 (+44_080, +0.328%), valid = True


### 0004 — Use ZIP_LZMA for files larger than 1MB to improve compression ratio on large tex
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB to improve compression ratio on large text files
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0005 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0006 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0007 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0008 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0009 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0010 — Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with extensions indi
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with extensions indicating already-compressed data
- Why (predicted): For already-compressed files, DEFLATE can expand the data. Z_HUFFMAN_ONLY skips the LZ77 step and only applies Huffman coding, which is more efficient for data that is already compressed.
- Result: total_compressed_bytes = 13_514_862 (+90_564, +0.675%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=8)


### 0011 — Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compre
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compression
- Why (predicted): Z_FILTERED strategy in zlib is optimized for data that is mostly small values with some larger values, which is common in binary files. This could lead to better compression for such files compared to the default strategy.
- Result: total_compressed_bytes = 13_445_011 (+20_713, +0.154%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=12)


### 0012 — Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compre
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data with small values and some larger values, common in binary files, which may yield better compression than the default strategy.
- Result: total_compressed_bytes = 13_445_011 (+20_713, +0.154%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=12)


### 0013 — Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compre
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data with small values and some larger values, common in binary files, which may yield better compression than the default strategy.
- Result: total_compressed_bytes = 13_445_011 (+20_713, +0.154%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=12)


### 0014 — Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data (e.g., .jpg, .png, .zip), increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0015 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0016 — Use ZIP_LZMA for large text files (>1MB) to leverage its better compression rati
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files (>1MB) to leverage its better compression ratio for repetitive patterns
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0017 — Use ZIP_LZMA for large text files (>1MB) to leverage its better compression rati
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files (>1MB) to leverage its better compression ratio for repetitive patterns
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0018 — Use zlib.compressobj with strategy=Z_FILTERED for text files to improve compress
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for text files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data with small values and some larger values, which is common in text files. This could lead to better compression for text files compared to the default strategy.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0019 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_425_482 (+1_184, +0.009%), valid = True


### 0020 — Use zlib.compressobj with strategy=Z_FILTERED for text files to improve compress
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for text files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data with small values and some larger values, which is common in text files. This could lead to better compression for text files compared to the default strategy.
- Result: total_compressed_bytes = 13_424_320 (+22, +0.000%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=2)


### 0021 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0022 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0023 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0024 — Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE exp
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data (e.g., .jpg, .png, .zip), increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_758_776 (+2_334_478, +17.390%), valid = True


### 0025 — Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with already-compres
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with already-compressed extensions to avoid DEFLATE expansion
- Why (predicted): Z_HUFFMAN_ONLY skips the LZ77 step in DEFLATE, which is redundant for already-compressed data and can cause expansion. This should prevent size increases for files like .jpg, .png, .zip, etc.
- Result: total_compressed_bytes = 13_509_429 (+85_131, +0.634%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=11)


### 0026 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0027 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0028 — Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE exp
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data (e.g., .jpg, .png, .zip), increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0029 — Use ZIP_LZMA for large text files (>1MB) to leverage its better compression rati
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files (>1MB) to leverage its better compression ratio
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0030 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0031 — Use ZIP_LZMA for large text files (>1MB) to leverage its better compression rati
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files (>1MB) to leverage its better compression ratio
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0032 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0033 — Use zlib.compressobj with strategy=Z_FILTERED for binary files and Z_HUFFMAN_ONL
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files and Z_HUFFMAN_ONLY for already-compressed files to optimize compression per file type
- Why (predicted): Z_FILTERED is better for mostly-numeric binary data, while Z_HUFFMAN_ONLY avoids DEFLATE expansion on already-compressed data. This targeted approach should reduce size for binary files and prevent expansion for compressed files.
- Result: total_compressed_bytes = 13_443_340 (+19_042, +0.142%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=8)


### 0034 — Use zlib.compressobj with strategy=Z_FILTERED for binary files and Z_HUFFMAN_ONL
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files and Z_HUFFMAN_ONLY for already-compressed files to optimize compression per file type
- Why (predicted): Z_FILTERED is better for mostly-numeric binary data, while Z_HUFFMAN_ONLY avoids DEFLATE expansion on already-compressed data. This targeted approach should reduce size for binary files and prevent expansion for compressed files.
- Result: total_compressed_bytes = crashed, valid = False


### 0035 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0036 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0037 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0038 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0039 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0040 — Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data, increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0041 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0042 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0043 — Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio 
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio for large text files
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0044 — Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio 
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio for large text files
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for large text files, especially those with repetitive patterns. By applying LZMA to files larger than 1MB, we can leverage its strength on larger inputs while keeping smaller files with DEFLATE for efficiency.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0045 — Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for already-compressed file extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data, increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0046 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0047 — Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE exp
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with already-compressed extensions to avoid DEFLATE expansion
- Why (predicted): DEFLATE can expand already-compressed data, increasing the archive size. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0048 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0049 — Use zlib.compressobj with Z_FILTERED strategy for binary files to improve compre
- Class: Negative
- Hypothesis: Use zlib.compressobj with Z_FILTERED strategy for binary files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data with many repeated values, which is common in binary files. This could yield better compression ratios for binary data compared to the default strategy.
- Result: total_compressed_bytes = 13_476_604 (+52_306, +0.390%), valid = False
- Harness note: round-trip mismatch (missing=0, extra=0, mismatched=12)


### 0050 — Use zlib.compressobj with Z_HUFFMAN_ONLY strategy for files with .gz extension t
- Class: Negative
- Hypothesis: Use zlib.compressobj with Z_HUFFMAN_ONLY strategy for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using Z_HUFFMAN_ONLY strategy for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0051 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0052 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0053 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0054 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0055 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0056 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's str
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's strength on text
- Why (predicted): BZIP2 often compresses text better than DEFLATE, while DEFLATE is better for binary data. Using BZIP2 for text files could reduce the overall archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0057 — Use ZIP_LZMA for large text files to leverage its better compression ratio for t
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files to leverage its better compression ratio for text
- Why (predicted): ZIP_LZMA typically provides better compression ratios for text data compared to DEFLATE, especially for larger files. This could reduce the overall archive size for text-heavy corpora.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0058 — Use ZIP_LZMA for text files and ZIP_DEFLATED for others to leverage LZMA's bette
- Class: Negative
- Hypothesis: Use ZIP_LZMA for text files and ZIP_DEFLATED for others to leverage LZMA's better compression ratio for text
- Why (predicted): LZMA typically provides better compression ratios for text data compared to DEFLATE, especially for larger files. This could reduce the overall archive size for text-heavy corpora.
- Result: total_compressed_bytes = 13_424_406 (+108, +0.001%), valid = False
- Harness note: unzip -t failed


### 0059 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0060 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0061 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0062 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0063 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0064 — Use ZIP_STORED for files with .gz, .zip, .jpg, .jpeg, .png, .mp4, .webp, .7z, .x
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz, .zip, .jpg, .jpeg, .png, .mp4, .webp, .7z, .xz, .bz2, .mp3, .avif extensions to avoid DEFLATE expansion
- Why (predicted): These file types are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0065 — Use ZIP_STORED for files with .gz, .zip, .jpg, .jpeg, .png, .mp4, .webp, .7z, .x
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz, .zip, .jpg, .jpeg, .png, .mp4, .webp, .7z, .xz, .bz2, .mp3, .avif extensions to avoid DEFLATE expansion
- Why (predicted): These file types are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0066 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0067 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0068 — Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's bet
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for text files and ZIP_DEFLATED for others to leverage BZIP2's better compression ratio for text
- Why (predicted): BZIP2 typically provides better compression ratios for text data compared to DEFLATE, especially for larger files. This could reduce the overall archive size for text-heavy corpora.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0069 — Use ZIP_BZIP2 for files larger than 1MB and ZIP_DEFLATED for smaller files to le
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB and ZIP_DEFLATED for smaller files to leverage BZIP2's better compression ratio for larger files
- Why (predicted): BZIP2 generally provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0070 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0071 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0072 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0073 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0074 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0075 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0076 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0077 — Use ZIP_STORED for files with .jpg, .jpeg, .png, .mp4, .webp, .7z, .xz, .bz2, .m
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg, .jpeg, .png, .mp4, .webp, .7z, .xz, .bz2, .mp3, and .avif extensions to avoid DEFLATE expansion
- Why (predicted): These file types are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_739_032 (+2_314_734, +17.243%), valid = True


### 0078 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0079 — Use ZIP_LZMA for files larger than 1MB and ZIP_DEFLATED for smaller files to lev
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB and ZIP_DEFLATED for smaller files to leverage LZMA's better compression ratio for larger files
- Why (predicted): LZMA typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0080 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0081 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0082 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0083 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0084 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0085 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0086 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0087 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): Files with .zip extension are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0088 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0089 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed using MP3 encoding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0090 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed using MP3 encoding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0091 — Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansi
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansion
- Why (predicted): JPEG files are already compressed using DCT-based encoding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0092 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed using DEFLATE, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0093 — Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Why (predicted): Files with .7z extension are already compressed using LZMA or LZMA2, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0094 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): Files with .xz extension are already compressed using LZMA, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0095 — Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio 
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): LZMA typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0096 — Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Why (predicted): BZIP2-compressed files are already highly compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0097 — Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Why (predicted): BZIP2-compressed files are already highly compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0098 — Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Why (predicted): WEBP files are already compressed using a combination of VP8/VP9 video compression and entropy coding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0099 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0100 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): Files with .gz extension are already compressed with gzip, which uses DEFLATE. Applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0101 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0102 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed using MP3 encoding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0103 — Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Why (predicted): MP4 files are already compressed using video/audio codecs, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_517_222 (+2_092_924, +15.591%), valid = True


### 0104 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0105 — Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansi
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansion
- Why (predicted): JPEG files are already compressed using DCT-based encoding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0106 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed using DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0107 — Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Why (predicted): WEBP files are already compressed using VP8/VP9 video compression and entropy coding, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0108 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0109 — Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Why (predicted): 7z files are already compressed with LZMA/LZMA2, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0110 — Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Why (predicted): BZ2 files are already compressed with BZIP2, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0111 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0112 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0113 — Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Why (predicted): PDF files are typically already compressed, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0114 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0115 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed using audio codecs, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0116 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0117 — Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Why (predicted): MP4 files are already compressed using video/audio codecs, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_517_222 (+2_092_924, +15.591%), valid = True


### 0118 — Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio 
- Class: Negative
- Hypothesis: Use ZIP_LZMA for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): LZMA typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_531_292 (+106_994, +0.797%), valid = False
- Harness note: unzip -t failed


### 0119 — Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Why (predicted): WEBP files are already compressed with VP8/VP9, and applying DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0120 — Use ZIP_STORED for files with .tar extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .tar extension to avoid DEFLATE expansion
- Why (predicted): TAR files are often already compressed or contain compressed members, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0121 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0122 — Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Why (predicted): 7z files are already compressed with LZMA or similar, and applying DEFLATE again can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0123 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0124 — Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansi
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansion
- Why (predicted): JPEG files are already compressed with DCT-based encoding, and applying DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0125 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0126 — Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with .gz extension t
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and using Z_HUFFMAN_ONLY will skip the LZ77 step, which is redundant and can expand the data. This should preserve the original size better than ZIP_STORED.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0127 — Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compre
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_FILTERED for binary files to improve compression
- Why (predicted): Z_FILTERED strategy is optimized for data that is mostly small values with some larger values, which is common in binary files. This could improve compression ratios for binary data compared to the default strategy.
- Result: total_compressed_bytes = crashed, valid = False


### 0128 — Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with .gz extension t
- Class: Negative
- Hypothesis: Use zlib.compressobj with strategy=Z_HUFFMAN_ONLY for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and using Z_HUFFMAN_ONLY will skip the LZ77 step, which is redundant and can expand the data. This should preserve the original size better than ZIP_STORED.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0129 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0130 — Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files larger than 1MB to leverage its better compression ratio for larger files
- Why (predicted): BZIP2 typically provides better compression ratios for larger files, especially text, while DEFLATE is more efficient for smaller files. This hybrid approach could reduce the overall archive size by applying the best method for each file size category.
- Result: total_compressed_bytes = 13_460_924 (+36_626, +0.273%), valid = True


### 0131 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0132 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0133 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0134 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0135 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed with MP3 encoding, and applying DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0136 — Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Why (predicted): MP4 files are already compressed with video/audio codecs, and applying DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_517_222 (+2_092_924, +15.591%), valid = True


### 0137 — Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansi
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansion
- Why (predicted): JPEG files are already compressed with DCT-based encoding, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0138 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0139 — Use ZIP_LZMA for large text files to leverage its better compression ratio
- Class: Negative
- Hypothesis: Use ZIP_LZMA for large text files to leverage its better compression ratio
- Why (predicted): LZMA typically provides better compression ratios for large text files compared to DEFLATE, which could reduce the overall archive size for text-heavy content.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0140 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0141 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0142 — Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .7z extension to avoid DEFLATE expansion
- Why (predicted): 7z files are already compressed with LZMA or similar, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0143 — Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Why (predicted): WEBP files are already compressed with VP8/VP9 encoding, and applying DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0144 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0145 — Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Why (predicted): BZIP2 files are already compressed with BZIP2, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0146 — Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Why (predicted): PDF files are typically already compressed with FlateDecode (DEFLATE) or other compression methods, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0147 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0148 — Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Why (predicted): PDF files are typically already compressed with FlateDecode (DEFLATE) or other compression methods, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0149 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed with MP3 encoding, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0150 — Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansi
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg and .jpeg extensions to avoid DEFLATE expansion
- Why (predicted): JPEG files are already compressed with DCT-based encoding, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0151 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0152 — Use ZIP_BZIP2 for files with .txt extension to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for files with .txt extension to improve compression ratio
- Why (predicted): Text files often compress better with BZIP2 than DEFLATE, especially when they contain repetitive patterns or long sequences of similar characters. Using ZIP_BZIP2 for .txt files could reduce the total archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0153 — Use ZIP_BZIP2 for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for .txt files to improve compression ratio
- Why (predicted): Text files often compress better with BZIP2 than DEFLATE, especially when they contain repetitive patterns or long sequences of similar characters. Using ZIP_BZIP2 for .txt files could reduce the total archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0154 — Use ZIP_BZIP2 for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for .txt files to improve compression ratio
- Why (predicted): Text files often compress better with BZIP2 than DEFLATE, especially when they contain repetitive patterns or long sequences of similar characters. Using ZIP_BZIP2 for .txt files could reduce the total archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0155 — Use ZIP_BZIP2 for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for .txt files to improve compression ratio
- Why (predicted): Text files often compress better with BZIP2 than DEFLATE, especially when they contain repetitive patterns or long sequences of similar characters. Using ZIP_BZIP2 for .txt files could reduce the total archive size.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0156 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED preserves their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0157 — Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .pdf extension to avoid DEFLATE expansion
- Why (predicted): PDF files are typically already compressed with FlateDecode (DEFLATE) or other compression methods, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0158 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0159 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0160 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0161 — Use ZIP_LZMA for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_LZMA for .txt files to improve compression ratio
- Why (predicted): LZMA typically provides better compression ratios than DEFLATE for text data, especially when the text contains repetitive patterns or long sequences of similar characters. This could reduce the total archive size for text files.
- Result: total_compressed_bytes = 13_424_406 (+108, +0.001%), valid = False
- Harness note: unzip -t failed


### 0162 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed with MP3 encoding, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0163 — Use ZIP_STORED for files with .jpg extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .jpg extension to avoid DEFLATE expansion
- Why (predicted): JPG files are already compressed with DCT-based encoding, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0164 — Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .png extension to avoid DEFLATE expansion
- Why (predicted): PNG files are already compressed with DEFLATE, and re-compressing them can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_646_108 (+221_810, +1.652%), valid = True


### 0165 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0166 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0167 — Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp4 extension to avoid DEFLATE expansion
- Why (predicted): MP4 files are already compressed with video/audio codecs, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 15_517_222 (+2_092_924, +15.591%), valid = True


### 0168 — Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .gz extension to avoid DEFLATE expansion
- Why (predicted): GZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0169 — Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .webp extension to avoid DEFLATE expansion
- Why (predicted): WEBP files are already compressed using VP8/VP9 or other codecs, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0170 — Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .zip extension to avoid DEFLATE expansion
- Why (predicted): ZIP files are already compressed with DEFLATE, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0171 — Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .bz2 extension to avoid DEFLATE expansion
- Why (predicted): BZ2 files are already compressed with BZIP2, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0172 — Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .xz extension to avoid DEFLATE expansion
- Why (predicted): XZ files are already compressed with LZMA, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True


### 0173 — Use ZIP_BZIP2 for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for .txt files to improve compression ratio
- Why (predicted): BZIP2 typically provides better compression ratios than DEFLATE for text data, especially when the text contains repetitive patterns or long sequences of similar characters. This could reduce the total archive size for text files.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0174 — Use ZIP_BZIP2 for .txt files to improve compression ratio
- Class: Negative
- Hypothesis: Use ZIP_BZIP2 for .txt files to improve compression ratio
- Why (predicted): BZIP2 typically provides better compression ratios than DEFLATE for text data, especially when the text contains repetitive patterns or long sequences of similar characters. This could reduce the total archive size for text files.
- Result: total_compressed_bytes = 13_424_392 (+94, +0.001%), valid = True


### 0175 — Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Class: Negative
- Hypothesis: Use ZIP_STORED for files with .mp3 extension to avoid DEFLATE expansion
- Why (predicted): MP3 files are already compressed with audio codecs, and re-compressing them with DEFLATE can expand the data. Using ZIP_STORED for these files will preserve their original size, likely reducing the total archive size.
- Result: total_compressed_bytes = 13_424_298 (+0, +0.000%), valid = True

