"""
compress.py — baseline .zip compression.

This file defines a single function, `compress(input_dir, output_zip_path)`,
which the agent is free to modify. The only contract is:

  - Input: a directory path containing arbitrary files.
  - Output: a file at output_zip_path that is a valid .zip readable by the
    system `unzip` utility, and whose contents round-trip byte-for-byte
    against the input when extracted.

The agent's goal is to make output_zip_path as small as possible.

This baseline uses stock zipfile.ZIP_DEFLATED at default compresslevel.
"""

import os
import zipfile


def compress(input_dir: str, output_zip_path: str) -> None:
    with zipfile.ZipFile(
        output_zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        for root, _dirs, files in os.walk(input_dir):
            for name in sorted(files):
                full_path = os.path.join(root, name)
                arcname = os.path.relpath(full_path, start=input_dir)
                zf.write(full_path, arcname=arcname)
