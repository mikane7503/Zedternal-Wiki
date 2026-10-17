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
    perk_summaries = build.ci_lookup(kor, "ZTUI_UPGMenu") or {}
    reborn = build.parse_kor_ini(build.INI_REBORN_KOR, encoding="utf-16")
    retired_skills, retired_perks = build.parse_retired_upgrade_paths(
        os.path.join(build.SOURCE_CLASS_DIR, "ZTRetiredSkillFilter.uc")
    )
    failures = []
    checked_perks = checked_skills = 0

    def verify_perk_summary(perk, kind):
        expected = build.perk_summary_for(perk["key"], perk_summaries)
        if not expected:
            return
        if perk.get("role") != expected or perk.get("summary") != expected:
            failures.append(f"{kind} perk summary mismatch: {perk['key']}")

    for perk in data.get("basePerks", []):
        verify_perk_summary(perk, "base")
        section = (
            build.ci_lookup(kor, f"ZTWrapper_Perk_{perk['key']}")
            or build.ci_lookup(kor, f"DKWrapper_Perk_{perk['key']}")
            or build.ci_lookup(kor, f"ZUTUpgrade_Perk_Base_{perk['key']}")
            or build.ci_lookup(reborn, f"WMUpgrade_Perk_{perk['key']}")
            or {}
        )
        expected = section.get("descriptions", [])
        actual = [entry.get("raw", "") for entry in perk.get("descriptions", [])]
        if expected != actual:
            failures.append(f"base perk text mismatch: {perk['key']}")
        expected_overview = [text for text in expected if not build.is_capstone_description(text)]
        actual_overview = [entry.get("raw", "") for entry in perk.get("overviewDescriptions", [])]
        if expected_overview != actual_overview:
            failures.append(f"base overview section is incomplete: {perk['key']}")
        if not (perk.get("role") or perk.get("summary")):
            failures.append(f"base description section is empty: {perk['key']}")
        if not (perk.get("passiveStats") or perk.get("passiveDescriptions")):
            failures.append(f"base passive section is empty: {perk['key']}")
        capstone_stats = [stat for stat in perk.get("fixedStats", []) if stat.get("capstoneLevel")]
        if not (perk.get("capstoneDescriptions") or capstone_stats or perk.get("noCapstoneNote")):
            failures.append(f"base capstone section is empty: {perk['key']}")
        checked_perks += 1
        for skill in perk.get("skills", []):
            if skill["key"].lower() in retired_skills:
                failures.append(f"retired skill is listed: {perk['key']}/{skill['key']}")
            localized = (
                build.ci_lookup(reborn, f"WMUpgrade_Skill_{skill['key']}")
                or build.ci_lookup(kor, f"ZTUpgrade_Skill_{skill['key']}")
                or build.ci_lookup(kor, f"DKUpgrade_Skill_{skill['key']}")
                or {}
            )
            standard = localized.get("StandardSkillUpgradeDescription") or localized.get("SkillUpgradeDescription1")
            deluxe = localized.get("DeluxeSkillUpgradeDescription") or localized.get("SkillUpgradeDescription2")
            if not skill.get("allowsDeluxe", True):
                deluxe = None
            if (skill.get("standardDescRaw") or None) != standard:
                failures.append(f"standard KOR mismatch: {perk['key']}/{skill['key']}")
            if (skill.get("deluxeDescRaw") or None) != deluxe:
                failures.append(f"deluxe KOR mismatch: {perk['key']}/{skill['key']}")
            if not standard and not deluxe and not skill.get("note"):
                failures.append(f"active skill lacks KOR prose and supplement: {perk['key']}/{skill['key']}")
            checked_skills += 1

    for perk in data.get("advancedPerks", []):
        verify_perk_summary(perk, "advanced")
        section = (
            build.ci_lookup(kor, f"ZTUpgrade_Perk_{perk['key']}")
            or build.ci_lookup(kor, f"DKUpgrade_Perk_{perk['key']}")
            or {}
        )
        expected = section.get("descriptions", [])
        actual = [entry.get("raw", "") for entry in perk.get("descriptions", [])]
        if expected != actual:
            failures.append(f"advanced perk text mismatch: {perk['key']}")
        expected_overview = [text for text in expected if not build.is_capstone_description(text)]
        actual_overview = [entry.get("raw", "") for entry in perk.get("overviewDescriptions", [])]
        if expected_overview != actual_overview:
            failures.append(f"overview section is incomplete: {perk['key']}")
        if not (perk.get("role") or perk.get("overviewDescriptions")):
            failures.append(f"description section is empty: {perk['key']}")
        if not (perk.get("passiveStats") or perk.get("passiveDescriptions")):
            failures.append(f"passive section is empty: {perk['key']}")
        capstone_stats = [stat for stat in perk.get("fixedStats", []) if stat.get("capstoneLevel")]
        if not (perk.get("capstoneDescriptions") or capstone_stats or perk.get("noCapstoneNote")):
            failures.append(f"capstone section is empty: {perk['key']}")
        checked_perks += 1

        for skill in perk.get("skills", []):
            if skill["key"].lower() in retired_skills:
                failures.append(f"retired skill is listed: {perk['key']}/{skill['key']}")
            perk_key, short = perk["key"], skill["key"]
            localized = build.ci_lookup(reborn, f"WMUpgrade_Skill_{short}") if perk_key == "Taskmaster" and short == "Tank" else None
            if localized is None:
                localized = next((
                    build.ci_lookup(kor, section_name)
                    for section_name in (
                        *((f"DKUpgrade_Skill_Overclock_Module_{short}",) if perk_key == "Override" else ()),
                        f"ZTUpgrade_Skill_{perk_key}_{short}", f"DKUpgrade_Skill_{perk_key}_{short}",
                        f"ZTUpgrade_Skill_{short}", f"DKUpgrade_Skill_{short}",
                    ) if build.ci_lookup(kor, section_name) is not None
                ), {})
            standard = localized.get("StandardSkillUpgradeDescription") or localized.get("SkillUpgradeDescription1")
            deluxe = localized.get("DeluxeSkillUpgradeDescription") or localized.get("SkillUpgradeDescription2")
            if not skill.get("allowsDeluxe", True):
                deluxe = None
            if (skill.get("standardDescRaw") or None) != standard:
                failures.append(f"standard KOR mismatch: {perk['key']}/{skill['key']}")
            if (skill.get("deluxeDescRaw") or None) != deluxe:
                failures.append(f"deluxe KOR mismatch: {perk['key']}/{skill['key']}")
            if not standard and not deluxe and not skill.get("note"):
                failures.append(f"active skill lacks KOR prose and supplement: {perk['key']}/{skill['key']}")
            checked_skills += 1

    by_key = {perk["key"]: perk for perk in data.get("advancedPerks", [])}
    override = by_key.get("Override")
    if not override:
        failures.append("active runtime perk missing: Override")
    else:
        if (override.get("parentPerk"), override.get("unlockLevel"), override.get("maxLevel")) != ("Demolitionist", 15, 10):
            failures.append("Override progression/max-level metadata mismatch")
        if override.get("skillCount") != 11 or any(not skill.get("standardDescRaw") for skill in override.get("skills", [])):
            failures.append("Override runtime module roster or KOR descriptions incomplete")
    gambit = by_key.get("Gambit")
    if not gambit or not gambit.get("summaryHtml") or not gambit.get("unlockRequirements"):
        failures.append("Capitalist Gambit summary/unlock data is null or incomplete")

    if failures:
        for item in failures:
            print(f"[WIKI_KOR_AUDIT] FAIL {item}")
        print(f"[WIKI_KOR_AUDIT] failures={len(failures)} perks={checked_perks} skills={checked_skills}")
        return 1
    print(f"[WIKI_KOR_AUDIT] PASS perks={checked_perks} activeSkills={checked_skills} exactKOR=100% retired=excluded uncoveredText=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
