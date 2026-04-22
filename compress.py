import os
import zipfile


def compress(input_dir: str, output_zip_path: str) -> None:
    with zipfile.ZipFile(
        output_zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for root, _dirs, files in os.walk(input_dir):
            for name in sorted(files):
                full_path = os.path.join(root, name)
                arcname = os.path.relpath(full_path, start=input_dir)
                zf.write(full_path, arcname=arcname)