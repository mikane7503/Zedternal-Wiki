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
INI_UPGRADES = os.path.join(ROOT, "KFZedternalReborn_Upgrades.ini")
MANUAL_BASE = os.path.join(ROOT, "data", "manual_base_perks.json")
MANUAL_VERDICTS = os.path.join(ROOT, "data", "manual_verdicts.json")
MANUAL_ROLES = os.path.join(ROOT, "data", "manual_role_descriptions.json")
OUT_JSON = os.path.join(ROOT, "docs", "data", "perks.json")

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


DK_SKILL_REGISTRY_RE = re.compile(
    r'([#;])?SkillUpgrade_Upgrade=\(PerkPath="ZedternalRBPerkpackage\.DKUpgrade_Perk_(\w+)",'
    r'SkillPath="ZedternalRBPerkpackage\.DKUpgrade_Skill_(\w+)"\)(?:\s*;\s*(.*))?'
)


def parse_dk_skill_registry(path):
    """[ZedternalReborn.Config_SkillUpgrade] is the game's own authoritative
    roster of which skills belong to which advanced (DK) perk -- including
    entries the mod authors have commented out (with '#' or ';') to disable
    a skill in-game while leaving its KOR text/ini config in place. Returns
    perk_key -> [(skill_short_name, is_disabled, disabled_note_or_None), ...]
    in file order.
    """
    registry = {}
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            m = DK_SKILL_REGISTRY_RE.match(raw.strip())
            if not m:
                continue
            disabled = bool(m.group(1))
            perk, skill, note = m.group(2), m.group(3), m.group(4)
            registry.setdefault(perk, []).append((skill, disabled, note))
    return registry


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


def split_tiers(raw_values):
    """Split a skill's build_stat_entries() output (one entry per ini
    occurrence, in file order) into a T1 view and a T2 view, one entry per
    distinct key. A key that only appears once (a fixed value that doesn't
    change between standard/deluxe) is reused for both tiers."""
    by_key = {}
    order = []
    for entry in raw_values:
        by_key.setdefault(entry["key"], []).append(entry)
        if entry["key"] not in order:
            order.append(entry["key"])
    t1, t2 = [], []
    for k in order:
        vals = by_key[k]
        t1.append(vals[0])
        t2.append(vals[1] if len(vals) > 1 else vals[0])
    return t1, t2


# Only these three units are reconciled directly in the flavor text: their
# in-text notation is unambiguous ("+50%", "6초", "500 도쉬"). "multiplier" is
# sometimes written as "%" and sometimes as "N배" inconsistently, and
# "distance"/"count" values aren't reliably distinguishable from unrelated
# numbers in prose -- those are left as-is (verified=False) rather than risk
# a wrong substitution.
RECONCILE_UNIT_PATTERNS = {
    "percent": re.compile(r"[+-]?\d+(?:\.\d+)?%"),
    "seconds": re.compile(r"\d+(?:\.\d+)?\s*초"),
    "currency": re.compile(r"[\d,]+(?:\.\d+)?\s*도쉬"),
}


def reconcile_skill_text(raw_text, tier_entries):
    """Rewrite hardcoded numbers embedded in a skill's KOR-ini flavor text so
    they match the currently-applied value in KFZedternalUnlimited.ini,
    which is the authoritative source -- the KOR ini text is just the
    original (possibly stale) game copy. Matches tokens to ini values
    positionally, per unit type, in the order they appear; if the count of
    tokens found doesn't exactly match the count of same-unit ini values,
    the text is left untouched and reported as unverified rather than
    guessed at.
    """
    if not raw_text:
        return raw_text, True, False

    queues = {unit: [e["display"] for e in tier_entries if e["unit"] == unit] for unit in RECONCILE_UNIT_PATTERNS}

    # Atomic: only rewrite if every unit's token count in the text exactly
    # matches its ini value count for this tier. A partial rewrite (some
    # numbers fixed, some left stale) would be more misleading than leaving
    # the whole string untouched.
    for unit, pattern in RECONCILE_UNIT_PATTERNS.items():
        if len(pattern.findall(raw_text)) != len(queues[unit]):
            return raw_text, False, False

    new_text = raw_text
    for unit, pattern in RECONCILE_UNIT_PATTERNS.items():
        q = queues[unit]
        new_text = pattern.sub(lambda m, _q=q: _q.pop(0), new_text)

    return new_text, True, new_text != raw_text


def build_ini_only_text(tier_entries):
    """Fallback for when reconcile_skill_text() can't safely patch the
    original KOR flavor sentence in place (e.g. one sentence covers several
    ini keys, or the text phrases a value as "N배" while the ini treats it
    as a percent -- both real cases found in this data). Rather than leave
    stale/mismatched numbers on the page, drop the flavor prose entirely and
    show a plain line built only from KFZedternalUnlimited.ini, which is the
    single source of truth per project policy -- the KOR ini is flavor text
    only, never authoritative for numbers."""
    if not tier_entries:
        return None
    return " · ".join(f"{e['label']}: {e['display']}" for e in tier_entries)


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


def build_test_warning(verdict, is_patched):
    """A short 'currently being tested/monitored' banner for perks whose
    balance status is notably in flux, phrased as a heads-up to players.
    Kept to a single lead sentence -- no raw ini patch-note dump."""
    tag = (verdict or {}).get("tag", "")

    if "확정 OP" in tag:
        return "🚨 경고! 이 퍼크는 밸런스 문제가 확정된 상태이며, 근본적인 수정 전까지는 매우 강력하게 작동할 수 있습니다."
    if "OP 소지" in tag:
        return "⚠️ 주의! 이 퍼크는 과도하게 강해질 우려가 있어 성능을 지속적으로 모니터링 중입니다."
    if "고위험 설계" in tag:
        return "⚠️ 참고: 이 퍼크는 의도적인 고위험-고보상 설계이며, 극단적인 빌드 조합의 영향을 계속 확인 중입니다."
    if "너프 완료" in tag:
        return "⚠️ 주의! 이 퍼크는 최근 과도한 강함(OP) 우려로 인해 일부 수치가 하향 조정되어 테스트 중입니다."
    if "상향 완료" in tag:
        return "⚠️ 주의! 이 퍼크는 최근 약함(Trash) 우려로 인해 일부 수치가 상향 조정되어 테스트 중입니다."
    if is_patched:
        return "⚠️ 주의! 이 퍼크는 최근 밸런스 조정이 적용되어 테스트 중입니다."
    return None


PLACEHOLDER_RE = re.compile(r"([+-]?)%x%(%)?")
CAPSTONE_LINE_RE = re.compile(r"^(?:<font[^>]*>)?레벨\s*\d+:")


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

    A '%x%' inside a "레벨 N:" capstone line is a different animal though --
    it describes a fixed or per-stack bonus for that one-shot ability (e.g.
    Parasite's "흡수된 적 1명당 +%x%%"), not something that grows with overall
    perk level. Filling it with the usual "레벨업당 ... 만렙 ..." framing
    produces nonsense (that one ballooned to a literal "+8000%"), so those
    get a plain flat value instead.
    """
    stats_queue = list(passive_stats)
    filled = []
    for d in raw_descriptions:
        if "%x%" not in d:
            filled.append(d)
            continue

        is_capstone_line = bool(CAPSTONE_LINE_RE.match(d))

        # Some descriptions state their own hard cap in prose, e.g.
        # "...(최대 30%)" -- the game clamps the runtime value there even
        # though the raw per-level*20 arithmetic would exceed it (Bulwark:
        # 0.02/level * 20 = 40%, but the mod clamps display to 30%).
        cap_match = re.search(r"최대[^0-9]{0,20}?([\d.]+)%", strip_font(d))
        cap = float(cap_match.group(1)) if cap_match else None

        def _sub(match, _queue=stats_queue, _cap=cap, _capstone=is_capstone_line):
            if _capstone:
                # The ini's field order doesn't reliably line up with a
                # placeholder embedded mid-capstone (verified: Parasite's
                # "흡수된 적 1명당 +%x%%" would otherwise consume the wrong
                # queue entry and print a nonsense number). Point at the
                # accurate value in the "고정 효과" section instead of
                # guessing which fixed stat it is.
                return "(정확한 수치는 아래 '고정 효과' 참고)"
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


# Site-wide Korean terminology fixes applied to every string in the final
# output, including raw text pulled straight from the KOR ini (which we
# don't edit in place, since it's the mod's own localization asset).
TERMINOLOGY_FIXES = [
    ("퍽", "퍼크"),
    ("도쐬", "도쉬"),
    ("커맨도", "코만도"),
]


def normalize_terminology(value):
    if isinstance(value, str):
        for old, new in TERMINOLOGY_FIXES:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [normalize_terminology(v) for v in value]
    if isinstance(value, dict):
        return {k: normalize_terminology(v) for k, v in value.items()}
    return value


def split_scaling_and_fixed_stats(passive_stats, raw_descriptions):
    """A perk's DKUpgrade_Perk_X ini section isn't uniformly a set of
    per-level-scaling passives -- the KOR text only ever treats the first
    N fields (one per '%x%' placeholder) as growing with perk level. Any
    fields after that are one-shot capstone bonuses (Level10Foo/Level20Bar)
    or flat constants (a fixed drop chance, a flat pickup amount) that the
    site was previously running through the same "value * selected level"
    slider math as the real passives -- e.g. Scavenger's fixed 30-ammo pickup
    was shown as "600" at Lv20. Split them so only genuine passives get the
    per-level treatment; the rest are reported as constant values.
    """
    # Only count placeholders in the leading, non-capstone lines -- a '%x%'
    # inside a "레벨 N:" capstone description (e.g. Parasite's per-siphoned-
    # enemy damage bonus) is a per-stack/fixed value for that ability, not
    # another genuinely level-scaling passive.
    scaling_count = sum(
        len(PLACEHOLDER_RE.findall(d)) for d in raw_descriptions if not CAPSTONE_LINE_RE.match(d)
    )
    scaling, fixed = [], []
    for i, stat in enumerate(passive_stats):
        if i < scaling_count:
            stat["scaling"] = True
            scaling.append(stat)
        else:
            stat["scaling"] = False
            # These aren't "per level" at all -- lv10/lv20 would otherwise
            # imply linear growth that doesn't happen, so just mirror the
            # flat value so any leftover consumer sees a constant.
            stat["lv10"] = stat["value"]
            stat["lv20"] = stat["value"]
            stat["lv10Display"] = stat["display"]
            stat["lv20Display"] = stat["display"]
            level_match = re.match(r"Level(\d+)", stat["key"])
            stat["capstoneLevel"] = int(level_match.group(1)) if level_match else None
            fixed.append(stat)
    return scaling, fixed


def reconcile_perk_descriptions(raw_descriptions, filled_descriptions, fixed_stats):
    """Beyond the '%x%'-templated lines, a perk's capstone/flavor description
    lines (levels 10/20, passive utility text) often hardcode a number that
    drifts from the ini after a balance pass -- same issue as skill text.
    Reconcile them the same way, but only apply the result if every fixed
    stat's notation matches atomically across the *combined* candidate
    lines; otherwise leave the original wording untouched rather than risk
    losing the flavor text for an uncertain guess.
    """
    candidate_idx = [
        i for i, d in enumerate(raw_descriptions)
        if "%x%" not in d and CAPSTONE_LINE_RE.match(d)
    ]
    if not candidate_idx or not fixed_stats:
        return filled_descriptions
    joined = "\x00".join(filled_descriptions[i] for i in candidate_idx)
    new_joined, ok, _ = reconcile_skill_text(joined, fixed_stats)
    if not ok:
        return filled_descriptions
    result = list(filled_descriptions)
    for idx, part in zip(candidate_idx, new_joined.split("\x00")):
        result[idx] = part
    return result


def build():
    main_sections = parse_ini_generic(INI_MAIN)
    kor_sections = parse_kor_ini(INI_KOR)
    dk_skill_registry = parse_dk_skill_registry(INI_UPGRADES)
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
        scaling_stats, fixed_stats = split_scaling_and_fixed_stats(passive_stats, raw_descs)
        filled_descriptions = reconcile_perk_descriptions(raw_descs, filled_descriptions, fixed_stats)
        descriptions = [
            {"raw": d, "text": strip_font(d), "isCapstone": bool(CAPSTONE_LINE_RE.match(d)) or d.startswith("레벨")}
            for d in filled_descriptions
        ]
        perk_patch_note = "; ".join(patch_notes.get(f"DKUpgrade_Perk_{key}", []))

        skill_notes = manual_verdicts.get("skillNotes", {}).get(key, {})
        skills = []
        for short, is_disabled, disabled_note in dk_skill_registry.get(key, []):
            skill_section = f"DKUpgrade_Skill_{short}"
            skor = kor_sections.get(skill_section, {})
            sini = main_sections.get(skill_section, [])
            cost_keys = set(SKILL_COST_STATS.get(short, []))
            signed_sini = [(k, to_num(v) * (-1 if k in cost_keys else 1) if isinstance(to_num(v), (int, float)) else to_num(v))
                           for k, v in sini if k != "MODEVERSION"]
            raw_values = build_stat_entries(signed_sini)
            skill_patch_note = "; ".join(patch_notes.get(skill_section, []))

            t1_entries, t2_entries = split_tiers(raw_values)
            std_orig = skor.get("StandardSkillUpgradeDescription")
            delx_orig = skor.get("DeluxeSkillUpgradeDescription")
            std_raw, std_ok, std_fixed = reconcile_skill_text(std_orig, t1_entries)
            delx_raw, delx_ok, delx_fixed = reconcile_skill_text(delx_orig, t2_entries)

            # If the flavor sentence couldn't be safely patched in place,
            # drop it in favor of a plain ini-only line -- never show
            # KOR-original numbers that might not match KFZedternalUnlimited.ini.
            if not std_ok:
                fallback = build_ini_only_text(t1_entries)
                if fallback:
                    std_raw, std_fixed = fallback, True
            if not delx_ok:
                fallback = build_ini_only_text(t2_entries)
                if fallback:
                    delx_raw, delx_fixed = fallback, True

            skills.append({
                "key": short,
                "name": skor.get("UpgradeName", short),
                "standardDesc": strip_font(std_raw),
                "deluxeDesc": strip_font(delx_raw),
                "standardDescRaw": std_raw,
                "deluxeDescRaw": delx_raw,
                "rawValues": raw_values,
                "hasKorText": bool(skor),
                "note": skill_notes.get(short),
                "isPatched": bool(skill_patch_note),
                "patchNote": skill_patch_note or None,
                "textFixed": std_fixed or delx_fixed,
                "disabled": is_disabled,
                "disabledNote": disabled_note,
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
            "passiveStats": scaling_stats,
            "fixedStats": fixed_stats,
            "role": role_desc.get("role"),
            "endgame": role_desc.get("endgame"),
            "descriptions": descriptions,
            "skills": skills,
            "skillCount": len(skills),
            "verdict": verdict,
            "grade": (verdict or {}).get("grade"),
            "isPatched": is_patched,
            "patchNote": perk_patch_note or None,
            "testWarning": build_test_warning(verdict, is_patched),
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
            "testWarning": build_test_warning(None, base_is_patched),
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
    data = normalize_terminology(data)

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
