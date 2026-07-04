"""Zip the locally-built Published/ folder (UDK compiler output) into
Published.zip and copy it into docs/downloads/, where the wiki's "한국어
패치 파일 다운로드" button (docs/app.js) points at it.

Published/ itself is a local build artifact (gitignored) -- only the zip
under docs/downloads/ is committed, since that's what GitHub Pages serves.
Run manually with `python data/sync_published_zip.py`, or let the
pre-push git hook (githooks/pre-push) run it automatically.
"""
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISHED_DIR = os.path.join(ROOT, "Published")
ROOT_ZIP = os.path.join(ROOT, "Published.zip")
DOWNLOAD_ZIP = os.path.join(ROOT, "docs", "downloads", "ZedternalRB_KOR_Patch.zip")


def zip_published():
    if not os.path.isdir(PUBLISHED_DIR):
        print(f"[sync_published_zip] {PUBLISHED_DIR} not found -- skipping.")
        return False

    for out_path in (ROOT_ZIP, DOWNLOAD_ZIP):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(PUBLISHED_DIR):
                for name in filenames:
                    full = os.path.join(dirpath, name)
                    arcname = os.path.join("Published", os.path.relpath(full, PUBLISHED_DIR))
                    zf.write(full, arcname)
        print(f"[sync_published_zip] wrote {out_path}")
    return True


if __name__ == "__main__":
    ok = zip_published()
    sys.exit(0 if ok else 1)
