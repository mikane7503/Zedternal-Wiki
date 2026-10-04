# 템퍼드 위키 원본 데이터

이 폴더는 GitHub Pages 빌드에서 사용할 템퍼드 소스 스냅샷입니다. 기준 표시는 `Tempered-Version.json`에 기록된 버전과 날짜를 사용합니다.

- 퍼크·스킬 값: `KFZedternalUnlimited.ini`, `KFZedternalReborn_Upgrades.ini`
- 게임 기본값: 같은 폴더의 Difficulty, Events, Game, Weapons, ZedWaves 설정
- 표시 설명: `ZedternalTempered.kor`, `ZedternalReborn.kor`
- 퍼크 클래스 기본 효과: `classes/ZUTUpgrade_Perk_Base_*.uc`, `classes/ZTUpgrade_Perk_Capitalist.uc`, `classes/ZTUpgrade_Perk_Engineer.uc`
- Engineer 드론 수치: `KFZedternalUnlimited.ini`의 `ZTConfig_EngineerDrones` 섹션

운영 서버의 INI는 서버 관리자 설정을 포함할 수 있어 위키 입력값으로 복사하지 않습니다. 스냅샷을 갱신할 때는 템퍼드 소스에서 해당 파일을 함께 교체하고, `python data/build.py`를 실행해 `docs/data/perks.json`을 재생성합니다. GitHub Actions도 배포 전에 같은 생성 단계를 수행합니다.
