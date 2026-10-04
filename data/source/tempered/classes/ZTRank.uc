// ===================================================================
// ZTRank - Rank system data and calculations
// 100 ranks across 100 tiers; each new rank compresses five legacy ranks
// New XP threshold = former curve at rank (5 * R), divided by 5
//   Rank 100 ~3.13M compressed XP (one fifth of the former rank-500 cap)
// ===================================================================
class ZTRank extends Object;

const MAX_RANK = 100;
const RANKS_PER_TIER = 1;
const NUM_TIERS = 100;
const LEGACY_RANKS_PER_LEVEL = 5;

// XP sources
const XP_TRASH_ZED = 1;
const XP_MEDIUM_ZED = 3;
const XP_LARGE_ZED = 10;
const XP_BOSS = 75;
const XP_WAVE_CLEAR = 25;

// ===================================================================
// LOCALIZED TIER NAMES (Phase 4)
//
// One var per tier (100 tiers). The English defaults below mirror the
// hardcoded asset-name strings returned by GetTierAssetName(). On a
// non-INT client these auto-load from [ZTRank] in the active locale
// file (UE3's `localized` keyword); they are read via `default.TierName_X`
// inside the static GetTierDisplayName() switch.
//
// The PARALLEL English strings in GetTierAssetName() are kept because
// they form part of the rank icon asset path:
//   ZedternalRBPerkpackage_Resources.Rank.UI_Rank_Tier_<EnglishName>
// Localizing the asset name would break icon loading on non-INT clients.
// ===================================================================
var localized string TierName_0;   // Rookie
var localized string TierName_1;   // Soldier
var localized string TierName_2;   // Veteran
var localized string TierName_3;   // Specialist
var localized string TierName_4;   // Elite
var localized string TierName_5;   // Commander
var localized string TierName_6;   // Warlord
var localized string TierName_7;   // Champion
var localized string TierName_8;   // Mythic
var localized string TierName_9;   // Eternal
var localized string TierName_10;  // Enforcer
var localized string TierName_11;  // Sentinel
var localized string TierName_12;  // Vanguard
var localized string TierName_13;  // Tactician
var localized string TierName_14;  // Operative
var localized string TierName_15;  // Recon
var localized string TierName_16;  // Juggernaut
var localized string TierName_17;  // Commando
var localized string TierName_18;  // Marshal
var localized string TierName_19;  // Ironwolf
var localized string TierName_20;  // Gladiator
var localized string TierName_21;  // Centurion
var localized string TierName_22;  // Crusader
var localized string TierName_23;  // Samurai
var localized string TierName_24;  // Viking
var localized string TierName_25;  // Spartan
var localized string TierName_26;  // Ronin
var localized string TierName_27;  // Berserker
var localized string TierName_28;  // Paladin
var localized string TierName_29;  // Conqueror
var localized string TierName_30;  // Phoenix
var localized string TierName_31;  // Dragon
var localized string TierName_32;  // Leviathan
var localized string TierName_33;  // Hydra
var localized string TierName_34;  // Cerberus
var localized string TierName_35;  // Valkyrie
var localized string TierName_36;  // Minotaur
var localized string TierName_37;  // Chimera
var localized string TierName_38;  // Kraken
var localized string TierName_39;  // Titan
var localized string TierName_40;  // Inferno
var localized string TierName_41;  // Tempest
var localized string TierName_42;  // Avalanche
var localized string TierName_43;  // Earthquake
var localized string TierName_44;  // Typhoon
var localized string TierName_45;  // Volcano
var localized string TierName_46;  // Lightning
var localized string TierName_47;  // Glacier
var localized string TierName_48;  // Sandstorm
var localized string TierName_49;  // Maelstrom
var localized string TierName_50;  // Nebula
var localized string TierName_51;  // Pulsar
var localized string TierName_52;  // Supernova
var localized string TierName_53;  // Blackhole
var localized string TierName_54;  // Quasar
var localized string TierName_55;  // Comet
var localized string TierName_56;  // Eclipse
var localized string TierName_57;  // Singularity
var localized string TierName_58;  // Stardust
var localized string TierName_59;  // Astral
var localized string TierName_60;  // Ancient
var localized string TierName_61;  // Primeval
var localized string TierName_62;  // Fossil
var localized string TierName_63;  // Monolith
var localized string TierName_64;  // Relic
var localized string TierName_65;  // Epoch
var localized string TierName_66;  // Primal
var localized string TierName_67;  // Archaic
var localized string TierName_68;  // Ancestor
var localized string TierName_69;  // Genesis
var localized string TierName_70;  // Ascendant
var localized string TierName_71;  // Ethereal
var localized string TierName_72;  // Celestial
var localized string TierName_73;  // Seraph
var localized string TierName_74;  // Oracle
var localized string TierName_75;  // Harbinger
var localized string TierName_76;  // Prophet
var localized string TierName_77;  // Sovereign
var localized string TierName_78;  // Immortal
var localized string TierName_79;  // Paragon
var localized string TierName_80;  // Demiurge
var localized string TierName_81;  // Archon
var localized string TierName_82;  // Empyrean
var localized string TierName_83;  // Apex
var localized string TierName_84;  // Omega
var localized string TierName_85;  // Oblivion
var localized string TierName_86;  // Exalted
var localized string TierName_87;  // Godslayer
var localized string TierName_88;  // Absolute
var localized string TierName_89;  // Infinite
var localized string TierName_90;  // Overlord
var localized string TierName_91;  // Cataclysm
var localized string TierName_92;  // Abyss
var localized string TierName_93;  // Annihilation
var localized string TierName_94;  // Ragnarok
var localized string TierName_95;  // Armageddon
var localized string TierName_96;  // Zenith
var localized string TierName_97;  // Apotheosis
var localized string TierName_98;  // Omnipotent
var localized string TierName_99;  // Zedternal

// ===================================================================
// XP CALCULATION
// ===================================================================

// Cumulative XP to reach a given rank (1-100). Every new rank spans five
// legacy ranks, while XP is divided by five to compress the total grind.
static function int GetCumulativeXPForRank(int Rank)
{
    local int LegacyRank;
    if (Rank <= 0) return 0;
    if (Rank > MAX_RANK) Rank = MAX_RANK;
    LegacyRank = Rank * LEGACY_RANKS_PER_LEVEL;
    return (LegacyRank * (125 + 75 * LegacyRank + (LegacyRank * LegacyRank) / 10)) / (2 * LEGACY_RANKS_PER_LEVEL);
}

// Convert XP stored by the previous 500-rank scale into the compressed scale.
static function int ConvertLegacyXP(int LegacyXP)
{
    return Min(Max(LegacyXP, 0) / LEGACY_RANKS_PER_LEVEL, GetCumulativeXPForRank(MAX_RANK));
}

// XP required for a single rank level (not cumulative)
static function int GetXPForSingleRank(int Rank)
{
    if (Rank <= 1) return GetCumulativeXPForRank(1);
    if (Rank > MAX_RANK) Rank = MAX_RANK;
    return GetCumulativeXPForRank(Rank) - GetCumulativeXPForRank(Rank - 1);
}

// Convert total XP to rank level (0 = unranked, 1-100)
static function int GetRankFromXP(int TotalXP)
{
    local int Lo, Hi, Mid, MidXP;

    if (TotalXP <= 0) return 0;
    if (TotalXP >= GetCumulativeXPForRank(MAX_RANK)) return MAX_RANK;

    // Binary search for O(log N) instead of O(N)
    Lo = 1;
    Hi = MAX_RANK;
    while (Lo <= Hi)
    {
        Mid = (Lo + Hi) / 2;
        MidXP = GetCumulativeXPForRank(Mid);
        if (TotalXP < MidXP)
            Hi = Mid - 1;
        else if (TotalXP >= GetCumulativeXPForRank(Mid + 1))
            Lo = Mid + 1;
        else
            return Mid;
    }
    return Hi;
}

// XP progress within current rank (0.0 to 1.0)
static function float GetRankProgress(int TotalXP)
{
    local int CurrentRank, XPAtCurrent, XPAtNext;

    CurrentRank = GetRankFromXP(TotalXP);
    if (CurrentRank >= MAX_RANK) return 1.0f;

    if (CurrentRank > 0)
        XPAtCurrent = GetCumulativeXPForRank(CurrentRank);
    else
        XPAtCurrent = 0;
    XPAtNext = GetCumulativeXPForRank(CurrentRank + 1);

    if (XPAtNext <= XPAtCurrent) return 1.0f;
    return FClamp(float(TotalXP - XPAtCurrent) / float(XPAtNext - XPAtCurrent), 0.0f, 1.0f);
}

// ===================================================================
// TIER CONVERSION
// ===================================================================

static function int GetTierFromRank(int Rank)
{
    if (Rank <= 0) return 0;
    return Min((Rank - 1) / RANKS_PER_TIER, NUM_TIERS - 1);
}

// ===================================================================
// TIER NAMES (100 unique tiers)
//
// Two parallel functions (Phase 4):
//   GetTierAssetName  -> English string used to build the icon asset path.
//                        MUST stay English on all clients or icon loads break.
//   GetTierDisplayName -> localized string used for HUD display, popups,
//                        and debug command output. Reads from `default.TierName_X`
//                        which UE3 auto-loads from [ZTRank] in the active locale.
// ===================================================================

static function string GetTierAssetName(int Rank)
{
    switch (GetTierFromRank(Rank))
    {
    // Phase 1: Military (Ranks 1-10)
    case 0: return "Rookie";
    case 1: return "Soldier";
    case 2: return "Veteran";
    case 3: return "Specialist";
    case 4: return "Elite";
    case 5: return "Commander";
    case 6: return "Warlord";
    case 7: return "Champion";
    case 8: return "Mythic";
    case 9: return "Eternal";
    // Phase 2: Special Operations (Ranks 11-20)
    case 10: return "Enforcer";
    case 11: return "Sentinel";
    case 12: return "Vanguard";
    case 13: return "Tactician";
    case 14: return "Operative";
    case 15: return "Recon";
    case 16: return "Juggernaut";
    case 17: return "Commando";
    case 18: return "Marshal";
    case 19: return "Ironwolf";
    // Phase 3: Legendary Warriors (Ranks 21-30)
    case 20: return "Gladiator";
    case 21: return "Centurion";
    case 22: return "Crusader";
    case 23: return "Samurai";
    case 24: return "Viking";
    case 25: return "Spartan";
    case 26: return "Ronin";
    case 27: return "Berserker";
    case 28: return "Paladin";
    case 29: return "Conqueror";
    // Phase 4: Mythological (Ranks 31-40)
    case 30: return "Phoenix";
    case 31: return "Dragon";
    case 32: return "Leviathan";
    case 33: return "Hydra";
    case 34: return "Cerberus";
    case 35: return "Valkyrie";
    case 36: return "Minotaur";
    case 37: return "Chimera";
    case 38: return "Kraken";
    case 39: return "Titan";
    // Phase 5: Elemental (Ranks 41-50)
    case 40: return "Inferno";
    case 41: return "Tempest";
    case 42: return "Avalanche";
    case 43: return "Earthquake";
    case 44: return "Typhoon";
    case 45: return "Volcano";
    case 46: return "Lightning";
    case 47: return "Glacier";
    case 48: return "Sandstorm";
    case 49: return "Maelstrom";
    // Phase 6: Cosmic (Ranks 51-60)
    case 50: return "Nebula";
    case 51: return "Pulsar";
    case 52: return "Supernova";
    case 53: return "Blackhole";
    case 54: return "Quasar";
    case 55: return "Comet";
    case 56: return "Eclipse";
    case 57: return "Singularity";
    case 58: return "Stardust";
    case 59: return "Astral";
    // Phase 7: Primordial (Ranks 61-70)
    case 60: return "Ancient";
    case 61: return "Primeval";
    case 62: return "Fossil";
    case 63: return "Monolith";
    case 64: return "Relic";
    case 65: return "Epoch";
    case 66: return "Primal";
    case 67: return "Archaic";
    case 68: return "Ancestor";
    case 69: return "Genesis";
    // Phase 8: Transcendent (Ranks 71-80)
    case 70: return "Ascendant";
    case 71: return "Ethereal";
    case 72: return "Celestial";
    case 73: return "Seraph";
    case 74: return "Oracle";
    case 75: return "Harbinger";
    case 76: return "Prophet";
    case 77: return "Sovereign";
    case 78: return "Immortal";
    case 79: return "Paragon";
    // Phase 9: Godlike (Ranks 81-90)
    case 80: return "Demiurge";
    case 81: return "Archon";
    case 82: return "Empyrean";
    case 83: return "Apex";
    case 84: return "Omega";
    case 85: return "Oblivion";
    case 86: return "Exalted";
    case 87: return "Godslayer";
    case 88: return "Absolute";
    case 89: return "Infinite";
    // Phase 10: Ultimate (Ranks 91-100)
    case 90: return "Overlord";
    case 91: return "Cataclysm";
    case 92: return "Abyss";
    case 93: return "Annihilation";
    case 94: return "Ragnarok";
    case 95: return "Armageddon";
    case 96: return "Zenith";
    case 97: return "Apotheosis";
    case 98: return "Omnipotent";
    case 99: return "Zedternal";
    }
    return "Unknown";
}

// Localized version of GetTierAssetName. Use everywhere a player will SEE
// the tier name (HUD, scoreboard, popups, debug commands). The asset name
// version above is for internal asset lookup only.
static function string GetTierDisplayName(int Rank)
{
    switch (GetTierFromRank(Rank))
    {
    case 0:  return default.TierName_0;
    case 1:  return default.TierName_1;
    case 2:  return default.TierName_2;
    case 3:  return default.TierName_3;
    case 4:  return default.TierName_4;
    case 5:  return default.TierName_5;
    case 6:  return default.TierName_6;
    case 7:  return default.TierName_7;
    case 8:  return default.TierName_8;
    case 9:  return default.TierName_9;
    case 10: return default.TierName_10;
    case 11: return default.TierName_11;
    case 12: return default.TierName_12;
    case 13: return default.TierName_13;
    case 14: return default.TierName_14;
    case 15: return default.TierName_15;
    case 16: return default.TierName_16;
    case 17: return default.TierName_17;
    case 18: return default.TierName_18;
    case 19: return default.TierName_19;
    case 20: return default.TierName_20;
    case 21: return default.TierName_21;
    case 22: return default.TierName_22;
    case 23: return default.TierName_23;
    case 24: return default.TierName_24;
    case 25: return default.TierName_25;
    case 26: return default.TierName_26;
    case 27: return default.TierName_27;
    case 28: return default.TierName_28;
    case 29: return default.TierName_29;
    case 30: return default.TierName_30;
    case 31: return default.TierName_31;
    case 32: return default.TierName_32;
    case 33: return default.TierName_33;
    case 34: return default.TierName_34;
    case 35: return default.TierName_35;
    case 36: return default.TierName_36;
    case 37: return default.TierName_37;
    case 38: return default.TierName_38;
    case 39: return default.TierName_39;
    case 40: return default.TierName_40;
    case 41: return default.TierName_41;
    case 42: return default.TierName_42;
    case 43: return default.TierName_43;
    case 44: return default.TierName_44;
    case 45: return default.TierName_45;
    case 46: return default.TierName_46;
    case 47: return default.TierName_47;
    case 48: return default.TierName_48;
    case 49: return default.TierName_49;
    case 50: return default.TierName_50;
    case 51: return default.TierName_51;
    case 52: return default.TierName_52;
    case 53: return default.TierName_53;
    case 54: return default.TierName_54;
    case 55: return default.TierName_55;
    case 56: return default.TierName_56;
    case 57: return default.TierName_57;
    case 58: return default.TierName_58;
    case 59: return default.TierName_59;
    case 60: return default.TierName_60;
    case 61: return default.TierName_61;
    case 62: return default.TierName_62;
    case 63: return default.TierName_63;
    case 64: return default.TierName_64;
    case 65: return default.TierName_65;
    case 66: return default.TierName_66;
    case 67: return default.TierName_67;
    case 68: return default.TierName_68;
    case 69: return default.TierName_69;
    case 70: return default.TierName_70;
    case 71: return default.TierName_71;
    case 72: return default.TierName_72;
    case 73: return default.TierName_73;
    case 74: return default.TierName_74;
    case 75: return default.TierName_75;
    case 76: return default.TierName_76;
    case 77: return default.TierName_77;
    case 78: return default.TierName_78;
    case 79: return default.TierName_79;
    case 80: return default.TierName_80;
    case 81: return default.TierName_81;
    case 82: return default.TierName_82;
    case 83: return default.TierName_83;
    case 84: return default.TierName_84;
    case 85: return default.TierName_85;
    case 86: return default.TierName_86;
    case 87: return default.TierName_87;
    case 88: return default.TierName_88;
    case 89: return default.TierName_89;
    case 90: return default.TierName_90;
    case 91: return default.TierName_91;
    case 92: return default.TierName_92;
    case 93: return default.TierName_93;
    case 94: return default.TierName_94;
    case 95: return default.TierName_95;
    case 96: return default.TierName_96;
    case 97: return default.TierName_97;
    case 98: return default.TierName_98;
    case 99: return default.TierName_99;
    }
    return "Unknown";
}

// ===================================================================
// TIER COLORS
// ===================================================================

static function Color GetTierColor(int Rank)
{
    local Color C;
    C.A = 255;

    switch (GetTierFromRank(Rank))
    {
    // Phase 1: Military
    case 0: C.R=153; C.G=153; C.B=153; break; // Rookie - Gray
    case 1: C.R=204; C.G=204; C.B=204; break; // Soldier - Silver
    case 2: C.R=66; C.G=224; C.B=135; break;  // Veteran - Green
    case 3: C.R=21; C.G=215; C.B=250; break;  // Specialist - Cyan
    case 4: C.R=59; C.G=130; C.B=246; break;  // Elite - Blue
    case 5: C.R=179; C.G=70; C.B=234; break;  // Commander - Purple
    case 6: C.R=232; C.G=64; C.B=64; break;   // Warlord - Red
    case 7: C.R=245; C.G=158; C.B=11; break;  // Champion - Orange
    case 8: C.R=255; C.G=215; C.B=0; break;   // Mythic - Gold
    case 9: C.R=255; C.G=244; C.B=204; break; // Eternal - Cream
    // Phase 2: Special Operations
    case 10: C.R=100; C.G=140; C.B=180; break; // Enforcer - Steel Blue
    case 11: C.R=0; C.G=160; C.B=140; break;   // Sentinel - Dark Teal
    case 12: C.R=34; C.G=140; C.B=60; break;   // Vanguard - Forest Green
    case 13: C.R=40; C.G=70; C.B=160; break;   // Tactician - Navy
    case 14: C.R=0; C.G=180; C.B=200; break;   // Operative - Dark Cyan
    case 15: C.R=85; C.G=120; C.B=50; break;   // Recon - Olive
    case 16: C.R=120; C.G=120; C.B=130; break; // Juggernaut - Gunmetal
    case 17: C.R=185; C.G=170; C.B=125; break; // Commando - Khaki
    case 18: C.R=190; C.G=35; C.B=35; break;   // Marshal - Blood Red
    case 19: C.R=170; C.G=180; C.B=195; break; // Ironwolf - Cold Silver
    // Phase 3: Legendary Warriors
    case 20: C.R=205; C.G=127; C.B=50; break;  // Gladiator - Bronze
    case 21: C.R=200; C.G=60; C.B=55; break;   // Centurion - Roman Red
    case 22: C.R=215; C.G=215; C.B=235; break; // Crusader - Silver White
    case 23: C.R=200; C.G=35; C.B=60; break;   // Samurai - Crimson
    case 24: C.R=130; C.G=185; C.B=235; break; // Viking - Ice Blue
    case 25: C.R=185; C.G=65; C.B=45; break;   // Spartan - Spartan Red
    case 26: C.R=125; C.G=65; C.B=165; break;  // Ronin - Dark Purple
    case 27: C.R=210; C.G=25; C.B=25; break;   // Berserker - Blood
    case 28: C.R=235; C.G=215; C.B=145; break; // Paladin - Holy Gold
    case 29: C.R=145; C.G=55; C.B=185; break;  // Conqueror - Imperial Purple
    // Phase 4: Mythological
    case 30: C.R=255; C.G=105; C.B=35; break;  // Phoenix - Fire Orange
    case 31: C.R=35; C.G=185; C.B=65; break;   // Dragon - Emerald
    case 32: C.R=25; C.G=85; C.B=170; break;   // Leviathan - Deep Ocean
    case 33: C.R=85; C.G=210; C.B=65; break;   // Hydra - Toxic Green
    case 34: C.R=210; C.G=45; C.B=45; break;   // Cerberus - Hellfire Red
    case 35: C.R=165; C.G=205; C.B=245; break; // Valkyrie - Arctic Blue
    case 36: C.R=165; C.G=115; C.B=55; break;  // Minotaur - Bronze Brown
    case 37: C.R=205; C.G=105; C.B=185; break; // Chimera - Magenta
    case 38: C.R=85; C.G=45; C.B=145; break;   // Kraken - Deep Purple
    case 39: C.R=215; C.G=185; C.B=65; break;  // Titan - Ancient Gold
    // Phase 5: Elemental
    case 40: C.R=255; C.G=85; C.B=5; break;    // Inferno - Flame
    case 41: C.R=55; C.G=125; C.B=210; break;  // Tempest - Storm Blue
    case 42: C.R=225; C.G=240; C.B=255; break; // Avalanche - Ice White
    case 43: C.R=145; C.G=105; C.B=55; break;  // Earthquake - Earth Brown
    case 44: C.R=5; C.G=145; C.B=165; break;   // Typhoon - Dark Teal
    case 45: C.R=235; C.G=65; C.B=25; break;   // Volcano - Magma Red
    case 46: C.R=255; C.G=245; C.B=55; break;  // Lightning - Electric Yellow
    case 47: C.R=105; C.G=185; C.B=235; break; // Glacier - Frost Blue
    case 48: C.R=215; C.G=185; C.B=105; break; // Sandstorm - Desert Gold
    case 49: C.R=155; C.G=55; C.B=205; break;  // Maelstrom - Chaotic Purple
    // Phase 6: Cosmic
    case 50: C.R=205; C.G=85; C.B=185; break;  // Nebula - Pink Purple
    case 51: C.R=65; C.G=165; C.B=255; break;  // Pulsar - Electric Blue
    case 52: C.R=255; C.G=205; C.B=85; break;  // Supernova - Bright Orange
    case 53: C.R=125; C.G=65; C.B=165; break;  // Blackhole - Deep Violet
    case 54: C.R=185; C.G=225; C.B=255; break; // Quasar - Brilliant Blue
    case 55: C.R=85; C.G=225; C.B=235; break;  // Comet - Cyan Trail
    case 56: C.R=205; C.G=175; C.B=65; break;  // Eclipse - Dark Gold
    case 57: C.R=185; C.G=145; C.B=225; break; // Singularity - Light Purple
    case 58: C.R=205; C.G=215; C.B=235; break; // Stardust - Sparkle Silver
    case 59: C.R=85; C.G=125; C.B=205; break;  // Astral - Deep Space Blue
    // Phase 7: Primordial
    case 60: C.R=155; C.G=145; C.B=125; break; // Ancient - Weathered Stone
    case 61: C.R=65; C.G=145; C.B=65; break;   // Primeval - Moss
    case 62: C.R=205; C.G=165; C.B=85; break;  // Fossil - Amber
    case 63: C.R=105; C.G=105; C.B=115; break; // Monolith - Obsidian
    case 64: C.R=125; C.G=175; C.B=145; break; // Relic - Patina Copper
    case 65: C.R=185; C.G=145; C.B=65; break;  // Epoch - Deep Amber
    case 66: C.R=205; C.G=65; C.B=45; break;   // Primal - Savage Red
    case 67: C.R=185; C.G=165; C.B=105; break; // Archaic - Faded Gold
    case 68: C.R=225; C.G=215; C.B=195; break; // Ancestor - Bone White
    case 69: C.R=105; C.G=205; C.B=105; break; // Genesis - Creation Green
    // Phase 8: Transcendent
    case 70: C.R=245; C.G=205; C.B=85; break;  // Ascendant - Rising Gold
    case 71: C.R=145; C.G=185; C.B=245; break; // Ethereal - Translucent Blue
    case 72: C.R=235; C.G=235; C.B=255; break; // Celestial - Star White
    case 73: C.R=255; C.G=225; C.B=125; break; // Seraph - Holy Gold
    case 74: C.R=165; C.G=105; C.B=225; break; // Oracle - Mystical Purple
    case 75: C.R=165; C.G=85; C.B=85; break;   // Harbinger - Dark Omen
    case 76: C.R=245; C.G=235; C.B=185; break; // Prophet - Sacred Gold
    case 77: C.R=185; C.G=125; C.B=245; break; // Sovereign - Royal Purple
    case 78: C.R=245; C.G=245; C.B=255; break; // Immortal - Radiant White
    case 79: C.R=215; C.G=225; C.B=235; break; // Paragon - Platinum
    // Phase 9: Godlike
    case 80: C.R=85; C.G=145; C.B=245; break;  // Demiurge - Creation Blue
    case 81: C.R=255; C.G=215; C.B=65; break;  // Archon - Radiant Gold
    case 82: C.R=125; C.G=185; C.B=255; break; // Empyrean - Heavenly Blue
    case 83: C.R=225; C.G=55; C.B=55; break;   // Apex - Peak Crimson
    case 84: C.R=205; C.G=65; C.B=85; break;   // Omega - Final Red
    case 85: C.R=105; C.G=85; C.B=125; break;  // Oblivion - Void
    case 86: C.R=245; C.G=225; C.B=205; break; // Exalted - Warm White
    case 87: C.R=225; C.G=45; C.B=65; break;   // Godslayer - Divine Red
    case 88: C.R=255; C.G=245; C.B=225; break; // Absolute - Pure Energy
    case 89: C.R=205; C.G=185; C.B=245; break; // Infinite - Endless Purple
    // Phase 10: Ultimate
    case 90: C.R=185; C.G=45; C.B=45; break;   // Overlord - Dark Crimson
    case 91: C.R=245; C.G=65; C.B=25; break;   // Cataclysm - Destruction Red
    case 92: C.R=45; C.G=65; C.B=130; break;   // Abyss - Darkest Blue
    case 93: C.R=225; C.G=35; C.B=35; break;   // Annihilation - Pure Red
    case 94: C.R=235; C.G=185; C.B=55; break;  // Ragnarok - Norse Gold
    case 95: C.R=245; C.G=125; C.B=25; break;  // Armageddon - Apocalypse Orange
    case 96: C.R=255; C.G=250; C.B=225; break; // Zenith - Peak White Gold
    case 97: C.R=225; C.G=205; C.B=255; break; // Apotheosis - Divine Purple
    case 98: C.R=255; C.G=235; C.B=105; break; // Omnipotent - All Power Gold
    case 99: C.R=255; C.G=55; C.B=55; break;   // Zedternal - Signature Red
    }
    return C;
}

// ===================================================================
// TIER ICONS (loaded dynamically by naming convention)
// ===================================================================

// Icon naming convention: ZedternalRBPerkpackage_Resources.Rank.UI_Rank_Tier_<TierName>
// Missing icons gracefully return None (bMayFail=true)
static function Texture2D GetTierIcon(int Rank)
{
    local string TName, Path;

    TName = GetTierAssetName(Rank);
    if (TName == "" || TName == "Unknown")
        return None;

    Path = "ZedternalRBPerkpackage_Resources.Rank.UI_Rank_Tier_" $ TName;
    return Texture2D(DynamicLoadObject(Path, class'Texture2D', true));
}

// ===================================================================
// DISPLAY STRINGS
// ===================================================================

// Numeric level only; tier names are retained for rank icon asset lookup.
static function string GetRankTitle(int Rank)
{
    return string(Clamp(Rank, 0, MAX_RANK));
}

// e.g. "42" (for scoreboard/HUD/rank-up notifications)
static function string GetRankDisplayString(int Rank)
{
    return string(Clamp(Rank, 0, MAX_RANK));
}

// ===================================================================
// ZED XP CLASSIFICATION
// ===================================================================

static function int GetXPForZed(Pawn KilledPawn)
{
    if (KFPawn_ZedBloatKing(KilledPawn) != None) return XP_BOSS;
    if (KFPawn_ZedFleshpoundKing(KilledPawn) != None) return XP_BOSS;
    if (KFPawn_ZedHans(KilledPawn) != None) return XP_BOSS;
    if (KFPawn_ZedPatriarch(KilledPawn) != None) return XP_BOSS;
    if (KFPawn_ZedMatriarch(KilledPawn) != None) return XP_BOSS;
    if (KFPawn_Monster(KilledPawn) != None && KFPawn_Monster(KilledPawn).bLargeZed) return XP_LARGE_ZED;
    if (KFPawn_ZedHusk(KilledPawn) != None) return XP_MEDIUM_ZED;
    if (KFPawn_ZedSiren(KilledPawn) != None) return XP_MEDIUM_ZED;
    if (KFPawn_ZedBloat(KilledPawn) != None) return XP_MEDIUM_ZED;
    if (KFPawn_ZedDAR(KilledPawn) != None) return XP_MEDIUM_ZED;
    return XP_TRASH_ZED;
}

defaultproperties
{
    Name="Default__ZTRank"
}
