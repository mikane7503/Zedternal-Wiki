"""Regenerate the wiki's downloadable Korean localization file.

The site's "한국어 패치 파일 다운로드" button used to ship a zip of the local
UDK build output (Published/). We now ship the actual localization file
directly, unzipped, converted to UTF-16 LE with a BOM -- Killing Floor 2's
localization loader mis-renders non-Latin text (Korean) when the file is
plain UTF-8, which is what caused in-game text corruption.

Source of truth: ZedternalRBPerkpackage.KOR.ini at repo root, which we edit
directly (kept as UTF-8 for git-diff readability and Edit-tool reliability).
This script only converts encoding + drops the ".ini" suffix so the shipped
file's name matches exactly what Killing Floor 2 expects
(BrewedPC/Localization/KOR/ZedternalRBPerkpackage.KOR).

Run manually with `python data/sync_kor_download.py`, or let the pre-push
git hook (githooks/pre-push) run it automatically before every push.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_KOR = os.path.join(ROOT, "ZedternalRBPerkpackage.KOR.ini")
DOWNLOAD_KOR = os.path.join(ROOT, "docs", "downloads", "ZedternalRBPerkpackage.KOR")


def sync_kor_download():
    if not os.path.isfile(SOURCE_KOR):
        print(f"[sync_kor_download] {SOURCE_KOR} not found -- skipping.")
        return False

    with open(SOURCE_KOR, encoding="utf-8-sig") as f:
        text = f.read()

    os.makedirs(os.path.dirname(DOWNLOAD_KOR), exist_ok=True)
    with open(DOWNLOAD_KOR, "w", encoding="utf-16-le") as f:
        f.write("﻿" + text)

    print(f"[sync_kor_download] wrote {DOWNLOAD_KOR} (UTF-16 LE, BOM)")
    return True


if __name__ == "__main__":
    ok = sync_kor_download()
    sys.exit(0 if ok else 1)
