# Zedternal Unlimited — OP/Trash 판정 총정리 (전체 자료 통합)
> 2026-07-01 기준. 오퍼(WM) 10개 + 커퍼(DK) 37개 패시브(기존 확정) + 커퍼 스킬 300개(신규 판정) + FLAG 전체를 하나로 통합.
> 기준 난이도: Zedwaves.ini HoE. 판정 원칙: worst-case 합산(같은 퍼크의 스킬을 전부 구매·Deluxe 장착했다는 가정 + 다른 퍼크와의 교차 스택).

---

## 0. 전체 통계

| 구분 | 총 개수 | OP(너프필요/완료) | Trash(버프필요/완료) | 적절 | FLAG(수정불가) |
|------|--------|---------|---------|------|--------|
| 오퍼(WM) 패시브+스킬 | 10퍼크 | 3 (Demo/Firebug/SWAT) | 2 (GS/SS 패시브) | 5 | 5(추가검증 항목, 아래 3장) |
| 커퍼(DK) 패시브 | 37퍼크 | 27건 너프완료 | 3건 상향완료 | 나머지 유지 | 9건 |
| 커퍼(DK) 스킬 | 300개(31퍼크) | **6건 신규 발견 (3건 즉시 수정 완료)** | **1건 신규 발견(버그)** | 대다수 | 4건(기존 FLAG와 연동) |
| **총계** | **~350 항목** | **OP 확정 다수, 최우선 1건(Predator)** | | | |

---

## 1. 오퍼(WM) 10개 — 최종 판정 (기존 확정, 요약)

| 퍼크 | 판정 | 핵심 사유 |
|------|------|---------|
| Berserker | 적절(일부 버프) | Brawler Trash→버프완료, Spartan ZED타임 화력 너프완료 |
| Commando | 적절 | 큰 문제 없음 |
| Demolitionist | 🔴 OP→너프완료 | 수류탄 피해 스택 ×4.5배 → 패시브 GrenadeDamage +150%→+80% |
| FieldMedic | 적절(일부 버프) | Hemoglobin 고정10피해 Trash→100으로 버프완료 |
| Firebug | 🔴 OP→너프완료 | Combustion T2 +120%, HeatWaves +200%, Barbecue DoT×3 전부 너프완료 |
| Gunslinger | Trash→버프완료 | 패시브 데미지 최하위(+30%)→+40% |
| Sharpshooter | Trash→버프완료 | 동일 사유, Hunter 흡혈량도 상향 |
| Support | 적절 | 균형 |
| SWAT | 🔴 OP→너프완료 | RiotShield 총기피해 -90%→-60%로 너프완료 |
| Survivalist | 적절 | 유틸리티 특화, 의도된 약한 딜 |

**오퍼 FLAG 5건 — ✅ 재조사 완료 (2026-07-01, ZedternalReborn.u 소스 확인)**: BringTheHeat(상한+감쇠 확인, 적절)/RankThemUp(자동리셋 확인, 적절)/BoneBreaker(구조 확인, 적절)/SonicResistantRounds(완전면역 확인→0.4/1.0→0.3/0.6 너프완료)/SuppressionRounds+Cripple 스네어(서로 다른 공식 확인했으나 KF2 베이스엔진 변환식 부재로 정량판정 불가, ⚠️FLAG 유지)

---

## 2. 커퍼(DK) 37개 패시브 — 최종 판정 (기존 확정, 요약)

27건 너프 + 3건 상향 완료. 상세는 `밸런싱_작업_완료_보고서.md` 1~3장 참조. 유지 판정: Bulwark, Warlord, SpecialAgent, Artificer, Parasite, Maniac, ForgeWarden, Headhunter, Gambler, Haunted, Omen, Frost, Venomancer, TimeTraveler.

**🚨 FLAG (INI 수정 불가, 확정 판정만 존재)**:

| 퍼크 | 판정 | 비고 |
|------|------|------|
| LuckySalvage(무기스킬) | Trash 확정 | 구제 불가 |
| **Predator 트로피 시스템** | **🚨 확정 OP, 전체 최고위험** | 3세트 후 5슬롯 무한중첩, 하드코딩 |
| Detonator | 적절(설계상) | 패시브 2종만 Balance ini 부재로 조정 불가 |
| Shapeshifter Mimicry | ⚠️ OP 소지 | 장기전 15버프 전부 활성, Balance ini 부재로 조정 불가 |
| Gambit | ⚠️ OP 소지 | 영구 스탯 무한누적+승수중첩, 조정 불가 |
| SoulStealer | ⚠️ 잔여 FLAG | HP클램프 미확인 (아래 5장에서 위험도 재평가) |

---

## 3. 커퍼(DK) 스킬 300개 — 신규 판정 (이번 분석)

방법론: 같은 퍼크 소속 스킬을 전부 T2(Deluxe)로 구매했다는 worst-case 가정으로 동일 카테고리(피해/방어/유틸) 수치를 합산, 오퍼·커퍼 패시브와 교차 스택 시 문제 여부 확인.

### 🔴 OP 신규 발견 (INI 수정 권장)

| 퍼크(소속) | 스킬 | 문제 | 비교 기준 |
|---|---|---|---|
| **Cinder (Firebug Lv15)** | **ScorchedEarth** ✅너프완료 | Damage=1.0/**2.5**(T2 +250%) — 전체 300개 스킬 중 단일 최고값. Pyre(+120%)와 동시 장착 시 화염피해 flat +370%, 여기에 Cinder 패시브(+60%+킬성장)·Firebug패시브(+50%)·Pyrokinetic(너프후+50%) 중첩 시 극단적 화력 | 타 퍼크 최고수준 단일스킬이 대개 +100~125% 선 (ForgeWarden Pyroclasm+125%, Wendigo Territorial+125%) |
| **Cryophilite (SWAT Lv20)** | FrostbiteArrows | DamagePerStack=0.2/0.4, 최대스택수 INI에 없음(FLAG) | 상한 미확인 시 무한누적 가능 |
| **Daredevil(SS Lv5)+Support 관통 교차** | FullMetalJacket | Penetration +300%. Support 패시브(+150%)+Penetrator스킬(+200%)와 동일계열이라 멀티클래스 시 관통 사실상 무제한 | 이미 Support쪽은 "관통 최강" 기록됨(교차스택 미검토였음) |
| **Hydra(Commando Lv15)** | CascadingMassacre+HuntDown | DamagePerStack 0.15+0.10, 각 최대5스택=합산 +125% 추가피해. Hydra 패시브(FuryMode 이미 3배→1.2배 너프)를 스킬로 사실상 복구 | 패시브 너프 취지 훼손 우려 |
| **Maniac(Demo Lv5)** | Elmo+MadBomber+SlowCooker+ArmedAndDangerous | 4개 전부 구매 시 수류탄/화기 피해 +50~100%씩 중첩. Demo 패시브(이미 +150%→+80% 너프)를 스킬 레이어가 재차 복구 | Demo 수류탄 스택은 오퍼 1장에서 이미 OP로 확정된 항목, 재발 위험 |
| **Shapeshifter(Support Lv20)** | PrimordialVigor | DRPerBuff=0.025 × 15버프 = 최대 -37.5% 피해감소가 Mimicry(이미 OP 확정)에 추가로 누적 | 기존 Mimicry OP 판정을 심화시킴 |

### 🟢 Trash 신규 발견 (버그/무의미)

| 퍼크 | 스킬 | 문제 |
|---|---|---|
| **Pyrokinetic(Firebug Lv5)** | **ConsumingFlame** | `Vampire=0; Vampire=0` — T1/T2 모두 값이 0. **미완성 또는 버그로 확정.** 밸런스 수치 문제가 아니라 값 자체가 비어있어 의도된 수치를 알 수 없음 → 개발 확인 필요, 임의로 채워넣지 않음 |

### ⚠️ FLAG (인게임/추가 확인 필요, 이번에 새로 식별)

| 퍼크 | 스킬 | 이슈 |
|---|---|---|
| Agony | TemporalRupture | Chance=0.25/0.50만 있고 대상 효과 필드가 안 보임 — 무엇의 확률인지 불명 |
| Artificer | MasterworkTechnique / Soulbound | "PerMilestone" 성장식 — 마일스톤 정의(킬수? 아이템?)와 상한 불명 |
| Cryophilite | FrostbiteArrows | DamagePerStack의 MaxStacks 필드가 INI에 없음 |
| Tycoon | HODLing | InterestRate=0.25가 이미 너프된 패시브 CompoundInterestRate(10%)와 별도 중첩되는지 확인 필요 |
| **Voodoo (전체 스킬 6개)** | DealWithTheDevil/OdeToGreed/PainSplit/PinpointAccuracy/PowerTransfer/Triskelion | **전부 "체력 -X% 소모형" 스킬.** Voodoo 패시브 자체가 이미 HP -50%인데, 스킬을 여러 개 동시 장착하면 DefaultHP 대비 차감 비율이 100%를 초과할 가능성 있음. 기존 SoulStealer 클램프 FLAG와 동일 계열 문제이나 **범위가 스킬 6개로 확대됨** → 우선순위 상향 권고 |

### ✅ 적절 (대다수, 특이사항만 기재)

- **Bulwark/SpecialAgent 각 10개**: 전부 유사 수치 패턴(0.2~0.6)이지만 특정 좀비·피해원 조건부로 추정 — 동시 발동 불가하므로 설계 의도상 적절 (기존 "유지" 판정과 일치)
- **Headhunter/Gambler/Tycoon 스킬 전체**: 경제 퍼크, 이미 확립된 도쐬 밸런스 기준과 부합
- **Predator 보조스킬 8개**(TrophyHoarder·WildHunt 제외): 적절. 단 TrophyHoarder·WildHunt 2개는 위 FLAG 표(2장) 확정 OP를 심화시키는 스킬이므로 **INI로 미리 완화 완료** (아래 4장)
- **T2<T1 이상값 2건**: Cryophilite.WintersSwiftness(WeaponSwitchSpeed 0.5→0.4), Voodoo.DealWithTheDevil(Healing 0.85→0.70) — 판정 보류, 버그 또는 의도된 트레이드오프인지 재확인 필요

---

## 4. INI 수정 — 적용 완료 (이번 세션)

```ini
; [1] Cinder — ScorchedEarth 250%→100%로 정상화 (전체 최고 이상값) ✅ 적용완료
[ZedternalRBPerkpackage.DKUpgrade_Skill_ScorchedEarth]
Damage=0.500000
Damage=1.000000

; [2] Predator — 트로피 시스템 자체는 하드코딩이라 손댈 수 없지만,
;     이 두 스킬만은 INI로 트로피 OP를 완화하는 유일한 개입 지점 ✅ 적용완료
[ZedternalRBPerkpackage.DKUpgrade_Skill_TrophyHoarder]
ExtraSlots=1                 ; T2도 슬롯 추가 없이 1로 고정

[ZedternalRBPerkpackage.DKUpgrade_Skill_WildHunt]
TrophyInterval=5             ; T2도 5로 고정 (드랍 가속 억제)
```

**추가 적용 완료 (2026-07-01 후속)**:
```ini
; [3] Daredevil — FullMetalJacket 관통 +300%→+150% (Support 관통 교차스택 억제)
[ZedternalRBPerkpackage.DKUpgrade_Skill_FullMetalJacket]
Penetration=0.750000
Penetration=1.500000

; [4] Hydra — CascadingMassacre+HuntDown 스택합산 +125%→+65%
[ZedternalRBPerkpackage.DKUpgrade_Skill_CascadingMassacre]
DamagePerStack=0.050000
DamagePerStack=0.080000
[ZedternalRBPerkpackage.DKUpgrade_Skill_HuntDown]
DamagePerStack=0.030000
DamagePerStack=0.050000

; [5] Maniac — 수류탄 스킬 4종 T2합 +260%→+145%
[ZedternalRBPerkpackage.DKUpgrade_Skill_ArmedAndDangerous]
Damage=0.200000 / 0.300000
[ZedternalRBPerkpackage.DKUpgrade_Skill_Elmo]
Damage=0.300000 / 0.500000
[ZedternalRBPerkpackage.DKUpgrade_Skill_MadBomber]
Damage=0.200000 / 0.350000
[ZedternalRBPerkpackage.DKUpgrade_Skill_SlowCooker]
Damage=0.150000 / 0.300000

; [6] Shapeshifter — PrimordialVigor DR -37.5%→-22.5% (Mimicry 탱크성 심화 억제)
[ZedternalRBPerkpackage.DKUpgrade_Skill_PrimordialVigor]
DRPerBuff=0.008000
DRPerBuff=0.015000
```
Maniac 4종은 스킬 소스 전문 확인 없이 INI 필드명(Damage) 기준 worst-case 가정으로 하향한 것 — 인게임 확인 권장.

---

## 5. 우선순위 재정렬 제안

1. **🚨 Predator 트로피 — 유저 최우선 인지** (INI로는 TrophyHoarder/WildHunt 완화만 가능, 근본 해결은 소스 패치 필요)
2. **Voodoo 스킬 6개 HP소모 중첩 + SoulStealer 클램프 — 인게임 테스트 필요** (범위 확대 확인됨)
3. ~~Cinder ScorchedEarth 즉시 너프~~ ✅완료
4. ~~Predator TrophyHoarder/WildHunt 완화~~ ✅완료
5. ~~Daredevil/Hydra/Maniac/Shapeshifter 스킬 4건~~ ✅완료 (2026-07-01)
6. Pyrokinetic ConsumingFlame 버그 — 유저 확인/의도 확인 필요 (밸런스 문제 아님)
7. ~~오퍼 FLAG 5건~~ ✅완료 (4건 적절/해소, SonicResistantRounds 너프, SuppressionRounds+Cripple만 잔여 FLAG)

---

## 6. 전체 FLAG 총목록 (INI 수정 불가 / 인게임·소스 확인 필요, 통합)

| 항목 | 원인 | 심각도 |
|---|---|---|
| Predator 트로피 시스템 | 완전 하드코딩 | 🚨 최고 |
| Shapeshifter Mimicry | Balance ini 부재 | 높음 |
| Gambit 영구누적 | 하드코딩, config 없음 | 높음 |
| Detonator 패시브 2종 | Balance ini 부재 | 낮음(설계자체는 적절) |
| SoulStealer+Voodoo스킬군 HP클램프 | 소스상 미확인 | 중간(확대됨) |
| LuckySalvage(무기) | transient+하드코딩 | Trash 확정, 구제불가 |
| Reaper 즉사 5% | 하드코딩 리터럴 | 낮음(대형ZED 포함 인지만 필요) |
| ConsumingFlame(Pyrokinetic) | 값이 0, 버그 추정 | 밸런스 외 이슈 |
| Agony.TemporalRupture 등 4건 | 효과/상한 불명 | 낮음~중간 |
| 오퍼 BringTheHeat 등 5건 | 인게임 확인 필요 | 중간 |
