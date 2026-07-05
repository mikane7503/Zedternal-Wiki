# -*- coding: utf-8 -*-
"""Compare the raw ZedternalRBPerkpackage.KOR.ini text against the final,
ini-reconciled text the wiki build already computes (docs/data/perks.json),
and report every mismatch.

Run this after any balance-ini change: build.py's reconciliation pipeline
(regex fixes + manual_skill_overrides.json / manual_perk_desc_overrides.json)
only ever corrects numbers in-memory for the website. It never writes
corrections back into KOR.ini, the file that actually ships to players --
so the two can silently drift apart. Run `python data/build.py` first to
refresh docs/data/perks.json, then this script.

Usage:
  python data/tools/kor_audit.py            # summary counts only
  python data/tools/kor_audit.py --details   # print every mismatch

Fix any mismatches by editing ZedternalRBPerkpackage.KOR.ini directly
(Edit tool, not this script -- it's read-only), then re-run to confirm 0.
"""
import json
import os
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(TOOLS_DIR)
ROOT = os.path.dirname(DATA_DIR)
sys.path.insert(0, DATA_DIR)
from build import parse_kor_ini, ci_lookup  # noqa: E402

KOR_PATH = os.path.join(ROOT, "ZedternalRBPerkpackage.KOR.ini")
PERKS_JSON = os.path.join(ROOT, "docs", "data", "perks.json")

kor_sections = parse_kor_ini(KOR_PATH)
data = json.load(open(PERKS_JSON, encoding="utf-8"))

mismatches = []          # (perk_key, kind, section, sub_key, current, target)
missing_sections = []    # (perk_key, skill_key)

for p in data["advancedPerks"]:
    perk_key = p["key"]
    perk_section = f"DKUpgrade_Perk_{perk_key}"
    pkor = kor_sections.get(perk_section, {})
    kor_descs = pkor.get("descriptions", [])
    for i, d in enumerate(p["descriptions"]):
        if i >= len(kor_descs):
            continue
        current = kor_descs[i]
        if "%x" in current:
            continue  # runtime-substituted by the game engine; leave alone
        target = d["raw"]
        if current != target:
            mismatches.append((perk_key, "perk_desc", perk_section, f"PerkUpgradeDescription{i+1}", current, target))

    for s in p["skills"]:
        skey = s["key"]
        section = f"DKUpgrade_Skill_{skey}"
        skor = ci_lookup(kor_sections, section)
        if s.get("noData"):
            continue
        if skor is None:
            missing_sections.append((perk_key, skey))
            continue
        # Recover the section's real (possibly differently-cased) key name
        real_section = section
        if section not in kor_sections:
            for k in kor_sections:
                if k.lower() == section.lower():
                    real_section = k
                    break
        current_std = skor.get("StandardSkillUpgradeDescription")
        current_dlx = skor.get("DeluxeSkillUpgradeDescription")
        target_std = s["standardDescRaw"]
        target_dlx = s["deluxeDescRaw"]
        if current_std is not None and current_std != target_std:
            mismatches.append((perk_key, "skill_std", real_section, "StandardSkillUpgradeDescription", current_std, target_std))
        if current_dlx is not None and current_dlx != target_dlx:
            mismatches.append((perk_key, "skill_dlx", real_section, "DeluxeSkillUpgradeDescription", current_dlx, target_dlx))

print(f"Total mismatches: {len(mismatches)}")
print(f"Missing KOR sections entirely: {len(missing_sections)}")
print()
by_kind = {}
for m in mismatches:
    by_kind[m[1]] = by_kind.get(m[1], 0) + 1
print("By kind:", by_kind)
print()
print("Missing sections:", missing_sections)
print()

if "--details" in sys.argv:
    for perk_key, kind, section, subkey, current, target in mismatches:
        print(f"[{perk_key}] {section}.{subkey}")
        print(f"  CUR: {current}")
        print(f"  TGT: {target}")
else:
    print("(pass --details to print every mismatch)")
