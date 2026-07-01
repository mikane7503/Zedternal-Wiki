# -*- coding: utf-8 -*-
"""
Zedternal Unlimited perk data builder.

Parses the mod's raw INI files + Korean localization file into a single
site/data/perks.json used by the static website. Also merges in
hand-curated balance verdicts / base-perk commentary (manual_*.json)
that only exist as prose in the balance docs.

Run: python build.py
"""
import json
import re
import os

from labels import translate_key, classify_unit_group, format_value_as

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INI_MAIN = os.path.join(ROOT, "KFZedternalUnlimited.ini")
INI_KOR = os.path.join(ROOT, "ZedternalRBPerkpackage.KOR.ini")
SKILL_MAP_MD = os.path.join(ROOT, "커퍼_스킬_원본데이터.md")
MANUAL_BASE = os.path.join(ROOT, "data", "manual_base_perks.json")
MANUAL_VERDICTS = os.path.join(ROOT, "data", "manual_verdicts.json")
MANUAL_ROLES = os.path.join(ROOT, "data", "manual_role_descriptions.json")
OUT_JSON = os.path.join(ROOT, "site", "data", "perks.json")

SECTION_RE = re.compile(r"^\[(?:ZedternalRBPerkpackage\.)?(.+)\]$")


def parse_ini_generic(path):
    """section_name -> list[(key, value_str)] , preserving duplicate keys (T1/T2) and order."""
    sections = {}
    current = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(";") or line.startswith("//"):
                continue
            m = SECTION_RE.match(line)
            if m:
                current = m.group(1)
                sections[current] = []
                continue
            if current is None or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            # strip trailing inline comment on value
            val = val.split(";")[0].strip()
            sections[current].append((key, val))
    return sections


def parse_patch_notes(path):
    """section_name -> [comment_text, ...] for lines carrying a '; 구 ...' balance-patch changelog note.

    KFZedternalUnlimited.ini is the authoritative, currently-applied values file. Whenever a
    number was tuned from its original value, the editor left a '; 구 <old> -> <reason>' comment
    on that line (per the project's own editing convention). We surface these so the site can
    warn when the flavor text in KOR.ini (which still contains the pre-patch numbers) might be stale.
    """
    notes = {}
    current = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            m = SECTION_RE.match(line)
            if m:
                current = m.group(1)
                continue
            if current is None or ";" not in line:
                continue
            comment = line.split(";", 1)[1].strip()
            if "구 " in comment:
                notes.setdefault(current, []).append(comment)
    return notes


KOR_LINE_RE = re.compile(r'^(\w+)\s*=\s*"(.*)"\s*$')


def parse_kor_ini(path):
    """section_name -> dict of {UpgradeName, descriptions:[...], StandardSkillUpgradeDescription, DeluxeSkillUpgradeDescription}"""
    sections = {}
    current = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.rstrip("\n").strip()
            if not line or line.startswith("//"):
                continue
            m = SECTION_RE.match(line)
            if m:
                current = m.group(1)
                sections[current] = {"descriptions": []}
                continue
            if current is None:
                continue
            km = KOR_LINE_RE.match(line)
            if not km:
                continue
            key, val = km.group(1), km.group(2)
            val = val.replace('\\"', '"')
            if key == "UpgradeName":
                sections[current]["UpgradeName"] = val
            elif key.startswith("PerkUpgradeDescription"):
                sections[current]["descriptions"].append(val)
            else:
                sections[current][key] = val
    return sections


def strip_font(s):
    if not s:
        return s
    s = re.sub(r"<font[^>]*>", "", s)
    s = s.replace("</font>", "")
    return s


PERK_HEADER_RE = re.compile(r"^##\s+DKUpgrade_Perk_(\w+)")
BOLD_SKILL_RE = re.compile(r"\*\*DKUpgrade_Skill_(\w+)\*\*")


def parse_skill_grouping(path):
    """perk_key -> [skill_short_name, ...] extracted from the balance-notes markdown."""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()

    # Cut off the "orphan sections" tail, not relevant to grouping
    text = text.split("## 고아 섹션")[0]

    blocks = re.split(r"(?=^## DKUpgrade_Perk_)", text, flags=re.M)
    grouping = {}
    for block in blocks:
        hm = PERK_HEADER_RE.match(block)
        if not hm:
            continue
        perk_key = hm.group(1)
        names = []
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            bold = BOLD_SKILL_RE.findall(line)
            if bold:
                names.extend(bold)
                continue
            # compact inline formats, e.g. "- Name1: a=b | Name2: c=d"
            # or "- NameA, NameB, NameC — 전부 X=Y"
            body = line[1:].strip()
            if "—" in body:
                body = body.split("—")[0]
            segments = body.split("|") if "|" in body else body.split(",")
            for seg in segments:
                seg = seg.strip()
                if not seg:
                    continue
                # drop trailing (...) annotations
                seg = re.sub(r"\([^)]*\)", "", seg).strip()
                seg = seg.replace("**", "")
                # take part before ':' or '=' (whichever comes first) as the skill name
                split_pos = len(seg)
                for sep in (":", "="):
                    idx = seg.find(sep)
                    if idx != -1:
                        split_pos = min(split_pos, idx)
                name = seg[:split_pos].strip()
                # drop trailing warning glyphs/emoji and whitespace
                name = re.sub(r"[^A-Za-z0-9]+$", "", name.split()[0]) if name.split() else ""
                # sanity: skill short names are single CamelCase words
                if re.match(r"^[A-Za-z][A-Za-z0-9]*$", name):
                    names.append(name)
        # de-dup, preserve order
        seen = set()
        uniq = []
        for n in names:
            if n not in seen:
                seen.add(n)
                uniq.append(n)
        grouping[perk_key] = uniq
    return grouping


UNLOCK_RULE_RE = re.compile(
    r'PerkUnlockRules=\(PerkName="DKUpgrade_Perk_(\w+)",Req1Perk="WMUpgrade_Perk_(\w+)",Req1Level=(\d+)'
)


def parse_unlock_rules(main_sections):
    rules = {}
    rows = main_sections.get("DKConfig_PerkUnlockRules", [])
    # PerkUnlockRules is a repeated key; re-scan the raw file for full value since '=' inside value breaks generic split
    with open(INI_MAIN, encoding="utf-8-sig") as f:
        text = f.read()
    for m in UNLOCK_RULE_RE.finditer(text):
        adv, base, lvl = m.group(1), m.group(2), int(m.group(3))
        rules[adv] = {"parentPerk": base, "unlockLevel": lvl}
    return rules


def to_num(s):
    try:
        if re.match(r"^-?\d+$", s):
            return int(s)
        return float(s)
    except (TypeError, ValueError):
        return s


def build_stat_entries(kv_pairs, with_levels=False):
    """kv_pairs: list of (key, raw_value_str_or_num) preserving duplicates/order.

    Groups by key (so a skill's own T1/T2 pair is classified together, see
    labels.classify_unit_group), then emits one Korean-labeled, human
    formatted entry per original pair.
    """
    nums = [(k, to_num(v) if isinstance(v, str) else v) for k, v in kv_pairs]
    by_key = {}
    for k, v in nums:
        by_key.setdefault(k, []).append(v)

    unit_by_key = {}
    for k, vals in by_key.items():
        probe = list(vals)
        if with_levels:
            for v in vals:
                if isinstance(v, (int, float)):
                    probe.append(v * 10)
                    probe.append(v * 20)
        unit_by_key[k] = classify_unit_group(k, probe)

    entries = []
    for k, v in nums:
        unit = unit_by_key[k]
        entry = {
            "key": k,
            "label": translate_key(k),
            "value": v,
            "unit": unit,
            "display": format_value_as(v, unit),
        }
        if with_levels and isinstance(v, (int, float)):
            lv10 = round(v * 10, 4) if isinstance(v, float) else v * 10
            lv20 = round(v * 20, 4) if isinstance(v, float) else v * 20
            entry["lv10"] = lv10
            entry["lv20"] = lv20
            entry["lv10Display"] = format_value_as(lv10, unit)
            entry["lv20Display"] = format_value_as(lv20, unit)
        entries.append(entry)
    return entries


# Skills whose KOR text explicitly states a stat is SACRIFICED/reduced
# (e.g. Voodoo: "체력이 X% 감소하는 대신 피해량이 Y% 증가") or gives a literal
# negative number ("-6%"), but whose ini only stores an unsigned magnitude.
# Found via a full-text audit of every DKUpgrade_Skill_* description for
# "감소하지만/하는 대신" (cost-for-benefit framing) and literal "-N%" numbers.
SKILL_COST_STATS = {
    "BloodRush": ["Health"],
    "DealWithTheDevil": ["Healing"],
    "GlassCannon": ["Health"],
    "NoStringsOnMe": ["Health"],
    "OdeToGreed": ["Health"],
    "PainSplit": ["Health"],
    "PinpointAccuracy": ["Health"],
    "PowerTransfer": ["Health"],
    "SoulStealer": ["Health"],
    "Triskelion": ["Health"],
    "DoubleDown": ["BodyPenalty"],
    "LifeTap": ["RechargeReductionPerSiphon"],
}


def build_test_warning(verdict, is_patched, patch_note):
    """A short 'currently being tested/monitored' banner for perks whose
    balance status is notably in flux, phrased as a heads-up to players
    rather than a raw changelog line."""
    tag = (verdict or {}).get("tag", "")
    note = (verdict or {}).get("note", "")

    if "확정 OP" in tag:
        lead = "🚨 경고! 이 퍼크는 밸런스 문제가 확정된 상태이며, 근본적인 수정 전까지는 매우 강력하게 작동할 수 있습니다."
    elif "OP 소지" in tag:
        lead = "⚠️ 주의! 이 퍼크는 과도하게 강해질 우려가 있어 성능을 지속적으로 모니터링 중입니다."
    elif "고위험 설계" in tag:
        lead = "⚠️ 참고: 이 퍼크는 의도적인 고위험-고보상 설계이며, 극단적인 빌드 조합의 영향을 계속 확인 중입니다."
    elif "너프 완료" in tag:
        lead = "⚠️ 주의! 이 퍼크는 최근 과도한 강함(OP) 우려로 인해 일부 수치가 하향 조정되어 테스트 중입니다."
    elif "상향 완료" in tag:
        lead = "⚠️ 주의! 이 퍼크는 최근 약함(Trash) 우려로 인해 일부 수치가 상향 조정되어 테스트 중입니다."
    elif is_patched:
        lead = "⚠️ 주의! 이 퍼크는 최근 밸런스 조정이 적용되어 테스트 중입니다."
    else:
        return None

    # The full reasoning already lives in the "밸런스 판정" verdict box further
    # down the page -- keep this top banner to the short heads-up sentence
    # plus the raw patch note, so the two sections don't just repeat each other.
    parts = [lead]
    if patch_note:
        parts.append(f"(패치 노트: {patch_note})")
    return " ".join(parts)


PLACEHOLDER_RE = re.compile(r"([+-]?)%x%(%)?")


def determine_stat_signs(raw_descriptions, stat_count):
    """The raw ini only ever stores unsigned magnitudes (e.g. Voodoo's
    Health=0.1) -- the +/- direction lives solely in the KOR text template
    ("-%x%%" for a penalty vs "+%x%%" for a bonus). Without this, a stat
    that's actually a *penalty* (Voodoo trading health/armor for damage)
    renders as a positive bonus everywhere else on the site (slider table,
    Lv10/Lv20 columns) -- a materially misleading bug, not just a display
    nitpick. We walk the descriptions in the same order fill_percent_placeholders
    consumes them and record each placeholder's sign, indexed to match the
    passiveStats list built from the same (order-preserved) ini section.
    """
    signs = [1] * stat_count
    idx = 0
    for d in raw_descriptions:
        for m in PLACEHOLDER_RE.finditer(d):
            if idx >= stat_count:
                break
            signs[idx] = -1 if m.group(1) == "-" else 1
            idx += 1
    return signs


def _fmt_signed_pct(x):
    s = f"{abs(x):.2f}".rstrip("0").rstrip(".")
    return f"{'-' if x < 0 else '+'}{s}"


def fill_percent_placeholders(raw_descriptions, passive_stats):
    """Replace '%x%' in the perk's game-text descriptions with BOTH the
    per-level-up increase and the Lv20 (max/만렙) total, computed from the
    matching passiveStats entry -- e.g. "+%x%%" becomes
    "레벨업당 +3% · 만렙(Lv20) +60%". passive_stats values are already signed
    (see determine_stat_signs), so the displayed sign always matches the
    stat's real direction rather than assuming every placeholder is a bonus.

    We consume passiveStats in ini order, one per placeholder encountered in
    description order -- this mirrors how the mod's own authors wrote the
    two lists side by side (verified: works cleanly for every perk with 2-3
    leading %x% stats, e.g. Cinder's FireDamagePerLevel/BurningTargetDamagePerLevel).
    """
    stats_queue = list(passive_stats)
    filled = []
    for d in raw_descriptions:
        if "%x%" not in d:
            filled.append(d)
            continue

        # Some descriptions state their own hard cap in prose, e.g.
        # "...(최대 30%)" -- the game clamps the runtime value there even
        # though the raw per-level*20 arithmetic would exceed it (Bulwark:
        # 0.02/level * 20 = 40%, but the mod clamps display to 30%).
        cap_match = re.search(r"최대[^0-9]{0,20}?([\d.]+)%", strip_font(d))
        cap = float(cap_match.group(1)) if cap_match else None

        def _sub(match, _queue=stats_queue, _cap=cap):
            if not _queue:
                sign = match.group(1) or "+"
                return f"{sign}?(하드코딩·비공개)"
            stat = _queue.pop(0)
            per_level = stat["value"] * 100
            max_val = stat["value"] * 20 * 100
            if _cap is not None:
                max_val = max(-_cap, min(max_val, _cap)) if max_val < 0 else min(max_val, _cap)
            return f"레벨업당 {_fmt_signed_pct(per_level)}% · 만렙(Lv20) {_fmt_signed_pct(max_val)}%"

        filled.append(PLACEHOLDER_RE.sub(_sub, d))
    return filled


def build():
    main_sections = parse_ini_generic(INI_MAIN)
    kor_sections = parse_kor_ini(INI_KOR)
    grouping = parse_skill_grouping(SKILL_MAP_MD)
    unlock_rules = parse_unlock_rules(main_sections)
    patch_notes = parse_patch_notes(INI_MAIN)

    with open(MANUAL_BASE, encoding="utf-8") as f:
        manual_base = json.load(f)
    with open(MANUAL_VERDICTS, encoding="utf-8") as f:
        manual_verdicts = json.load(f)
    with open(MANUAL_ROLES, encoding="utf-8") as f:
        manual_roles = json.load(f)

    # ---- advanced perks (커퍼 / DK) ----
    adv_keys = sorted({k[len("DKUpgrade_Perk_"):] for k in kor_sections if k.startswith("DKUpgrade_Perk_")})

    advanced_perks = []
    for key in adv_keys:
        kor = kor_sections.get(f"DKUpgrade_Perk_{key}", {})
        ini_kv = main_sections.get(f"DKUpgrade_Perk_{key}", [])
        raw_descs = kor.get("descriptions", [])
        filtered_kv = [(k, v) for k, v in ini_kv if k != "MODEVERSION"]
        signs = determine_stat_signs(raw_descs, len(filtered_kv))
        signed_kv = [(k, to_num(v) * sign if isinstance(to_num(v), (int, float)) else to_num(v))
                     for (k, v), sign in zip(filtered_kv, signs)]
        passive_stats = build_stat_entries(signed_kv, with_levels=True)
        filled_descriptions = fill_percent_placeholders(raw_descs, passive_stats)
        descriptions = [
            {"raw": d, "text": strip_font(d), "isCapstone": bool(re.match(r"^<font[^>]*>레벨 \d+:", d)) or d.startswith("레벨")}
            for d in filled_descriptions
        ]
        perk_patch_note = "; ".join(patch_notes.get(f"DKUpgrade_Perk_{key}", []))

        skill_notes = manual_verdicts.get("skillNotes", {}).get(key, {})
        skills = []
        for short in grouping.get(key, []):
            skill_section = f"DKUpgrade_Skill_{short}"
            skor = kor_sections.get(skill_section, {})
            sini = main_sections.get(skill_section, [])
            cost_keys = set(SKILL_COST_STATS.get(short, []))
            signed_sini = [(k, to_num(v) * (-1 if k in cost_keys else 1) if isinstance(to_num(v), (int, float)) else to_num(v))
                           for k, v in sini if k != "MODEVERSION"]
            raw_values = build_stat_entries(signed_sini)
            skill_patch_note = "; ".join(patch_notes.get(skill_section, []))
            skills.append({
                "key": short,
                "name": skor.get("UpgradeName", short),
                "standardDesc": strip_font(skor.get("StandardSkillUpgradeDescription")),
                "deluxeDesc": strip_font(skor.get("DeluxeSkillUpgradeDescription")),
                "standardDescRaw": skor.get("StandardSkillUpgradeDescription"),
                "deluxeDescRaw": skor.get("DeluxeSkillUpgradeDescription"),
                "rawValues": raw_values,
                "hasKorText": bool(skor),
                "note": skill_notes.get(short),
                "isPatched": bool(skill_patch_note),
                "patchNote": skill_patch_note or None,
            })

        rule = unlock_rules.get(key, {})
        verdict = manual_verdicts.get("advancedPerks", {}).get(key)
        is_patched = bool(perk_patch_note)
        role_desc = manual_roles.get(key, {})

        advanced_perks.append({
            "key": key,
            "name": kor.get("UpgradeName", key),
            "parentPerk": rule.get("parentPerk"),
            "unlockLevel": rule.get("unlockLevel"),
            "hasIniConfig": bool(ini_kv),
            "passiveStats": passive_stats,
            "role": role_desc.get("role"),
            "endgame": role_desc.get("endgame"),
            "descriptions": descriptions,
            "skills": skills,
            "skillCount": len(skills),
            "verdict": verdict,
            "grade": (verdict or {}).get("grade"),
            "isPatched": is_patched,
            "patchNote": perk_patch_note or None,
            "testWarning": build_test_warning(verdict, is_patched, perk_patch_note),
            "icon": f"icons/{key.lower()}.png",
        })

    advanced_perks.sort(key=lambda p: ((p["parentPerk"] or "zzz"), p["unlockLevel"] or 99))

    # ---- base perks (오퍼 / WM) ----
    base_perks = []
    for bkey, bdata in manual_base.items():
        wrapper_kv = main_sections.get(f"DKWrapper_Perk_{bkey}", [])
        passive_stats = build_stat_entries([(k, v) for k, v in wrapper_kv if k != "MODEVERSION"], with_levels=True)
        unlocks = [
            {"level": p["unlockLevel"], "perk": p["key"], "name": p["name"]}
            for p in advanced_perks if p["parentPerk"] == bkey
        ]
        unlocks.sort(key=lambda u: u["level"] or 0)
        base_patch_note = "; ".join(patch_notes.get(f"DKWrapper_Perk_{bkey}", []))
        base_is_patched = bool(base_patch_note)
        base_perks.append({
            "key": bkey,
            "name": bdata["name"],
            "grade": bdata.get("grade"),
            "summary": bdata.get("summary"),
            "role": bdata.get("role"),
            "endgame": bdata.get("endgame"),
            "passiveStats": passive_stats,
            "strengths": bdata.get("strengths", []),
            "weaknesses": bdata.get("weaknesses", []),
            "unlocks": unlocks,
            "isPatched": base_is_patched,
            "patchNote": base_patch_note or None,
            "testWarning": build_test_warning(None, base_is_patched, base_patch_note),
            "icon": f"icons/{bkey.lower()}.png",
        })

    data = {
        "basePerks": base_perks,
        "advancedPerks": advanced_perks,
        "meta": {
            "advancedPerkCount": len(advanced_perks),
            "basePerkCount": len(base_perks),
            "totalSkills": sum(p["skillCount"] for p in advanced_perks),
        },
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print(f"base perks: {len(base_perks)}")
    print(f"advanced perks: {len(advanced_perks)}")
    print(f"total skills grouped: {data['meta']['totalSkills']}")
    for p in advanced_perks:
        print(f"  {p['key']:16s} parent={p['parentPerk'] or '-':12s} lvl={p['unlockLevel']} skills={p['skillCount']}")


if __name__ == "__main__":
    build()
