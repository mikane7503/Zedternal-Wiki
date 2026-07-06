# -*- coding: utf-8 -*-
"""Auto-tag perks as "최근 버프됨" / "최근 너프됨" by diffing
KFZedternalUnlimited.ini's numeric fields against a previous git ref.

Run this as part of every balance-patch commit (after editing the ini,
before `git commit`): it compares the working copy against a baseline
commit, decides per perk whether the net change was a buff or a nerf
(more fields went up = buff, more went down = nerf; ties/no changes are
left untagged), and writes the result into data/recent_changes.json with
today's date. build.py reads that file into each perk's `recentChangeTag`.

Usage:
    python data/tools/tag_recent_changes.py [--since REF] [--dry-run]

REF defaults to HEAD (i.e. "what changed in the working copy since the
last commit"). Use an older ref to cover a multi-commit patch session.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "data"))
import build  # noqa: E402

RECENT_CHANGES_PATH = os.path.join(ROOT, "data", "recent_changes.json")


def git_show(ref, path):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    out = subprocess.run(
        ["git", "show", f"{ref}:{rel}"], cwd=ROOT, capture_output=True, check=True
    )
    return out.stdout.decode("utf-8-sig")


def parse_ini_text(text):
    with tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False, encoding="utf-8") as f:
        f.write(text)
        tmp_path = f.name
    try:
        return build.parse_ini_generic(tmp_path)
    finally:
        os.remove(tmp_path)


def owning_perk_for_section(section, skill_to_perk):
    if section.startswith("DKWrapper_Perk_"):
        return section[len("DKWrapper_Perk_"):]
    if section.startswith("DKUpgrade_Perk_"):
        return section[len("DKUpgrade_Perk_"):]
    if section.startswith("DKUpgrade_Skill_"):
        skill = section[len("DKUpgrade_Skill_"):]
        return skill_to_perk.get(skill)
    return None


def collect_signals(old_sections, new_sections, skill_to_perk):
    signals = {}  # perk_key -> [buff_count, nerf_count]
    for section, new_kv in new_sections.items():
        perk_key = owning_perk_for_section(section, skill_to_perk)
        if perk_key is None:
            continue
        old_kv = old_sections.get(section, [])
        old_by_key = {}
        for k, v in old_kv:
            old_by_key.setdefault(k, []).append(v)
        new_by_key = {}
        for k, v in new_kv:
            new_by_key.setdefault(k, []).append(v)
        for k, new_vals in new_by_key.items():
            if k == "MODEVERSION":
                continue
            old_vals = old_by_key.get(k, [])
            for old_v, new_v in zip(old_vals, new_vals):
                old_n, new_n = build.to_num(old_v), build.to_num(new_v)
                if not isinstance(old_n, (int, float)) or not isinstance(new_n, (int, float)):
                    continue
                if new_n == old_n:
                    continue
                bucket = signals.setdefault(perk_key, [0, 0])
                if new_n > old_n:
                    bucket[0] += 1
                else:
                    bucket[1] += 1
    return signals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="HEAD")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    old_text = git_show(args.since, build.INI_MAIN)
    old_sections = parse_ini_text(old_text)
    new_sections = build.parse_ini_generic(build.INI_MAIN)

    registry = build.parse_dk_skill_registry(build.INI_UPGRADES)
    skill_to_perk = {}
    for perk, skills in registry.items():
        for skill, _disabled, _note in skills:
            skill_to_perk[skill] = perk

    signals = collect_signals(old_sections, new_sections, skill_to_perk)

    today = datetime.date.today().isoformat()
    existing = {}
    if os.path.exists(RECENT_CHANGES_PATH):
        with open(RECENT_CHANGES_PATH, encoding="utf-8") as f:
            existing = json.load(f)

    changed = []
    for perk_key, (buffs, nerfs) in sorted(signals.items()):
        if buffs == nerfs:
            continue
        change_type = "buff" if buffs > nerfs else "nerf"
        existing[perk_key] = {"type": change_type, "date": today}
        changed.append((perk_key, change_type, buffs, nerfs))

    print(f"{len(changed)} perk(s) tagged from diff against '{args.since}':")
    for perk_key, change_type, buffs, nerfs in changed:
        print(f"  {perk_key}: {change_type} (+{buffs}/-{nerfs} fields)")

    if args.dry_run:
        print("(dry-run, not written)")
        return

    with open(RECENT_CHANGES_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {RECENT_CHANGES_PATH}")


if __name__ == "__main__":
    main()
