# Zedternal Tempered 위키

GitHub Pages 정적 사이트입니다. Pages 배포는 `main` 브랜치 push 또는 Actions의 수동 실행으로 시작되며, 배포 전에 `python data/build.py`가 체크인된 템퍼드 소스 스냅샷에서 퍼크·스킬·시스템 데이터를 다시 생성합니다.

## 로컬 데이터 갱신

1. `data/source/tempered/`의 설정·로컬라이제이션·기본 클래스 스냅샷을 템퍼드 기준 소스와 함께 갱신합니다.
2. `python data/build.py`를 실행합니다. 생성 결과는 `docs/data/perks.json`입니다.
3. 사이트 파일을 수정한 뒤 Pages 워크플로가 만드는 결과를 확인합니다.

사이트는 운영 서버 INI를 읽지 않습니다. 서버별 별도 설정이 있을 수 있으므로 위키의 출처 표시는 항상 템퍼드 소스 기본값 기준입니다. 원본 파일의 버전과 날짜는 `data/source/tempered/Tempered-Version.json`에서 확인할 수 있습니다.
