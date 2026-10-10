# -*- coding: utf-8 -*-
"""Verify generated wiki perk/skill descriptions against shipped KOR text."""
import json
import os
import sys

import build


def fail(message):
    print(f"[WIKI_KOR_AUDIT] FAIL {message}")
    return False


def main():
    data_path = os.environ.get("ZEDTERNAL_WIKI_DATA", build.OUT_JSON)
    with open(data_path, encoding="utf-8-sig") as stream:
        data = json.load(stream)

    encoding = "utf-16" if build.INI_KOR.lower().endswith(".kor") else "utf-8-sig"
    kor = build.parse_kor_ini(build.INI_KOR, encoding=encoding)
    reborn = build.parse_kor_ini(build.INI_REBORN_KOR, encoding="utf-16")
    retired_skills, retired_perks = build.parse_retired_upgrade_paths(
        os.path.join(build.SOURCE_CLASS_DIR, "ZTRetiredSkillFilter.uc")
    )
    failures = []
    checked_perks = checked_skills = 0

    for perk in data.get("basePerks", []):
        section = build.ci_lookup(reborn, f"WMUpgrade_Perk_{perk['key']}") or {}
        expected = section.get("descriptions", [])
        actual = [entry.get("raw", "") for entry in perk.get("descriptions", [])]
        if expected != actual:
            failures.append(f"base perk text mismatch: {perk['key']}")
        checked_perks += 1
        for skill in perk.get("skills", []):
            if skill["key"].lower() in retired_skills:
                failures.append(f"retired skill is listed: {perk['key']}/{skill['key']}")
            localized = (
                build.ci_lookup(reborn, f"WMUpgrade_Skill_{skill['key']}")
                or build.ci_lookup(kor, f"DKUpgrade_Skill_{skill['key']}")
                or {}
            )
            standard = localized.get("StandardSkillUpgradeDescription") or localized.get("SkillUpgradeDescription1")
            deluxe = localized.get("DeluxeSkillUpgradeDescription") or localized.get("SkillUpgradeDescription2")
            if (skill.get("standardDescRaw") or None) != standard:
                failures.append(f"standard KOR mismatch: {perk['key']}/{skill['key']}")
            if (skill.get("deluxeDescRaw") or None) != deluxe:
                failures.append(f"deluxe KOR mismatch: {perk['key']}/{skill['key']}")
            if not standard and not deluxe and not skill.get("note"):
                failures.append(f"active skill lacks KOR prose and supplement: {perk['key']}/{skill['key']}")
            checked_skills += 1

    for perk in data.get("advancedPerks", []):
        section = build.ci_lookup(kor, f"DKUpgrade_Perk_{perk['key']}") or {}
        expected = section.get("descriptions", [])
        actual = [entry.get("raw", "") for entry in perk.get("descriptions", [])]
        if expected != actual:
            failures.append(f"advanced perk text mismatch: {perk['key']}")
        checked_perks += 1

        for skill in perk.get("skills", []):
            if skill["key"].lower() in retired_skills:
                failures.append(f"retired skill is listed: {perk['key']}/{skill['key']}")
            localized = build.ci_lookup(kor, f"DKUpgrade_Skill_{skill['key']}") or {}
            standard = localized.get("StandardSkillUpgradeDescription") or localized.get("SkillUpgradeDescription1")
            deluxe = localized.get("DeluxeSkillUpgradeDescription") or localized.get("SkillUpgradeDescription2")
            if (skill.get("standardDescRaw") or None) != standard:
                failures.append(f"standard KOR mismatch: {perk['key']}/{skill['key']}")
            if (skill.get("deluxeDescRaw") or None) != deluxe:
                failures.append(f"deluxe KOR mismatch: {perk['key']}/{skill['key']}")
            if not standard and not deluxe and not skill.get("note"):
                failures.append(f"active skill lacks KOR prose and supplement: {perk['key']}/{skill['key']}")
            checked_skills += 1

    if failures:
        for item in failures:
            print(f"[WIKI_KOR_AUDIT] FAIL {item}")
        print(f"[WIKI_KOR_AUDIT] failures={len(failures)} perks={checked_perks} skills={checked_skills}")
        return 1
    print(f"[WIKI_KOR_AUDIT] PASS perks={checked_perks} activeSkills={checked_skills} exactKOR=100% retired=excluded uncoveredText=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
