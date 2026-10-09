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
# Local working copies are fallbacks for contributors who do not have the
# source checkout or game server mounted. The canonical Windows paths are
# used automatically on the maintainer's machine and can be overridden with
# ZEDTERNAL_SOURCE_DIR / ZEDTERNAL_OPERATIONS_DIR.
SOURCE_DIR = os.environ.get(
    "ZEDTERNAL_SOURCE_DIR",
    r"C:\Users\yss19\Documents\Projects\zedternal-unlimited-main\ZedternalTempered",
)
OPERATIONS_DIR = os.environ.get(
    "ZEDTERNAL_OPERATIONS_DIR",
    r"D:\KF2server\KFGame\Config\SV_Zedternal_Tempered",
)


def preferred_file(directory, filename, fallback):
    candidate = os.path.join(directory, filename)
    return candidate if os.path.isfile(candidate) else os.path.join(ROOT, fallback)


INI_MAIN = preferred_file(OPERATIONS_DIR, "KFZedternalUnlimited.ini", "KFZedternalUnlimited.ini")
INI_BALANCE = preferred_file(
    OPERATIONS_DIR, "KFZedternalUnlimited_Balance.ini", "KFZedternalUnlimited_Balance.ini"
)
INI_KOR = preferred_file(
    os.path.join(SOURCE_DIR, "Localization", "KOR"), "ZedternalTempered.kor", "ZedternalRBPerkpackage.KOR.ini"
)
INI_REBORN_KOR = preferred_file(
    os.path.join(SOURCE_DIR, "Localization", "KOR"),
    "ZedternalReborn.kor",
    "ZedternalReborn.kor.ini",
)
INI_UPGRADES = preferred_file(SOURCE_DIR, "KFZedternalReborn_Upgrades.ini", "KFZedternalReborn_Upgrades.ini")
INI_GAME = preferred_file(OPERATIONS_DIR, "KFZedternalReborn_Game.ini", "KFZedternalReborn_Game.ini")
MANUAL_BASE = os.path.join(ROOT, "data", "manual_base_perks.json")
MANUAL_VERDICTS = os.path.join(ROOT, "data", "manual_verdicts.json")
MANUAL_ROLES = os.path.join(ROOT, "data", "manual_role_descriptions.json")
MANUAL_SKILL_OVERRIDES = os.path.join(ROOT, "data", "manual_skill_overrides.json")
MANUAL_PERK_EXTRAS = os.path.join(ROOT, "data", "manual_perk_extras.json")
OUT_JSON = os.path.join(ROOT, "docs", "data", "perks.json")
SKILL_ICON_DIR = os.path.join(ROOT, "docs", "icons", "skills")
PERK_ICON_DIR = os.path.join(ROOT, "docs", "icons")
SOURCE_CLASS_DIR = os.path.join(SOURCE_DIR, "Classes")
PROGRESSION_CATALOG = os.path.join(SOURCE_CLASS_DIR, "ZTPerkProgressionCatalog.uc")


def parse_player_aurora(path):
    """Return the live server's ordered damage multipliers for the aurora UI."""
    given, taken = [], []
    holding_melee = None
    value_re = re.compile(r'Multiplier=([+-]?[\d.]+)')
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("Player_DamageGiven="):
                match = value_re.search(line)
                if match:
                    given.append(float(match.group(1)))
            elif line.startswith("Player_DamageTaken="):
                match = value_re.search(line)
                if match:
                    taken.append(float(match.group(1)))
            elif line.startswith("Player_DamageTakenMultiplierWhileHoldingMelee="):
                match = re.search(r'HOE=([+-]?[\d.]+)', line)
                if match:
                    holding_melee = float(match.group(1))
    # The live Tempered profile currently has ten general damage rows, 37
    # weapon-specific rows, six incoming-damage rows, and the melee-held
    # modifier. Keep this check aligned with the labels in docs/app.js so a
    # changed config cannot silently attach values to the wrong names.
    if len(given) != 47 or len(taken) != 6 or holding_melee is None:
        raise ValueError(
            f"Unexpected damage config in {path}: {len(given)} given, {len(taken)} taken, "
            f"holding-melee={'present' if holding_melee is not None else 'missing'}"
        )
    return {"damageGiven": given, "damageTaken": taken, "holdingMelee": holding_melee}


def merge_ini_sections(base, overrides):
    """Overlay dedicated balance sections on the server's main config."""
    merged = {section: list(rows) for section, rows in base.items()}
    for section, override_rows in overrides.items():
        rows = merged.setdefault(section, [])
        for key, value in override_rows:
            indices = [i for i, (existing_key, _) in enumerate(rows) if existing_key == key]
            if indices:
                for i in indices:
                    rows[i] = (key, value)
            else:
                rows.append((key, value))
    return merged


def skill_icon_path(short):
    if os.path.exists(os.path.join(SKILL_ICON_DIR, f"{short}.png")):
        return f"icons/skills/{short}.png"
    return None


PERK_ICON_FALLBACKS = {
    # The custom textures for these perks are loaded from the separately
    # cooked game package. Use the source-defined fallback or parent icon.
    "Diablo": "icons/berserker.png",
    "JekyllHyde": "icons/shapeshifter.png",
    "Capitalist": "icons/support.png",
}


def perk_icon_path(short, parent=None):
    candidate = f"icons/{short.lower()}.png"
    if os.path.isfile(os.path.join(PERK_ICON_DIR, f"{short.lower()}.png")):
        return candidate
    if short in PERK_ICON_FALLBACKS:
        return PERK_ICON_FALLBACKS[short]
    if parent and os.path.isfile(os.path.join(PERK_ICON_DIR, f"{parent.lower()}.png")):
        return f"icons/{parent.lower()}.png"
    return "icons/support.png"


STATIC_PERK_STAT_DEFS = {
    "Capitalist": [
        {"index": 0, "key": "Dosh", "label": "웨이브 생존 보상", "unit": "currency", "scale": 1},
        {"index": 1, "key": "DoshPerKill", "label": "직접 처치 도쉬 보너스", "unit": "percent", "scale": 0.01},
    ],
    "Goliath": [
        {"index": 0, "key": "Damage", "label": "버서커 무기 피해량", "unit": "percent", "scale": 0.01},
        {"index": 1, "key": "ArmorPerLevel", "label": "기본 방어구 증가량", "unit": "percent", "scale": 0.01},
    ],
    "Vanguard": [
        {"index": 0, "key": "SupportDamagePerLevel", "label": "서포트 무기 피해량", "unit": "percent", "scale": 0.01},
        {"index": 1, "key": "SupportPenetrationPerLevel", "label": "서포트 무기 관통력", "unit": "percent", "scale": 0.01},
        {"index": 2, "key": "HealthPerLevel", "label": "최대 체력", "unit": "percent", "scale": 0.01},
    ],
}

STATIC_PERK_BONUS_FALLBACKS = {"Capitalist": [10, 1]}


def parse_source_perk_bonus(key):
    """Read PerkBonus defaults from source classes if the live INI has no override."""
    class_path = os.path.join(SOURCE_CLASS_DIR, f"ZTUpgrade_Perk_{key}.uc")
    values = {}
    if os.path.isfile(class_path):
        with open(class_path, encoding="utf-8-sig") as f:
            source = f.read()
        pattern = re.compile(
            r'PerkBonus\((\d+)\)=\(baseValue=([^,]+),\s*incValue=([^,]+),\s*maxValue=([^)]+)\)'
        )
        for match in pattern.finditer(source):
            try:
                values[int(match.group(1))] = float(match.group(3).strip().rstrip("f"))
            except ValueError:
                continue
    if not values and key in STATIC_PERK_BONUS_FALLBACKS:
        values = dict(enumerate(STATIC_PERK_BONUS_FALLBACKS[key]))
    return values


def build_static_perk_stats(key, bonus_values):
    stats = []
    for definition in STATIC_PERK_STAT_DEFS.get(key, []):
        value = bonus_values.get(definition["index"])
        if value is None:
            continue
        value *= definition["scale"]
        stats.append({
            "key": definition["key"],
            "label": definition["label"],
            "value": value,
            "unit": definition["unit"],
            "display": format_value_as(value, definition["unit"]),
            "scaling": True,
            "lv10": value * 10,
            "lv20": value * 20,
            "lv10Display": format_value_as(value * 10, definition["unit"]),
            "lv20Display": format_value_as(value * 20, definition["unit"]),
        })
    return stats


PERK_LEVEL_STAT_LABELS = {
    "Diablo": {
        "HeavyDamagePerLevel": "강공격 피해량",
        "LargeMeleeDamagePerLevel": "대형 제드 대상 근접 피해량",
    },
    "Shapeshifter": {
        "Buff_Carnage_PerLevel": "전체 피해량",
        "Buff_Executioner_PerLevel": "헤드샷 피해량",
        "Buff_Rampage_PerLevel": "연사 속도",
        "Buff_Crusher_PerLevel": "강공격 피해량",
        "Buff_Berserker_PerLevel": "근접 공격 속도",
        "Buff_Fortress_PerLevel": "받는 피해 감소",
        "Buff_Leech_PerLevel": "처치 시 체력 회복",
        "Buff_Anchor_PerLevel": "반동 감소",
        "Buff_Hawk_PerLevel": "탄퍼짐 감소",
        "Buff_Speedloader_PerLevel": "재장전 속도",
        "Buff_Switchblade_PerLevel": "무기 전환 속도",
        "Buff_Speedfreak_PerLevel": "이동 속도",
        "Buff_Hoarder_PerLevel": "예비 탄약",
        "Buff_Drumfire_PerLevel": "탄창 크기",
        "Buff_Phantom_PerLevel": "ZED 타임 연사 속도",
    },
}

PERK_STAT_LABEL_OVERRIDES = {
    "Diablo": {
        "DeathwaveInterval": "데스웨이브 간격", "DeathwaveRadius": "데스웨이브 반경",
        "FearDeathwavePct": "공포 데스웨이브 피해 비율", "HellDeathwavePct": "지옥 데스웨이브 피해 비율",
        "ReservoirPct": "누적 피해 보너스 비율", "MeleeLedgerBonus": "근접 공격 누적 보너스",
        "ScorchedWakePct": "그을린 흔적 피해 비율", "EchoPct": "메아리 피해 비율",
        "DemonSkinResistance": "악마 가죽 피해 저항", "BloodTributeHealPct": "피의 헌납 치유 비율",
        "HellgateRadiusBonus": "지옥문 범위 보너스", "ApocalypsePct": "종말 피해 비율",
    },
    "Agony": {"CapstoneDamageBonus": "캡스톤 피해량 보너스", "KillExtensionSeconds": "처치 시 ZED 타임 연장"},
    "Hivemind": {"SwarmCooldownSeconds": "무리 재사용 대기시간"},
    "JekyllHyde": {
        "HydeDuration": "하이드 변신 지속시간", "HydeDurationCapstoneMult": "캡스톤 변신 지속시간 배율",
        "HydeBodyScale": "하이드 몸집 배율", "HydeScaleRate": "하이드 변신 속도",
        "HydeMeleeBonus": "하이드 근접 피해 보너스", "HydeGunDamageMult": "하이드 총기 피해 배율",
        "HydeAoERadius": "하이드 충격파 반경", "HydeAoEMinDamageFrac": "하이드 충격파 최소 피해 비율",
        "HydeChargesBase": "웨이브당 기본 변신 횟수", "HydeChargesCapstone2": "20레벨 변신 횟수",
        "HydeFinalDamageTakenMult": "하이드 받는 피해 배율", "Jekyll_MovePerRank": "지킬 랭크당 이동 속도",
        "Jekyll_ReloadPerRank": "지킬 랭크당 재장전 속도",
    },
    "Haunted": {
        "DisasterDamagePerLevel": "유령 단계당 재앙 피해량", "DisasterMinWaveProgress": "재앙 최소 웨이브 진행도",
        "DisasterMaxWaveProgress": "재앙 최대 웨이브 진행도", "DisasterWarningDuration": "재앙 예고 지속시간",
    },
    "MissingNO": {
        "GlitchProcChancePerLevel": "레벨당 글리치 발동 확률", "GlitchDamageBonus": "글리치 추가 피해량",
        "GlitchDoshAmount": "글리치 도쉬 획득량", "GlitchAmmoRefillFraction": "글리치 탄약 환급 비율",
        "GlitchHealAmount": "글리치 체력 회복량", "TypeMismatchDamageScale": "타입 불일치 추가 피해량",
        "DataMissingProcChance": "데이터 누락 발동 확률", "DataMissingInvulnDuration": "데이터 누락 무적 지속시간",
        "DataMissingSpeedMultiplier": "데이터 누락 이동 속도 배율", "WaveEndDuplicateChance": "웨이브 종료 무기 복제 확률",
    },
}


def apply_perk_stat_labels(perk_key, stats):
    labels = PERK_STAT_LABEL_OVERRIDES.get(perk_key, {})
    for stat in stats:
        if stat["key"] in labels:
            stat["label"] = labels[stat["key"]]
    return stats

ENGINEER_LEVEL_STAT_PATTERNS = {
    "DamageBonus": ("드론 피해량", r"S\.DamageBonus\s*=\s*([+-]?[\d.]+)f?\s*\*\s*S\.Level"),
    "AmmoBonus": ("드론 탄약 용량", r"S\.AmmoBonus\s*=\s*([+-]?[\d.]+)f?\s*\*\s*S\.Level"),
    "RangeBonus": ("드론 탐지 반경", r"S\.RangeBonus\s*=\s*([+-]?[\d.]+)f?\s*\*\s*S\.Level"),
}


def build_engineer_perk_level_stats():
    """Read Engineer's per-level drone bonuses from the live implementation."""
    source_path = os.path.join(SOURCE_CLASS_DIR, "ZTEngineerDroneSystem.uc")
    with open(source_path, encoding="utf-8-sig") as f:
        source = f.read()
    rows = []
    for key, (_, pattern) in ENGINEER_LEVEL_STAT_PATTERNS.items():
        match = re.search(pattern, source, re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not read Engineer per-level stat {key} from {source_path}")
        rows.append((key, float(match.group(1))))
    stats = build_stat_entries(rows, with_levels=True)
    for stat in stats:
        stat["label"] = ENGINEER_LEVEL_STAT_PATTERNS[stat["key"]][0]
        stat["scaling"] = True
    return stats


ENGINEER_DRONE_STAT_LABELS = {
    "SentinelAmmo": "센티넬 기본 탄약",
    "WarthogAmmo": "워트호그 기본 탄약",
    "PreciousSentinelAmmo": "프레셔스 센티넬 탄약",
    "PreciousWarthogAmmo": "프레셔스 워트호그 탄약",
    "ReforgedSentinelAmmo": "리포지드 센티넬 탄약",
    "ReforgedWarthogAmmo": "리포지드 워트호그 탄약",
    "MaxLifetimeSeconds": "드론 최대 지속시간 (0 = 제한 없음)",
}

SECTION_RE = re.compile(r"^\[(?:[^.\]]+\.)?(.+)\]$")


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
                current = canonical_section(m.group(1))
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


def canonical_section(section):
    """Map current ZT/ZUT config namespaces onto the site's stable data keys."""
    replacements = (
        ("ZUTUpgrade_Perk_Base_", "DKWrapper_Perk_"),
        ("ZTWrapper_Perk_", "DKWrapper_Perk_"),
        ("ZUTUpgrade_Skill_", "WMUpgrade_Skill_"),
        ("ZTWrapper_Skill_", "WMUpgrade_Skill_"),
        ("ZTUpgrade_Perk_", "DKUpgrade_Perk_"),
        ("ZTUpgrade_Skill_", "DKUpgrade_Skill_"),
    )
    for old, new in replacements:
        if section.startswith(old):
            return new + section[len(old):]
    return section


def parse_patch_notes(path):
    """section_name -> [comment_text, ...] for lines carrying a '; 구 ...' balance-patch changelog note.

    The operations KFZedternalUnlimited.ini is the authoritative, currently-applied values file. Whenever a
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
                current = canonical_section(m.group(1))
                continue
            if current is None or ";" not in line:
                continue
            comment = line.split(";", 1)[1].strip()
            if "구 " in comment:
                notes.setdefault(current, []).append(comment)
    return notes


KOR_LINE_RE = re.compile(r'^(\w+)\s*=\s*(?:"(.*)"|(.*))\s*$')


def parse_kor_ini(path, encoding="utf-8-sig"):
    """section_name -> dict of {UpgradeName, descriptions:[...], StandardSkillUpgradeDescription, DeluxeSkillUpgradeDescription}"""
    sections = {}
    current = None
    with open(path, encoding=encoding) as f:
        for raw in f:
            line = raw.rstrip("\n").strip()
            if not line or line.startswith("//"):
                continue
            m = SECTION_RE.match(line)
            if m:
                current = canonical_section(m.group(1))
                sections[current] = {"descriptions": []}
                continue
            if current is None:
                continue
            km = KOR_LINE_RE.match(line)
            if not km:
                continue
            key, val = km.group(1), km.group(2) if km.group(2) is not None else km.group(3)
            val = val.replace('\\"', '"')
            if key == "UpgradeName":
                sections[current]["UpgradeName"] = val
            elif key.startswith("PerkUpgradeDescription"):
                sections[current]["descriptions"].append(val)
            elif key == "SkillUpgradeDescription1":
                # Current Tempered localization uses numbered tier keys for
                # some remade skills; keep the older explicit key format
                # supported below for the rest of the catalog.
                sections[current].setdefault("StandardSkillUpgradeDescription", val)
            elif key == "SkillUpgradeDescription2":
                sections[current].setdefault("DeluxeSkillUpgradeDescription", val)
            else:
                sections[current][key] = val
    return sections


def strip_font(s):
    if not s:
        return s
    s = re.sub(r"<font[^>]*>", "", s)
    s = s.replace("</font>", "")
    return s


UNLOCK_RULE_RE = re.compile(r'PerkUnlockRules=\(PerkName="(?:ZT|DK)Upgrade_Perk_(\w+)",([^)]*)\)')
UNLOCK_REQUIREMENT_PERK_RE = re.compile(
    r'Req([123])Perk="(?:ZUTUpgrade_Perk_Base_|WMUpgrade_Perk_|ZTUpgrade_Perk_|DKUpgrade_Perk_)(\w+)"'
)
UNLOCK_REQUIREMENT_LEVEL_RE = re.compile(r'Req([123])Level=(\d+)')


def parse_unlock_rules(main_sections):
    rules = {}
    rows = main_sections.get("DKConfig_PerkUnlockRules", [])
    # PerkUnlockRules is a repeated key; re-scan the raw file for full value since '=' inside value breaks generic split
    with open(INI_MAIN, encoding="utf-8-sig") as f:
        text = f.read()
    for m in UNLOCK_RULE_RE.finditer(text):
        adv, body = m.group(1), m.group(2)
        perk_by_index = {int(index): perk for index, perk in UNLOCK_REQUIREMENT_PERK_RE.findall(body)}
        level_by_index = {int(index): int(level) for index, level in UNLOCK_REQUIREMENT_LEVEL_RE.findall(body)}
        requirements = []
        for index in sorted(set(perk_by_index) & set(level_by_index)):
            requirement = {"perk": perk_by_index[index], "level": level_by_index[index]}
            if requirement not in requirements:
                requirements.append(requirement)
        if requirements:
            distinct_perks = {req["perk"] for req in requirements}
            rules[adv] = {
                "parentPerk": requirements[0]["perk"],
                "unlockLevel": requirements[0]["level"] if len(distinct_perks) == 1 else None,
                "requirements": requirements,
                "isCombinationUnlocked": len(distinct_perks) > 1,
            }
    return rules


DK_SKILL_REGISTRY_RE = re.compile(
    r'([#;])?SkillUpgrade_Upgrade=\(PerkPath="(?:ZedternalTempered|ZedternalRBPerkpackage)\.(?:ZT|DK)Upgrade_Perk_(\w+)",'
    r'SkillPath="(?:ZedternalTempered|ZedternalRBPerkpackage)\.(?:ZT|DK)Upgrade_Skill_(\w+)"\)(?:\s*;\s*(.*))?'
)

# Same registry file, but the base (10-perk) skill roster -- registered under
# the game's own "WM" (WildMonster/base perk) namespace rather than "DK".
WM_SKILL_REGISTRY_RE = re.compile(
    r'([#;])?SkillUpgrade_Upgrade=\(PerkPath="(?:ZedternalTempered\.ZUTUpgrade_Perk_Base_|ZedternalReborn\.WMUpgrade_Perk_)(\w+)",'
    r'SkillPath="(?:ZedternalTempered\.(?:ZUT|ZT)Upgrade_Skill_|ZedternalReborn\.WMUpgrade_Skill_)(\w+)"\)(?:\s*;\s*(.*))?'
)

ACTIVE_PERK_REGISTRY_RE = re.compile(
    r'PerkUpgrade_Upgrade=\(PerkPath="(?:ZedternalTempered\.ZTUpgrade_Perk_|ZedternalRBPerkpackage\.DKUpgrade_Perk_)(\w+)",bIsStatic=(True|False)\)'
)


def ci_lookup(mapping, key):
    """Case-insensitive dict lookup (exact-case match wins)."""
    if key in mapping:
        return mapping[key]
    lowered = key.lower()
    for k, v in mapping.items():
        if k.lower() == lowered:
            return v
    return None


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


def parse_wm_skill_registry(path):
    """Same as parse_dk_skill_registry() but for the base-perk (WM) skill roster."""
    registry = {}
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            m = WM_SKILL_REGISTRY_RE.match(raw.strip())
            if not m:
                continue
            disabled = bool(m.group(1))
            perk, skill, note = m.group(2), m.group(3), m.group(4)
            registry.setdefault(perk, []).append((skill, disabled, note))
    return registry


def parse_active_advanced_perks(path):
    """Return active perk registrations and whether each is a static perk."""
    active = {}
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith(("#", ";")):
                continue
            match = ACTIVE_PERK_REGISTRY_RE.search(line)
            if match:
                active[match.group(1)] = match.group(2) == "True"
    return active


def merge_runtime_perk_registrations(active, catalog_path):
    """Include perks inserted into the live catalog by Tempered at runtime."""
    if not os.path.isfile(catalog_path):
        return active
    with open(catalog_path, encoding="utf-8-sig") as f:
        source = f.read()
    for key, is_static in re.findall(
        r'EnsurePerk\("ZedternalTempered\.ZTUpgrade_Perk_(\w+)",\s*(True|False)\)',
        source,
        flags=re.IGNORECASE,
    ):
        active.setdefault(key, is_static.lower() == "true")
    return active


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


def build_john_wick_passives():
    """Level scaling implemented directly by ZTUpgrade_Perk_JohnWick.uc."""
    definitions = [
        ("Damage", "모든 무기 피해량", 0.01),
        ("AttackSpeed", "공격·발사 속도", 0.01),
        ("WeaponSwitch", "무기 교체 속도", 0.01),
        ("Penetration", "관통력", 0.01),
        ("ReloadSpeed", "재장전 속도", 0.005),
        ("RecoilReduction", "반동 감소", 0.005),
        ("MovementSpeed", "이동 속도", 0.0025),
        ("DamageReduction", "받는 피해 감소", 0.002),
        ("MagazineCapacity", "건슬링거 무기 탄창 용량", 0.01),
        ("SpareAmmo", "건슬링거 무기 휴대 탄약", 0.02),
    ]
    result = []
    for key, label, value in definitions:
        result.append({
            "key": key,
            "label": label,
            "value": value,
            "unit": "percent",
            "display": f"+{value * 100:g}%",
            "lv10": value * 10,
            "lv20": value * 20,
            "lv10Display": f"+{value * 1000:g}%",
            "lv20Display": f"+{value * 2000:g}%",
            "scaling": True,
        })
    return result


def source_skill_has_deluxe(short):
    """Return a skill's actual deluxe availability when its class declares it."""
    class_path = os.path.join(SOURCE_CLASS_DIR, f"ZTUpgrade_Skill_{short}.uc")
    if not os.path.isfile(class_path):
        return None
    with open(class_path, encoding="utf-8-sig") as f:
        source = f.read()
    match = re.search(r"\bbHasDeluxe\s*=\s*(True|False)", source, re.IGNORECASE)
    return match.group(1).lower() == "true" if match else None


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
    # Lookahead-only: the number often sits in its own <font> span, closed
    # before the literal "도쉬" label (e.g. "<font ...>8</font> 도쉬") -- a
    # greedy match-and-replace of the whole span would eat that closing tag.
    # Matching just the digits and leaving the label (and any tag) untouched
    # keeps the surrounding markup intact; see the "currency" queue below,
    # which supplies bare numbers instead of the full "N 도쉬" display string.
    "currency": re.compile(r"[\d,]+(?:\.\d+)?(?=(?:</font>)?\s*도쉬)"),
}

HEALTH_BARE_RE = re.compile(r"(체력(?:</font>)?[^<>\d]*(?:<font[^>]*>)?)(\d+(?:\.\d+)?)(%?)")

STACK_TOTAL_RE = re.compile(
    r"([+-]?\d+(?:\.\d+)?)%(?:(?!%).){0,60}?(\d+)(?:</font>)?\s*스택.{0,40}?([+-]?\d+(?:\.\d+)?)%"
)


def reconcile_stack_total_text(raw_text, tier_entries):
    """Several "stack" skills state both a per-stack percent AND the
    derived grand total at max stacks in one sentence (e.g.
    CascadingMassacre: "스택당 +8% (최대 5스택, +40%)") -- the second number
    is per_stack * max_stacks, not its own ini field, so the normal
    token-count-based reconciler can never match it (it sees 2 percent
    tokens but only 1 percent-type ini value) and always falls through to
    the flat fallback. Detect the "N%....M스택....P%" shape and recompute
    both numbers from the current ini.

    Confidence anchor: the stack count named in the text (M) must exactly
    match a "count"-type ini field, and exactly one "percent"-type field
    must remain -- NOT requiring the text's current total (P) to already
    match the freshly-derived one, since that total is exactly the number
    that's usually stale after a per-stack rebalance (verified: HuntDown's
    text says "+25%" total but the current per-stack value only derives to
    "+15%" -- that mismatch is the bug being fixed, not a sign to bail).
    """
    if not raw_text:
        return raw_text, tier_entries
    m = STACK_TOTAL_RE.search(raw_text)
    if not m:
        return raw_text, tier_entries
    stack_count_in_text = float(m.group(2))
    percent_candidates = [e for e in tier_entries if e["unit"] == "percent" and isinstance(e["value"], (int, float))]
    count_candidates = [e for e in tier_entries if e["unit"] == "count" and isinstance(e["value"], (int, float))]
    ce = next((c for c in count_candidates if c["value"] == stack_count_in_text), None)
    if not ce or len(percent_candidates) != 1:
        return raw_text, tier_entries
    pe = percent_candidates[0]
    derived = pe["value"] * ce["value"] * 100
    per_stack_s = _fmt_signed_pct(pe["value"] * 100)
    total_s = _fmt_signed_pct(derived)
    new_text = (
        raw_text[:m.start(1)] + per_stack_s
        + raw_text[m.end(1):m.start(3)] + total_s
        + raw_text[m.end(3):]
    )
    remaining = [e for e in tier_entries if e is not pe]
    return new_text, remaining


def reconcile_health_cost_text(raw_text, tier_entries):
    """Several "health cost" skills (Health is a SKILL_COST_STATS
    sign-flipped percent stat, e.g. Voodoo's) write the magnitude as a bare
    number right after '체력이' with no '%' sign at all
    ("최대 체력이 5 감소") -- the normal percent-token reconciliation requires
    an explicit '%' so it never touches these, and several have drifted from
    the current ini value (verified against every SKILL_COST_STATS Health
    skill: PowerTransfer/SoulStealer/NoStringsOnMe/OdeToGreed/
    PinpointAccuracy/Triskelion already match by coincidence -- confirming
    this is a real, consistent convention, not a guess -- while BloodRush
    and PainSplit's deluxe tier are genuinely stale). Fix the bare number in
    place using the tier's Health stat, and return a tier list with Health
    removed so it doesn't also get counted (and left unmatched) by the
    normal percent-token reconciliation pass below.

    Skips skills that already write Health with an explicit '%' (e.g.
    GlassCannon) -- those are handled by the normal percent pass already.
    A trailing negative lookahead for '%' would work here in principle, but
    Python's greedy \\d+ backtracks past it (matching "3" instead of "30"
    to satisfy "not followed by %"), corrupting the number; capturing the
    optional '%' and checking it explicitly avoids that pitfall entirely.
    """
    health = next((e for e in tier_entries if e["key"] == "Health"), None)
    if not raw_text or not health or not isinstance(health["value"], (int, float)):
        return raw_text, tier_entries
    magnitude = abs(health["value"]) * 100
    s = f"{magnitude:.2f}".rstrip("0").rstrip(".")
    found = []

    def _sub(m):
        if m.group(3):
            return m.group(0)
        found.append(True)
        return m.group(1) + s

    new_text = HEALTH_BARE_RE.sub(_sub, raw_text, count=1)
    if not found:
        return raw_text, tier_entries
    remaining = [e for e in tier_entries if e is not health]
    return new_text, remaining


FOLD_RE = re.compile(r"\d+(?:\.\d+)?\s*배")


def _fmt_plain(x):
    return f"{abs(x):.2f}".rstrip("0").rstrip(".")


def reconcile_fold_matches(raw_text, tier_entries):
    """Pre-claims "N배" (fold) tokens that exactly match a tier entry's raw
    ini value regardless of its unit classification (e.g. BatteringRam's
    ChargeDamage is classified "percent" but written as "피해량이 2배/3배가
    됩니다" -- a completely different notation than "+N%", which the
    percent-based reconciler never recognizes, and it sits alongside a
    genuinely %-styled field (SprintResistance) in the same sentence, so
    the whole-bucket "try one notation for everything" attempts in
    reconcile_skill_text() can't handle the mix either).

    Only claims an *exact* value match -- never guesses at a possibly-stale
    number -- so it's safe to run unconditionally before the main pass.
    """
    if not raw_text:
        return raw_text, tier_entries
    matches = list(FOLD_RE.finditer(raw_text))
    if not matches:
        return raw_text, tier_entries
    remaining = list(tier_entries)
    claimed = {}
    for m in matches:
        n = float(m.group(0).replace("배", "").strip())
        candidate = next(
            (e for e in remaining if isinstance(e["value"], (int, float)) and abs(e["value"]) == n), None)
        if candidate:
            remaining.remove(candidate)
            claimed[m.start()] = f"{_fmt_plain(candidate['value'])}배"
    if not claimed:
        return raw_text, tier_entries
    new_text = FOLD_RE.sub(lambda m: claimed.get(m.start(), m.group(0)), raw_text)
    return new_text, remaining


def _attempt_reconcile(raw_text, tier_entries, percent_pattern, percent_display_fn, percent_units, dedupe=False):
    """One atomic attempt: only rewrite if every unit's token count in the
    text exactly matches its ini value count for this tier. A partial
    rewrite (some numbers fixed, some left stale) would be more misleading
    than leaving the whole string untouched.

    dedupe=True collapses same-unit entries that share the exact same
    value down to one queue slot (e.g. Archangel/DivineFortitude's
    HealthBonus and ArmorBonus are both 0.1/0.25, described together as one
    "체력과 방어력이 10% 증가" clause instead of two separate numbers).
    """
    percent_vals = [e for e in tier_entries if e["unit"] in percent_units]
    if dedupe:
        seen = set()
        deduped = []
        for e in percent_vals:
            if e["value"] not in seen:
                seen.add(e["value"])
                deduped.append(e)
        percent_vals = deduped
    patterns = dict(RECONCILE_UNIT_PATTERNS, percent=percent_pattern)
    queues = {
        "percent": [percent_display_fn(e) for e in percent_vals],
        "seconds": [e["display"] for e in tier_entries if e["unit"] == "seconds"],
        # Bare number only -- the "currency" pattern above matches just the
        # digits (see its lookahead comment), so the label text already in
        # the sentence must be left in place, not duplicated.
        "currency": [f"{e['value']:,.0f}" for e in tier_entries if e["unit"] == "currency"],
    }
    for unit, pattern in patterns.items():
        if len(pattern.findall(raw_text)) != len(queues[unit]):
            return raw_text, False
    new_text = raw_text
    for unit, pattern in patterns.items():
        q = queues[unit]
        new_text = pattern.sub(lambda m, _q=q: _q.pop(0), new_text)
    return new_text, True


def reconcile_skill_text(raw_text, tier_entries):
    """Rewrite hardcoded numbers embedded in a skill's KOR-ini flavor text so
    they match the currently-applied value in KFZedternalUnlimited.ini,
    from the operations INI -- the KOR ini text is just the
    original (possibly stale) game copy. Matches tokens to ini values
    positionally, per unit type, in the order they appear; if the count of
    tokens found doesn't exactly match the count of same-unit ini values,
    the text is left untouched and reported as unverified rather than
    guessed at.

    Tries two notations for "percent"/"multiplier"-unit values, since the
    mod phrases the same kind of field both ways depending on the skill:
    - "+N%" using value*100 (HighNoon/ChainFeed/Overkill store a raw
      multiplier like 1.5 but write "재장전 속도가 150% 증가").
    - "N배" fold notation using the raw value directly (BatteringRam's
      "피해량이 2배가 됩니다").

    Skipped when a tier has two-or-more "multiplier" fields that share the
    exact same raw value (e.g. Medusa/GorgonsCurse's DamageMultiplier and
    DamageTakenMultiplier are both 0.4/0.8) -- positional matching can't
    tell which text clause each belongs to, and verified against that
    skill's actual KOR text, naively formatting both as value*100 produces
    two identical numbers where the real text states two different ones
    (+25%/+50%, not +40%/+40%). Safer to fall through to the plain
    ini-values line than confidently print a wrong number.
    """
    if not raw_text:
        return raw_text, True, False

    multiplier_values = [e["value"] for e in tier_entries if e["unit"] == "multiplier"]
    if len(multiplier_values) != len(set(multiplier_values)):
        return raw_text, False, False

    new_text, ok = _attempt_reconcile(
        raw_text, tier_entries,
        RECONCILE_UNIT_PATTERNS["percent"],
        lambda e: e["display"] if e["unit"] == "percent" else f"{_fmt_signed_pct(e['value'] * 100)}%",
        ("percent", "multiplier"),
    )
    # The FOLD ("N배") attempt below counts tokens using its OWN pattern
    # only -- if the text actually has standalone "+N%" tokens (the OTHER
    # notation) that the percent attempt above just failed to match against
    # any ini field, those tokens are invisible to FOLD_RE's own count and
    # it can vacuously "succeed" doing nothing (0 FOLD tokens == 0
    # multiplier-type candidates) while leaving a genuinely stale percent
    # number sitting right there untouched (verified: Cryophilite's Lv10
    # capstone "+500%" -- IcicleArrowBonus is a "count"-type field with no
    # percent/multiplier candidates at all, so attempt 1 correctly fails,
    # but attempt 2 has nothing to fold either and would otherwise report a
    # false "ok"). Skip the FOLD attempt entirely when unaddressed percent
    # tokens remain.
    if not ok and not RECONCILE_UNIT_PATTERNS["percent"].search(raw_text):
        new_text, ok = _attempt_reconcile(
            raw_text, tier_entries,
            FOLD_RE,
            lambda e: f"{_fmt_plain(e['value'])}배",
            ("percent", "multiplier"),
        )
    if not ok:
        # A single clause sometimes covers several identically-valued
        # fields at once (e.g. DivineFortitude's "최대 체력과 최대 방어력이
        # 10% 증가합니다" covers HealthBonus AND ArmorBonus, both 0.1/0.25).
        new_text, ok = _attempt_reconcile(
            raw_text, tier_entries,
            RECONCILE_UNIT_PATTERNS["percent"],
            lambda e: e["display"] if e["unit"] == "percent" else f"{_fmt_signed_pct(e['value'] * 100)}%",
            ("percent", "multiplier"),
            dedupe=True,
        )
    if not ok:
        return raw_text, False, False
    return new_text, True, new_text != raw_text


def build_ini_only_text(tier_entries):
    """Fallback for when reconcile_skill_text() can't safely patch the
    original KOR flavor sentence in place (e.g. one sentence covers several
    ini keys, or the text phrases a value as "N배" while the ini treats it
    as a percent -- both real cases found in this data). Rather than leave
    stale/mismatched numbers on the page, drop the flavor prose entirely and
    show a plain line built only from the operations INI, which is the
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


# build_test_warning() (generic "이 퍼크는 최근 ... 테스트 중입니다" banner) was
# removed 2026-07-07 -- superseded by the per-patch buff/nerf tag system
# (see compute_recent_change_tag()).


PLACEHOLDER_RE = re.compile(r"([+-]?)%x(%%?)?")
CAPSTONE_LINE_RE = re.compile(r"^(?:<font[^>]*>)?레벨\s*\d+:")
CAPSTONE_TEXT_RE = re.compile(
    r"(?:캡스톤|^(?:레벨|LEVEL)\s*(?:10|20)\s*[-—:：]|^(?:10|20)\s*레벨(?:부터|(?=\s*[-—:：]))|^Lv\.?\s*(?:10|20)\s*[-—:：])",
    re.IGNORECASE,
)


def is_capstone_description(text):
    visible = strip_font(text).strip()
    if re.search(r"(?:캡스톤.{0,12}(?:없|미구현|미적용)|(?:없|미구현|미적용).{0,12}캡스톤)", visible):
        return False
    return bool(CAPSTONE_LINE_RE.match(text) or CAPSTONE_TEXT_RE.search(visible))


def reorder_placeholder_targets(passive_stats, raw_descriptions):
    """compute_placeholder_groups() (and, downstream, fill_percent_placeholders())
    consumes passive_stats positionally, one entry per '%x' placeholder in
    description order -- that assumes ini declaration order matches
    description order, which usually holds but not always. A bare '%x'
    immediately followed by '도쉬' specifically expects a field literally
    named Dosh (e.g. Gambler's ini lists an unrelated 'Doodle' field before
    'Dosh', but its first description line is the dosh reward). Reorder the
    list once up front so both consumers agree.
    """
    order = list(passive_stats)
    pos = 0
    for d in raw_descriptions:
        if CAPSTONE_LINE_RE.match(d):
            continue
        for m in PLACEHOLDER_RE.finditer(d):
            if pos >= len(order):
                break
            is_percent = bool(m.group(2))
            following = d[m.end():m.end() + 6]
            if not is_percent and "도쉬" in following and order[pos]["key"].lower() != "dosh":
                dosh_idx = next((i for i in range(pos, len(order)) if order[i]["key"].lower() == "dosh"), None)
                if dosh_idx is not None:
                    order[pos], order[dosh_idx] = order[dosh_idx], order[pos]
            pos += 1
    return order


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


# Perks whose descriptions were converted to static text (no more literal
# '%x%' for determine_stat_signs() to read a sign off of), but which DO have
# genuine negative/penalty stats -- keyed by ini field name -> sign. Verified
# against each perk's own static KOR sentence (e.g. Voodoo's "-5%·만렙-50%"
# for Health/Armor, Tycoon's "-0.8%·만렙-16%" for BulkDiscount).
IMPLICIT_STAT_SIGNS = {
    "Voodoo": {"Health": -1, "Armor": -1},
    "Tycoon": {"BulkDiscount": -1, "CostCutting": -1},
}


def apply_implicit_stat_signs(perk_key, filtered_kv, signs):
    overrides = IMPLICIT_STAT_SIGNS.get(perk_key)
    if not overrides:
        return signs
    return [overrides.get(k, sign) for (k, _v), sign in zip(filtered_kv, signs)]


def _fmt_signed_pct(x):
    s = f"{abs(x):.2f}".rstrip("0").rstrip(".")
    return f"{'-' if x < 0 else '+'}{s}"


def fill_percent_placeholders(raw_descriptions, placeholder_groups):
    """Replace '%x%' in the perk's game-text descriptions with BOTH the
    per-level-up increase and the Lv20 (max/만렙) total, computed from the
    matching placeholder group's first entry -- e.g. "+%x%%" becomes
    "레벨업당 +3% · 만렙(Lv20) +60%". Stat values are already signed
    (see determine_stat_signs), so the displayed sign always matches the
    stat's real direction rather than assuming every placeholder is a bonus.

    placeholder_groups is pre-partitioned by compute_placeholder_groups(),
    one group per leading (non-capstone) '%x%' occurrence, in description
    order -- this mirrors how the mod's own authors wrote the two lists side
    by side (verified: works cleanly for every perk with 2-3 leading %x%
    stats, e.g. Cinder's FireDamagePerLevel/BurningTargetDamagePerLevel),
    while also correctly leaving a placeholder with NO backing ini field
    (e.g. TimeTraveler's "ZED 타임 지속 시간" -- the ini only has the 14
    fields for its other "모든 능력치" placeholder, nothing left for this
    one) as an explicit "no ini data" marker instead of silently borrowing
    an unrelated field's value just because a flat queue wasn't empty yet.

    A '%x%' inside a "레벨 N:" capstone line is a different animal though --
    it describes a fixed or per-stack bonus for that one-shot ability (e.g.
    Parasite's "흡수된 적 1명당 +%x%%"), not something that grows with overall
    perk level. Filling it with the usual "레벨업당 ... 만렙 ..." framing
    produces nonsense (that one ballooned to a literal "+8000%"), so those
    get a plain flat value instead.
    """
    groups_queue = list(placeholder_groups)
    filled = []
    for d in raw_descriptions:
        if "%x" not in d:
            filled.append(d)
            continue

        is_capstone_line = bool(CAPSTONE_LINE_RE.match(d))

        # Some descriptions state their own hard cap in prose, e.g.
        # "...(최대 30%)" -- the game clamps the runtime value there even
        # though the raw per-level*20 arithmetic would exceed it (Bulwark:
        # 0.02/level * 20 = 40%, but the mod clamps display to 30%).
        cap_match = re.search(r"최대[^0-9]{0,20}?([\d.]+)%", strip_font(d))
        cap = float(cap_match.group(1)) if cap_match else None

        def _sub(match, _groups=groups_queue, _cap=cap, _capstone=is_capstone_line):
            if _capstone:
                # The ini's field order doesn't reliably line up with a
                # placeholder embedded mid-capstone (verified: Parasite's
                # "흡수된 적 1명당 +%x%%" would otherwise consume the wrong
                # queue entry and print a nonsense number). Point at the
                # accurate value in the "고정 효과" section instead of
                # guessing which fixed stat it is.
                return "(정확한 수치는 아래 '고정 효과' 참고)"
            if not _groups:
                sign = match.group(1) or "+"
                return f"{sign}?(하드코딩·비공개)"
            group = _groups.pop(0)
            if not group:
                sign = match.group(1) or "+"
                return f"{sign}?(하드코딩·비공개)"
            stat = group[0]
            is_percent = bool(match.group(2))
            if not is_percent:
                # A bare '%x' (no '%' at all, e.g. "%x 도쉬" or "%x초") --
                # the unit word (도쉬/초/발/개) already sits in the
                # surrounding KOR text, so just substitute the flat number
                # (still growing per level; e.g. Headhunter's per-headshot
                # dosh reward was never being filled in at all before this).
                per_level = stat["value"]
                max_val = stat["value"] * 20
                return f"레벨업당 {_fmt_signed_pct(per_level)} · 만렙(Lv20) {_fmt_signed_pct(max_val)}"
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
    # The mod's format strings escape a literal percent as '%%' (e.g.
    # Predator's "+15%%"); the site renders raw text, so collapse them.
    # Safe here: this pass runs on the final output dict, after every
    # '%x%%' placeholder has already been filled.
    ("%%", "%"),
]


# Perks whose KOR text uses NO '%x%' templating anywhere, so
# compute_placeholder_groups() finds zero placeholders and (without this
# override) would dump every ini field into "fixed effects" -- including
# fields that are genuinely per-level (Riot's *PerLevel fields; Metronome's
# and Predator's "레벨당"/"등급당" wording). Value = how many of the perk's
# LEADING ini fields (in file order) are real per-level scaling stats;
# verified per perk against its own KOR sentences, not guessed:
#   Riot: MeleeDamagePerLevel/DamageResistancePerLevel/AttackSpeedPerLevel
#     grow with level ("레벨당ㅁ..."); DamagePerNearbyEnemy/ResistancePerNearbyEnemy
#     scale with a *stack count* (nearby enemies), not perk level, so they
#     stay in "fixed effects" alongside the genuinely constant thresholds.
#   Metronome: each of the 4 phase lines states "레벨당" for its first stat
#     (AssaultDamage, TempoReload, MomentumSpeed, BastionDamage) and, where
#     present, a second stat in the same clause (AssaultPenetration,
#     TempoRateOfFire, MomentumWeaponSwitch) -- BASTION's "피해 저항 15%" has
#     no backing ini field at all, so its group stops at BastionDamage alone.
#   Predator: "등급당 모든 피해량" -- its one and only ini field (Damage) is
#     per-level; there's nothing left to be "fixed effects" for this perk.
IMPLICIT_SCALING_COUNTS = {
    "Riot": 3,
    "Metronome": 7,
    "Predator": 1,
    # The rest were added after converting every remaining %x%%-templated
    # PerkUpgradeDescription line to static pre-computed text (2026-07-05,
    # commit fef92f8) -- that conversion removed the last '%x%' substrings
    # compute_placeholder_groups() relies on, so every one of these perks'
    # counts silently dropped to 0. Values restored from the pre-conversion
    # build (commit 2d3cedd) to match exactly.
    "Bulwark": 3,
    "Voodoo": 3,
    "SpecialAgent": 3,
    "Warlord": 6,
    "Agony": 2,
    "Maniac": 2,
    "ForgeWarden": 2,
    "Hollow": 2,
    "Archangel": 3,
    "Hivemind": 2,
    "Parasite": 2,
    "Symbiote": 3,
    "Pyrokinetic": 3,
    "Cinder": 2,
    "Headhunter": 1,
    "TimeTraveler": 14,
    "Reaper": 3,
    "Scavenger": 3,
    "Taskmaster": 14,
    "Frost": 3,
    "Omen": 3,
    "Daredevil": 3,
    "Wendigo": 3,
    "Cryophilite": 3,
    "Gambler": 2,
    "Artificer": 2,
    "Hydra": 3,
    "Venomancer": 3,
    "Medusa": 3,
    "Tycoon": 3,
}

# Perks whose raw ini field order doesn't match description order, so the
# leading-N-fields heuristic above (IMPLICIT_SCALING_COUNTS) would grab the
# wrong fields. Explicit key order overrides that heuristic when present.
# Gambler's ini declares Doodle/Chance/Dosh in that order, but its two
# descriptions are about Dosh (per-wave reward) then Chance (headshot
# proc) -- Doodle is an unrelated fixed stat that must stay out of scaling.
# reorder_placeholder_targets() used to fix this via literal '%x' detection
# before the descriptions were converted to static text; this is its
# manual-override equivalent for the post-conversion static-text perks.
IMPLICIT_SCALING_KEY_ORDER = {
    "Gambler": ["Dosh", "Chance"],
}

# BALANCE_COMPLETE_PERKS ("밸런싱 완료" badge) removed 2026-07-07 -- superseded
# by the per-patch buff/nerf tag system (RECENT_CHANGES, see below).
RECENT_CHANGES_PATH = os.path.join(ROOT, "data", "recent_changes.json")


KOR_DESCRIPTION_FIELDS = {
    "descriptions", "capstoneDescriptions", "role",
    "raw", "text", "standardDesc", "deluxeDesc",
    "standardDescRaw", "deluxeDescRaw",
}


def normalize_terminology(value, preserve_kor=False):
    if preserve_kor:
        return value
    if isinstance(value, str):
        for old, new in TERMINOLOGY_FIXES:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [normalize_terminology(v, preserve_kor) for v in value]
    if isinstance(value, dict):
        return {
            k: normalize_terminology(v, k in KOR_DESCRIPTION_FIELDS)
            for k, v in value.items()
        }
    return value


def compute_placeholder_groups(passive_stats, raw_descriptions, implicit_scaling_count=0):
    """A perk's DKUpgrade_Perk_X ini section isn't uniformly a set of
    per-level-scaling passives -- the KOR text only ever treats some ini
    fields as growing with perk level, one group per leading (non-capstone)
    '%x%' placeholder occurrence, in description order. Fields left over
    after the last placeholder is satisfied are one-shot capstone bonuses
    (Level10Foo/Level20Bar) or flat constants (a fixed drop chance, a flat
    pickup amount) that the site was previously running through the same
    "value * selected level" slider math as the real passives -- e.g.
    Scavenger's fixed 30-ammo pickup was shown as "600" at Lv20. Split them
    so only genuine passives get the per-level treatment.

    Usually each placeholder covers exactly one field. A single placeholder
    can also cover a whole *run* of separately-named ini fields that all
    carry the exact same value at once -- e.g. Taskmaster's "무기의 모든
    능력치가 %x% 증가합니다" (all weapon stats) covers 14 identically-valued
    fields (Damage, Heal, MagSize, ...), not just the first one. But folding
    consecutive equal-value fields into one group purely because their
    *values* happen to match is unsafe on its own: after the 2026-07-02
    global-passive-halving patch, plenty of perks ended up with two
    genuinely separate, single-field placeholders that coincidentally
    share a value (Agony's MovementPerLevel and DamagePerLevel both became
    0.01) -- folding those together silently swallowed the next field
    (Level10Movement, a one-time Lv10 capstone bonus) into the scaling
    group, making it wrongly grow with the level slider. The mod's own KOR
    text already signals genuine multi-field coverage explicitly with the
    word "모든" (all/every) -- only fold when that marker is present on the
    placeholder's own description line; otherwise each placeholder claims
    exactly one field, same as a lone-value case.

    "모든" alone still isn't sufficient: Hollow's first line reads "모든
    무기 피해량" (all WEAPON damage -- rhetorically "all", but one stat)
    and its DamagePerLevel/ReloadPerLevel coincidentally both sit at
    0.0075, so a "모든"-triggered fold swallowed ReloadPerLevel into the
    damage group and the SECOND placeholder (reload speed) then consumed
    ConditionTarget_Headshot=50, rendering a nonsense "+5000%". The genuine
    multi-field cases (Taskmaster/TimeTraveler) have 14 consecutive
    equal-value fields; coincidental collisions observed in this data are
    always runs of exactly 2 -- so additionally require the equal-value run
    to be 3+ fields long before folding.

    A handful of perks (Riot, Predator, Metronome) never use '%x%'
    templating AT ALL -- every number in their KOR text is hardcoded
    directly in the prose, including ones the mod's own field names or
    "레벨당"/"등급당" (per level/per rank) wording confirm ARE meant to grow
    with perk level (Riot: MeleeDamagePerLevel/DamageResistancePerLevel/
    AttackSpeedPerLevel -- the "PerLevel" suffix says it outright). With
    zero placeholders found, every single one of these perks' fields was
    falling through to the "fixed" bucket below: the level slider
    disappeared entirely, and the per-level RATE got displayed in the
    "고정 효과" table as if it were a game-long constant instead of a
    value that's meant to reach 20x that at Lv20. IMPLICIT_SCALING_COUNTS
    (checked by the caller) gives the leading field count that's genuinely
    per-level for these specific hardcoded-only perks, verified field by
    field against each one's own KOR sentence.
    """
    groups = []
    i, n = 0, len(passive_stats)
    for d in raw_descriptions:
        if CAPSTONE_LINE_RE.match(d):
            continue
        count = len(PLACEHOLDER_RE.findall(d))
        if count == 0:
            continue
        greedy = "모든" in d
        for _ in range(count):
            if i >= n:
                groups.append([])
                continue
            stat = passive_stats[i]
            stat["scaling"] = True
            group = [stat]
            group_value = stat["value"]
            i += 1
            if greedy:
                run_end = i
                while (run_end < n and passive_stats[run_end]["value"] == group_value
                       and not re.match(r"^Level\d+", passive_stats[run_end]["key"])):
                    run_end += 1
                if (run_end - i) + 1 >= 3:
                    while i < run_end:
                        passive_stats[i]["scaling"] = True
                        group.append(passive_stats[i])
                        i += 1
            groups.append(group)

    if not groups and implicit_scaling_count:
        for _ in range(min(implicit_scaling_count, n)):
            stat = passive_stats[i]
            stat["scaling"] = True
            groups.append([stat])
            i += 1

    fixed = []
    for stat in passive_stats[i:]:
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
    return groups, fixed


def reconcile_perk_descriptions(raw_descriptions, filled_descriptions, fixed_stats, placeholder_groups):
    """Beyond the '%x%'-templated lines, a perk's capstone/flavor description
    lines (levels 10/20, passive utility text) often hardcode a number that
    drifts from the ini after a balance pass -- same issue as skill text.
    Reconcile them the same way, trying the combined candidate lines
    atomically first (preserves the original flavor prose when it works).

    Only attempted when the perk has at least one genuine leading '%x%'
    placeholder somewhere in its non-capstone text. When it has none (e.g.
    Predator/Gambit, whose entire KOR text hardcodes every number directly
    with no %x templating anywhere), the mod's own authors never
    established ANY positional link between that perk's ini fields and its
    prose -- fixed_stats there is just leftover ini cruft (verified:
    Predator's ini has exactly one field, "Damage=0.0075" for an unrelated
    passive, that isn't referenced by any description at all), and matching
    it against a capstone line purely because the token COUNT happens to
    coincide (Predator's Lv20 "트로피 드롭률이 5%%로 고정" has exactly one
    percent token, same as fixed_stats' one entry) produces a confidently
    wrong substitution ("5%" trophy-drop-rate replaced by "+0.8%" damage) --
    worse than leaving the original text untouched.

    When the joint attempt fails (mixed hardcoded/ini-backed numbers in one
    sentence, e.g. Agony's Lv20 "500 도쉬" reward with no backing Dosh
    field), the lines are left untouched here and MANUAL_PERK_DESCS
    (data/manual_perk_desc_overrides.json) is expected to carry a
    hand-authored copy of the original KOR sentence with each number
    individually corrected against the operations INI -- prose stays,
    numbers trace to ini. Never substitute a partial/uncertain guess, and
    never truncate the flavor text: an earlier "정확한 수치는 아래 참고"
    replacement approach also leaked the capstone prefix's UNCLOSED
    <font color="#8B0000"> tag into the page and tinted everything after it
    dark red -- do not reintroduce that.
    """
    candidate_idx = [
        i for i, d in enumerate(raw_descriptions)
        if "%x%" not in d and CAPSTONE_LINE_RE.match(d)
    ]
    if not candidate_idx or not fixed_stats or not placeholder_groups:
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
    print(f"[build] 운영 수치: {INI_MAIN}")
    print(f"[build] 추가 밸런스 수치: {INI_BALANCE}")
    print(f"[build] 소스 스킬 배정: {INI_UPGRADES}")
    print(f"[build] 소스 한국어: {INI_KOR}")
    print(f"[build] 피해 오로라: {INI_GAME}")
    main_sections = merge_ini_sections(
        parse_ini_generic(INI_MAIN),
        parse_ini_generic(INI_BALANCE) if os.path.isfile(INI_BALANCE) else {},
    )
    aurora_stats = parse_player_aurora(INI_GAME)
    kor_encoding = "utf-16" if INI_KOR.lower().endswith(".kor") else "utf-8-sig"
    kor_sections = parse_kor_ini(INI_KOR, encoding=kor_encoding)
    reborn_kor_sections = parse_kor_ini(INI_REBORN_KOR, encoding="utf-16")
    dk_skill_registry = parse_dk_skill_registry(INI_UPGRADES)
    wm_skill_registry = parse_wm_skill_registry(INI_UPGRADES)
    active_advanced_perks = parse_active_advanced_perks(INI_UPGRADES)
    merge_runtime_perk_registrations(active_advanced_perks, PROGRESSION_CATALOG)
    unlock_rules = parse_unlock_rules(main_sections)
    # WaveGambler is injected into the perk progression catalog at runtime,
    # rather than listed in Config_PerkUpgrade. Its active unlock rule and
    # localization section are the authoritative signals that it is present.
    if "WaveGambler" in unlock_rules and "DKUpgrade_Perk_WaveGambler" in kor_sections:
        active_advanced_perks.setdefault("WaveGambler", False)
    patch_notes = parse_patch_notes(INI_MAIN)
    if os.path.isfile(INI_BALANCE):
        for section, notes in parse_patch_notes(INI_BALANCE).items():
            patch_notes.setdefault(section, []).extend(notes)

    with open(MANUAL_BASE, encoding="utf-8") as f:
        manual_base = json.load(f)
    with open(MANUAL_VERDICTS, encoding="utf-8") as f:
        manual_verdicts = json.load(f)
    with open(MANUAL_ROLES, encoding="utf-8") as f:
        manual_roles = json.load(f)
    with open(MANUAL_SKILL_OVERRIDES, encoding="utf-8") as f:
        manual_skill_overrides = json.load(f)
    with open(MANUAL_PERK_EXTRAS, encoding="utf-8") as f:
        manual_perk_extras = json.load(f)
    recent_changes = {}
    if os.path.exists(RECENT_CHANGES_PATH):
        with open(RECENT_CHANGES_PATH, encoding="utf-8") as f:
            recent_changes = json.load(f)

    # ---- advanced perks (커퍼 / DK) ----
    localized_perks = {k[len("DKUpgrade_Perk_"):] for k in kor_sections if k.startswith("DKUpgrade_Perk_")}
    adv_keys = sorted(localized_perks & set(active_advanced_perks))

    advanced_perks = []
    for key in adv_keys:
        is_static = active_advanced_perks.get(key, False)
        kor = kor_sections.get(f"DKUpgrade_Perk_{key}", {})
        ini_kv = main_sections.get(f"DKUpgrade_Perk_{key}", [])
        static_bonus_values = parse_source_perk_bonus(key) if is_static else {}
        raw_descs = kor.get("descriptions", [])
        filtered_kv = [(k, v) for k, v in ini_kv if k != "MODEVERSION"]
        signs = determine_stat_signs(raw_descs, len(filtered_kv))
        signs = apply_implicit_stat_signs(key, filtered_kv, signs)
        signed_kv = [(k, to_num(v) * sign if isinstance(to_num(v), (int, float)) else to_num(v))
                     for (k, v), sign in zip(filtered_kv, signs)]
        passive_stats = build_stat_entries(signed_kv, with_levels=True)
        if key == "Gambler":
            # Generic "Chance" label reads as meaningless ("발동 확률") next
            # to Gambler's other passive -- spell out what it actually is.
            for stat in passive_stats:
                if stat["key"] == "Chance":
                    stat["label"] = "헤드샷 처치시 5도쉬 획득 확률"
        passive_stats = reorder_placeholder_targets(passive_stats, raw_descs)
        if key in IMPLICIT_SCALING_KEY_ORDER:
            order = IMPLICIT_SCALING_KEY_ORDER[key]
            by_key = {s["key"]: s for s in passive_stats}
            passive_stats = [by_key[k] for k in order if k in by_key] + [s for s in passive_stats if s["key"] not in order]
        placeholder_groups, fixed_stats = compute_placeholder_groups(
            passive_stats, raw_descs, IMPLICIT_SCALING_COUNTS.get(key, 0))
        scaling_stats = [stat for group in placeholder_groups for stat in group]
        if key == "JohnWick" and not scaling_stats:
            scaling_stats = build_john_wick_passives()
        # The wiki's explanation text is an exact copy of the active Korean
        # localization. Keep %x% placeholders and wording intact; INI values
        # are displayed separately in the passive/stat sections.
        filled_descriptions = list(raw_descs)
        static_perk_stats = build_static_perk_stats(key, static_bonus_values)
        if is_static and not scaling_stats:
            scaling_stats = static_perk_stats
        if key == "Engineer":
            drone_rows = main_sections.get("ZTConfig_EngineerDrones", [])
            drone_stats = build_stat_entries(
                [(name, to_num(value)) for name, value in drone_rows if name != "MODEVERSION"]
            )
            for stat in drone_stats:
                stat["label"] = ENGINEER_DRONE_STAT_LABELS.get(stat["key"], stat["label"])
                if stat["key"] == "MaxLifetimeSeconds":
                    stat["unit"] = "seconds"
                    stat["display"] = "제한 없음" if stat["value"] == 0 else format_value_as(stat["value"], "seconds")
            fixed_stats.extend(drone_stats)
            scaling_stats.extend(build_engineer_perk_level_stats())
        if key in {"Goliath", "Vanguard"}:
            scaling_stats.extend(build_static_perk_stats(key, parse_source_perk_bonus(key)))
        if key in PERK_LEVEL_STAT_LABELS:
            level_keys = set(PERK_LEVEL_STAT_LABELS[key])
            promoted, remaining = [], []
            for stat in fixed_stats:
                (promoted if stat["key"] in level_keys else remaining).append(stat)
            if promoted:
                level_stats = build_stat_entries(
                    [(stat["key"], stat["value"]) for stat in promoted], with_levels=True
                )
                for stat in level_stats:
                    stat["label"] = PERK_LEVEL_STAT_LABELS[key][stat["key"]]
                    stat["scaling"] = True
                scaling_stats.extend(level_stats)
                fixed_stats = remaining
        descriptions = [
            {"raw": d, "text": strip_font(d), "isCapstone": is_capstone_description(d)}
            for d in filled_descriptions
        ]
        perk_patch_note = "; ".join(patch_notes.get(f"DKUpgrade_Perk_{key}", []))

        perk_extras = manual_perk_extras.get(key, {})
        # Skills confirmed to exist in the perk's game code + KOR sections
        # but absent from the Config_SkillUpgrade registry (e.g. Gambit's
        # entire hardcoded skill set) -- run them through the exact same
        # pipeline as registry skills.
        skill_roster = list(dk_skill_registry.get(key, []))
        skill_roster += [(short, False, None) for short in perk_extras.get("skills", [])]
        skills = []
        for short, is_disabled, disabled_note in skill_roster:
            skill_section = f"DKUpgrade_Skill_{short}"
            # The game's Config_SkillUpgrade registry and the KOR/main ini
            # section headers disagree on casing for a handful of skills
            # (registry "ShowOff" vs section "[DKUpgrade_Skill_Showoff]").
            # UnrealScript resolves names case-insensitively so it works
            # in-game; mirror that here or those skills read as "no data".
            skor = ci_lookup(kor_sections, skill_section) or {}
            sini = ci_lookup(main_sections, skill_section) or []
            cost_keys = set(SKILL_COST_STATS.get(short, []))
            signed_sini = [(k, to_num(v) * (-1 if k in cost_keys else 1) if isinstance(to_num(v), (int, float)) else to_num(v))
                           for k, v in sini if k != "MODEVERSION"]
            raw_values = build_stat_entries(signed_sini)
            skill_patch_note = "; ".join(patch_notes.get(skill_section, []))
            override = manual_skill_overrides.get(short, {})

            # The localization file is the sole source for visible skill prose.
            # Do not reconcile it with INI values or substitute manual text.
            std_raw = skor.get("StandardSkillUpgradeDescription")
            delx_raw = skor.get("DeluxeSkillUpgradeDescription")
            std_fixed = delx_fixed = False
            deluxe_available = source_skill_has_deluxe(short)

            skills.append({
                "key": short,
                "name": override.get("name") or skor.get("UpgradeName", short),
                "standardDesc": strip_font(std_raw),
                "deluxeDesc": strip_font(delx_raw),
                "standardDescRaw": std_raw,
                "deluxeDescRaw": delx_raw,
                "rawValues": raw_values,
                "hasKorText": bool(skor),
                "note": None,
                "isPatched": bool(skill_patch_note),
                "patchNote": skill_patch_note or None,
                "textFixed": std_fixed or delx_fixed,
                "disabled": is_disabled,
                "deluxeAvailable": deluxe_available,
                "disabledNote": disabled_note,
                "noData": not std_raw and not delx_raw,
                "icon": skill_icon_path(short),
            })

        rule = unlock_rules.get(key, {})
        verdict = manual_verdicts.get("advancedPerks", {}).get(key)
        is_patched = bool(perk_patch_note)
        role_desc = manual_roles.get(key, {})
        kor_role = next(
            (strip_font(d) for d in raw_descs if not is_capstone_description(d)),
            strip_font(raw_descs[0]) if raw_descs else None,
        )

        advanced_perks.append({
            "key": key,
            "name": kor.get("UpgradeName", key),
            "parentPerk": rule.get("parentPerk"),
            "unlockLevel": rule.get("unlockLevel"),
            "unlockRequirements": rule.get("requirements", []),
            "isCombinationUnlocked": rule.get("isCombinationUnlocked", False),
            "isStatic": is_static,
            "hasIniConfig": bool(ini_kv),
            "maxLevel": 10 if key in {"Engineer", "Technician", "Hacker"} else 20,
            "passiveStats": apply_perk_stat_labels(key, scaling_stats),
            "fixedStats": apply_perk_stat_labels(key, fixed_stats),
            "valueSourceNote": (
                "레벨별 효과는 현재 ZTUpgrade_Perk_JohnWick 클래스 구현을 기준으로 표시합니다."
                if key == "JohnWick" else
                "현재 운영 INI에 별도 수치가 없어 ZedternalTempered 퍼크 클래스의 PerkBonus 기본값을 표시합니다."
                if key in {"Capitalist", "Goliath", "Vanguard"} else
                "레벨당 드론 수치는 ZTEngineerDroneSystem 구현값이며, 드론 설정 수치는 운영 INI를 읽습니다."
                if key == "Engineer" else None
            ),
            "role": kor_role,
            "summaryHtml": perk_extras.get("summaryHtml"),
            "endgame": role_desc.get("endgame"),
            "descriptions": descriptions,
            "capstoneDescriptions": [d for d in descriptions if d["isCapstone"]],
            "skills": skills,
            "skillCount": len(skills),
            "verdict": verdict,
            "grade": (verdict or {}).get("grade"),
            "isPatched": is_patched,
            "patchNote": perk_patch_note or None,
            "testWarning": None,
            "recentChangeTag": recent_changes.get(key),
            "extraSections": perk_extras.get("extraSections", []),
            "icon": perk_icon_path(key, rule.get("parentPerk")),
        })

    advanced_perks.sort(key=lambda p: ((p["parentPerk"] or "zzz"), p["unlockLevel"] or 99))

    # ---- base perks (오퍼 / WM) ----
    base_perks = []
    for bkey, bdata in manual_base.items():
        base_kor = (
            ci_lookup(reborn_kor_sections, f"WMUpgrade_Perk_{bkey}")
            or ci_lookup(kor_sections, f"DKWrapper_Perk_{bkey}")
            or {}
        )
        base_raw_descs = base_kor.get("descriptions", [])
        base_descriptions = [
            {"raw": d, "text": strip_font(d), "isCapstone": is_capstone_description(d)}
            for d in base_raw_descs
        ]
        base_kor_role = next(
            (strip_font(d) for d in base_raw_descs if not is_capstone_description(d)),
            strip_font(base_raw_descs[0]) if base_raw_descs else None,
        )
        wrapper_kv = main_sections.get(f"DKWrapper_Perk_{bkey}", [])
        passive_stats = build_stat_entries([(k, v) for k, v in wrapper_kv if k != "MODEVERSION"], with_levels=True)
        if bkey == "Demolitionist":
            # Demolitionist's plain "피해량" field is a flat perk-weapon
            # damage bonus that applies to both direct hits and splash --
            # unlike Cfg_GrenadeDamage/Cfg_LZDamage (grenade-type / large-zed
            # conditional bonuses), so it reads as ambiguous next to them.
            for stat in passive_stats:
                if stat["key"] == "Cfg_Damage":
                    stat["label"] = "피해량(직격/스플래시)"
        unlocks = [
            {"level": p["unlockLevel"], "perk": p["key"], "name": p["name"]}
            for p in advanced_perks if p["parentPerk"] == bkey and not p["isCombinationUnlocked"]
        ]
        unlocks.sort(key=lambda u: u["level"] or 0)
        base_patch_note = "; ".join(patch_notes.get(f"DKWrapper_Perk_{bkey}", []))
        base_is_patched = bool(base_patch_note)

        base_skills = []
        for short, is_disabled, disabled_note in wm_skill_registry.get(bkey, []):
            skill_section = f"DKWrapper_Skill_{short}"
            skor = (
                ci_lookup(reborn_kor_sections, f"WMUpgrade_Skill_{short}")
                or ci_lookup(kor_sections, f"DKUpgrade_Skill_{short}")
                or {}
            )
            sini = ci_lookup(main_sections, skill_section) or []
            cost_keys = set(SKILL_COST_STATS.get(short, []))
            signed_sini = [(k, to_num(v) * (-1 if k in cost_keys else 1) if isinstance(to_num(v), (int, float)) else to_num(v))
                           for k, v in sini if k != "MODEVERSION"]
            raw_values = build_stat_entries(signed_sini)
            skill_patch_note = "; ".join(patch_notes.get(skill_section, []))
            override = manual_skill_overrides.get(short, {})

            # Use the exact Standard/Deluxe text present in the Korean source.
            std_raw = skor.get("StandardSkillUpgradeDescription")
            delx_raw = skor.get("DeluxeSkillUpgradeDescription")
            std_fixed = delx_fixed = False

            base_skills.append({
                "key": short,
                "name": override.get("name") or skor.get("UpgradeName", short),
                "standardDesc": strip_font(std_raw),
                "deluxeDesc": strip_font(delx_raw),
                "standardDescRaw": std_raw,
                "deluxeDescRaw": delx_raw,
                "rawValues": raw_values,
                "hasKorText": bool(skor),
                "note": None,
                "isPatched": bool(skill_patch_note),
                "patchNote": skill_patch_note or None,
                "textFixed": std_fixed or delx_fixed,
                "disabled": is_disabled,
                "disabledNote": disabled_note,
                "noData": not std_raw and not delx_raw,
                "icon": skill_icon_path(short),
            })

        base_perks.append({
            "key": bkey,
            "name": bdata["name"],
            "grade": bdata.get("grade"),
            "summary": None,
            "role": base_kor_role,
            "endgame": bdata.get("endgame"),
            "descriptions": base_descriptions,
            "capstoneDescriptions": [d for d in base_descriptions if d["isCapstone"]],
            "passiveStats": passive_stats,
            "maxLevel": 20,
            "strengths": bdata.get("strengths", []),
            "weaknesses": bdata.get("weaknesses", []),
            "unlocks": unlocks,
            "skills": base_skills,
            "skillCount": len(base_skills),
            "isPatched": base_is_patched,
            "patchNote": base_patch_note or None,
            "testWarning": None,
            "recentChangeTag": recent_changes.get(bkey),
            "icon": f"icons/{bkey.lower()}.png",
        })

    data = {
        "basePerks": base_perks,
        "advancedPerks": advanced_perks,
        "aurora": aurora_stats,
        "meta": {
            "advancedPerkCount": len(advanced_perks),
            "basePerkCount": len(base_perks),
            "totalSkills": sum(p["skillCount"] for p in advanced_perks) + sum(p["skillCount"] for p in base_perks),
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
