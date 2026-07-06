# -*- coding: utf-8 -*-
"""
Translates the mod's internal INI stat key names (English, CamelCase) into
human-readable Korean labels, and classifies each key's value so it can be
formatted as a percent / count / seconds / currency instead of a raw decimal.
"""
import re

# token (lowercased) -> Korean word/phrase
WORD_MAP = {
    "10": "10", "20": "20",
    "absorption": "흡수", "activation": "발동", "adaptive": "적응형",
    "allies": "아군", "ally": "아군", "ambush": "매복", "ammo": "탄약",
    "amount": "량", "amplification": "증폭", "apex": "정점", "armor": "방어구",
    "arrow": "화살", "assault": "돌격", "attack": "공격", "aura": "오라",
    "avalanche": "눈사태", "bailout": "긴급환매", "base": "기본",
    "bastion": "요새", "blood": "피", "bob": "흔들림", "body": "몸통",
    "bond": "결속", "bonus": "보너스", "boost": "증폭", "boss": "보스",
    "buff": "버프", "bulk": "대량", "burn": "화상", "burning": "화상 중인",
    "burst": "버스트", "cap": "상한", "capacity": "용량", "carry": "휴대",
    "category": "카테고리", "chance": "확률", "charge": "충전", "chill": "냉기",
    "cloak": "은신", "cloaked": "은신 중", "close": "근접", "cloud": "구름",
    "collateral": "관통 처치", "collective": "집단", "combat": "전투",
    "compound": "복리", "condition": "조건", "conversion": "전환",
    "cooldown": "재사용 대기시간", "core": "핵심", "cost": "비용",
    "count": "횟수", "crit": "치명타", "critical": "치명타", "cross": "교차",
    "crouch": "앉기", "curse": "저주", "cutting": "절감", "damage": "피해량",
    "defense": "저항력", "delay": "지연", "deluxe": "디럭스", "detection": "탐지",
    "discount": "할인",
    "dist": "거리", "divider": "나눔값", "do": "", "doodle": "낙서",
    "dosh": "도쉬", "double": "2배", "dr": "피해 감소", "duration": "지속시간",
    "durations": "지속시간", "echo": "메아리", "enemies": "적", "enemy": "적",
    "excess": "초과", "explosion": "폭발", "explosive": "폭발물",
    "ext": "연장", "extension": "연장", "extra": "추가", "factor": "계수",
    "field": "장", "fire": "화염", "for": "", "freeze": "동결",
    "fury": "분노", "gain": "획득", "ghost": "유령", "grant": "부여",
    "grenade": "수류탄", "grenades": "수류탄", "ground": "지면",
    "harvest": "수확", "haste": "가속", "head": "머리", "headshot": "헤드샷",
    "heal": "치유", "healing": "치유", "health": "체력", "hemorrhage": "출혈",
    "hit": "타격", "hits": "타격", "hodl": "존버", "hostile": "적대적",
    "hp": "체력", "hurt": "부상", "icicle": "고드름", "immunity": "면역",
    "inc": "증가", "increase": "증가", "inferno": "지옥불", "interest": "이자",
    "interval": "간격", "inv": "역", "invincibility": "무적",
    "invuln": "무적", "iron": "강철", "jackpot": "잭팟", "kill": "처치",
    "kills": "처치", "knockdown": "넉다운", "large": "대형", "level": "레벨",
    "life": "생명", "limit": "한도", "linger": "잔류", "lingering": "잔류",
    "lz": "대형 제드", "machine": "머신", "mag": "탄창", "magazine": "탄창",
    "magnet": "자석", "mark": "표식", "mastery": "숙련도", "max": "최대",
    "medicine": "의술", "melee": "근접", "milestone": "마일스톤",
    "min": "최소", "miracle": "기적", "mod": "배율", "mode": "모드",
    "molten": "용융", "momentum": "탄력", "move": "이동", "movement": "이동",
    "mult": "배율", "multiplier": "배율", "name": "이름", "nearby": "근처",
    "network": "네트워크", "neural": "신경", "of": "", "offense": "공격",
    "on": "", "over": "", "pandemic": "전염병", "passive": "패시브",
    "penalty": "페널티", "penetration": "관통력", "per": "당",
    "percent": "퍼센트", "percentage": "퍼센트", "perfect": "완벽한",
    "perk": "퍼크", "permanent": "영구", "petrify": "석화", "phoenix": "불사조",
    "poison": "독", "power": "위력", "preserve": "보존", "probability": "확률",
    "proximity": "근접도", "pulse": "파동", "purchase": "구매", "radius": "범위",
    "range": "사거리", "rapid": "연속", "rate": "속도", "ratio": "비율",
    "readiness": "준비태세", "received": "받는", "recharge": "재충전",
    "recoil": "반동", "recovery": "회복", "reduction": "감소", "reflect": "반사",
    "reflection": "반사", "reforge": "재련", "refund": "환급", "regen": "재생",
    "reload": "재장전", "required": "필요", "residual": "잔여", "resist": "저항",
    "resistance": "저항력", "resonance": "공명", "restore": "복구",
    "reward": "보상", "rifle": "소총", "riot": "리어트", "roll": "굴림",
    "round": "라운드", "scavenge": "노획", "scavenging": "노획",
    "second": "초", "self": "자신", "set": "세트", "share": "공유",
    "shield": "보호막", "shot": "샷", "shots": "샷", "sight": "조준경",
    "single": "단일", "siphon": "흡수", "siphoned": "흡수된", "size": "크기",
    "slot": "슬롯", "slots": "슬롯", "snare": "속박", "soulbound": "영혼귀속",
    "spare": "여분", "special": "특수", "speed": "속도", "spending": "소비",
    "spread": "탄퍼짐", "sprint": "질주", "sq": "제곱", "stack": "스택",
    "stacks": "스택", "stage": "단계", "stalk": "추적", "stalker": "스토커",
    "stat": "능력치", "stationary": "정지", "steal": "흡수", "stipend": "지원금",
    "stopping": "제압", "stored": "저장된", "strike": "타격", "stumble": "휘청임",
    "stun": "기절", "supplier": "보급", "survival": "생존", "swarm": "무리",
    "switch": "전환", "symbiote": "공생체", "sync": "동기화", "t": "",
    "taken": "받는", "takeover": "장악", "target": "대상", "tax": "세금",
    "team": "팀", "teammate": "팀원", "tempo": "템포", "threshold": "임계값",
    "tick": "틱", "time": "시간", "to": "", "total": "총",
    "touch": "손길", "toxic": "독성", "transform": "변신", "trigger": "발동",
    "trophy": "트로피", "twin": "쌍둥이", "type": "종류", "utility": "유틸리티",
    "vampire": "흡혈", "venom": "맹독", "wave": "웨이브", "weap": "무기",
    "weapon": "무기", "weight": "중량", "window": "시간창", "zed": "제드",
}

# key (as-is, case sensitive) -> full hand-picked label, takes priority over
# the automatic tokenizer for names that would otherwise read awkwardly.
OVERRIDES = {
    "Cfg_Damage": "피해량", "Cfg_ReloadRate": "재장전 속도", "Cfg_DamageHead": "헤드샷 피해량",
    "Cfg_LZDamage": "대형 제드 피해량", "Cfg_GrenadeDamage": "수류탄 피해량", "Cfg_HealRate": "치유 속도",
    "Cfg_Health": "체력", "Cfg_Defense": "저항력", "Cfg_Ammo": "탄약", "Cfg_MoveSpeed": "이동 속도",
    "Cfg_SwitchSpeed": "무기 전환 속도", "Cfg_Armor": "방어구", "Cfg_MagSize": "탄창 크기",
    "Cfg_Recoil": "반동", "Cfg_SpareAmmo": "여분 탄약", "Cfg_StoppingPower": "제압력",
    "Cfg_Penetration": "관통력", "Cfg_AttackSpeed": "공격 속도",
    "Damage": "피해량", "Health": "체력", "Armor": "방어구", "Resistance": "저항력",
    "Chance": "발동 확률", "Duration": "지속시간", "Radius": "범위", "Range": "사거리",
    "MaxStacks": "최대 스택 수", "MovementSpeed": "이동 속도", "ReloadSpeed": "재장전 속도",
    "ReloadRate": "재장전 속도", "FireRate": "연사 속도", "RateOfFire": "연사 속도",
    "Penetration": "관통력", "Recoil": "반동", "Spread": "탄퍼짐", "MagSize": "탄창 크기",
    "SpareAmmo": "여분 탄약", "HeadshotDamage": "헤드샷 피해량", "BossDamage": "보스 피해량",
    "GrenadeDamage": "수류탄 피해량", "Dosh": "도쉬", "DoshPerKill": "처치당 도쉬",
    "HealAmount": "치유량", "HealPercent": "치유량 비율", "ExtraSlots": "추가 슬롯",
    "WeaponSwitchBonus": "무기 전환 속도 보너스", "WeaponSwitchSpeed": "무기 전환 속도",
    "ZedTimeExtension": "ZED타임 연장", "KillThreshold": "필요 처치 수",
    "StackDuration": "스택 지속시간", "BuffDuration": "버프 지속시간",
    "FieldMedicine": "야전 의술", "RateOfFire": "연사 속도", "RateOfFireBonus": "연사 속도 보너스",
    "RateOfFireInv": "연사 속도", "FuryModeRateOfFireMult": "분노 모드 연사 속도 배율",
    "DamageOverTime": "지속 피해량",
}

# key -> forced unit classification, for the handful of names where the
# generic token heuristics get the wrong answer (see comments at each use).
FORCE_UNIT = {
    "DamageOverTime": "percent",  # "damage OVER TIME" is a DoT multiplier, not a duration
    "RiotLinger": "seconds",  # how long the lingering effect lasts, in seconds
    # Shapeshifter's PolymorphicSynthesis: flat penetration points per active
    # utility buff (+1/+2), not a percentage -- "penetration" is a PERCENT_HINT
    # and both values are small integers (<=3), so the generic heuristic
    # misreads this as "+100%"/"+200%".
    "PenetrationPerUtilityBuff": "count",
}

# lowercased tokens that indicate the raw value is a ratio/bonus that should
# render as a percentage (e.g. 0.05 -> "+5%").
PERCENT_HINTS = {
    "damage", "bonus", "chance", "probability", "percent", "percentage",
    "resistance", "reduction", "rate", "speed", "boost", "penalty",
    "penetration", "recoil", "spread", "snare", "stun", "knockdown",
    "stumble", "healrate", "healing", "healpercent", "conversion",
    "factor", "ratio", "amplification", "haste", "inc", "increase",
    "cutting", "discount", "refund", "interest", "readiness",
}
# tokens that mean "count this many times / this many units", not a percent
COUNT_HINTS = {
    "stacks", "stack", "threshold", "slots", "slot", "count", "shots",
    "kills", "kill", "hits", "required", "milestone", "stage", "set",
    "type", "category",
}
SECONDS_HINTS = {"duration", "durations", "cooldown", "interval", "window", "time", "ext", "extension", "recharge"}
# words that are unambiguously a ratio no matter what else is in the key name
# (e.g. "ZedTimeDR" is a % damage reduction, not a duration, despite "Time").
STRONG_PERCENT_HINTS = {"chance", "probability", "dr", "resistance", "reduction", "amplification", "percentage"}
CURRENCY_HINTS = {"dosh"}
DISTANCE_HINTS = {"radius", "range"}
MULTIPLIER_HINTS = {"mult", "multiplier", "mod"}

TOKEN_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")

# Multi-token idioms that must not be translated word-by-word: "Fire" + "Rate"
# means "rate of fire" (연사 속도), not "fire's speed" (화염 속도). Checked as
# a sliding window over the lowercased token list; first match wins.
PHRASES = [
    (("rate", "of", "fire"), "연사 속도"),
    (("fire", "rate"), "연사 속도"),
]


def tokenize(key):
    key = key.replace("Cfg_", "")
    return TOKEN_RE.findall(key)


def _merge_phrases(tokens):
    """Replace known multi-token idioms with a single pre-translated chunk."""
    lower = [t.lower() for t in tokens]
    out_tokens, out_words = [], []
    i = 0
    while i < len(tokens):
        matched = False
        for phrase, translation in PHRASES:
            n = len(phrase)
            if tuple(lower[i:i + n]) == phrase:
                out_tokens.append(None)
                out_words.append(translation)
                i += n
                matched = True
                break
        if not matched:
            out_tokens.append(tokens[i])
            out_words.append(WORD_MAP.get(lower[i], tokens[i]))
            i += 1
    return out_tokens, out_words


def translate_key(key):
    if key in OVERRIDES:
        return OVERRIDES[key]
    tokens = tokenize(key)
    tokens, words = _merge_phrases(tokens)

    # "PerX" -> "X당" reordering (e.g. Level, Stack, BurningEnemy, Milestone)
    out = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok is not None and tok.lower() == "per":
            rest = [w for w in words[i + 1:] if w]
            out = rest + ["당"] + out
            break
        out.append(words[i])
        i += 1
    result = " ".join([w for w in out if w]).strip()
    return result or key


def classify_unit_group(key, values):
    """Classify a key's unit using ALL of its sibling values within the same
    perk/skill (its T1/T2 pair, typically). The same key name (e.g. "ArmorBonus")
    is reused across different skills for different things (a flat armor grant
    in one, a % bonus in another) so looking at just one skill's own pair -
    rather than the value in isolation, or all 300 skills at once - is what
    actually disambiguates it: a skill whose pair is (10, 20) is obviously a
    flat amount, while a pair of (0.1, 0.25) is obviously a ratio.
    """
    if key in FORCE_UNIT:
        return FORCE_UNIT[key]

    tokens = [t.lower() for t in tokenize(key)]
    tokenset = set(tokens)
    nums = [v for v in values if isinstance(v, (int, float))]
    has_decimal = any(not float(v).is_integer() for v in nums)

    # A probability/DR/resistance/etc is always a ratio -- never seconds,
    # currency, or a flat count -- so these must win over every other
    # keyword (e.g. "HeadshotExtensionChance" contains both "Extension"
    # (seconds) and "Chance" (percent); Chance wins. "ZedTimeDR" contains
    # "Time" (seconds) and "DR" (percent); DR wins).
    if tokenset & STRONG_PERCENT_HINTS:
        return "percent"
    if tokenset & CURRENCY_HINTS:
        # A decimal "dosh" value is a conversion RATIO ("DoshConversion=0.25"
        # meaning 25%), not a currency amount -- real dosh amounts are ints.
        return "percent" if has_decimal else "currency"
    if tokenset & MULTIPLIER_HINTS:
        return "multiplier"
    if tokenset & DISTANCE_HINTS:
        # Real distances in this dataset are always in the hundreds+ (Unreal
        # Units). A small "Range"/"Radius" value (e.g. CloakRange=0.5/1.5) is
        # actually a ratio bonus that happens to share the word "range".
        if max((abs(v) for v in nums), default=0) >= 50:
            return "distance"
    if tokenset & SECONDS_HINTS:
        return "seconds"

    # Ambiguous categories (e.g. "HealthThreshold" can be a flat HP amount
    # like 50, or a HP% like 0.3): a fractional value is the strongest signal
    # that this particular skill's instance is a ratio, regardless of keyword.
    if has_decimal:
        return "percent"
    if tokenset & COUNT_HINTS:
        return "count"
    if tokenset & PERCENT_HINTS:
        mx = max((abs(v) for v in nums), default=0)
        if mx <= 3:
            return "percent"
    return "count"


def classify_unit(key):
    return classify_unit_group(key, [])


def format_value_as(value, unit):
    if not isinstance(value, (int, float)):
        return str(value)
    if unit == "percent":
        pct = value * 100
        # Two decimals, not one: after the 2026-07-02 global passive halving
        # many real ini values land on quarter-percent steps (0.0075 →
        # +0.75%, 0.0025 → +0.25%) and one-decimal rounding displayed them
        # as +0.8%/+0.2% -- a wiki whose whole point is exact ini numbers
        # shouldn't round them.
        s = f"{pct:.2f}".rstrip("0").rstrip(".")
        sign = "+" if value >= 0 else ""
        return f"{sign}{s}%"
    if unit == "multiplier":
        s = f"{value:.2f}".rstrip("0").rstrip(".")
        return f"×{s}"
    if unit == "seconds":
        s = f"{value:.2f}".rstrip("0").rstrip(".")
        return f"{s}초"
    if unit == "currency":
        return f"{value:,.0f} 도쉬"
    # distance / count / flat -- preserve decimals, just format nicely
    if isinstance(value, int) or float(value).is_integer():
        return f"{int(value):,}"
    s = f"{value:.2f}".rstrip("0").rstrip(".")
    return s


def format_value(key, value):
    """Single-value formatting fallback (no siblings to compare against)."""
    unit = classify_unit_group(key, [value])
    return format_value_as(value, unit)


def format_value_group(key, values):
    """Format every value in `values` (the T1/T2/etc siblings of one key
    within a single perk/skill) using one shared unit classification."""
    unit = classify_unit_group(key, values)
    return [format_value_as(v, unit) for v in values]


def label_and_format(key, value):
    return translate_key(key), format_value(key, value)
