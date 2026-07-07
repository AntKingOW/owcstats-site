# PLAN 04 — 경기별 스탯 제공을 위한 사이트 개편

> 2026-07-08 업데이트: 상위 IA 문서 [PLAN_07](PLAN_07_SITE_IA_REDESIGN.md)이 추가됨 (홈 제거 → 경기 피드).
> S1 데이터 소급은 [PLAN_06](PLAN_06_S1_MATCH_DATA_BACKFILL.md)이 담당 — matches 데이터는 2026 Stage 2 시작이 아니라
> **S1부터 전체 백필**로 변경. match_id 체계도 PLAN_06 §2a의 canonical id를 따른다.

목표: owtv.gg처럼 **경기(매치) 단위 상세 페이지**를 제공 — 맵별 결과, 히어로 밴, 선수별 맵 스탯.
의존: [PLAN_02](PLAN_02_OWTV_STAGE2_SCRAPING.md) 산출물 (경기·맵·밴·스탯 데이터).
제약: GitHub Pages **정적 호스팅** — 서버 없음, 빌드 타임에 JSON 생성 + 클라이언트 fetch 방식 유지.

## 1. 설계 원칙

- 기존 페이지(elo/players/teams/tournaments/ban-calculator)는 유지하고 **matches 축을 추가**한다.
  "전체 개편"은 빅뱅 재작성이 아니라, 매치 데이터 모델을 중심에 놓고 기존 페이지가 이를 참조하도록
  단계적으로 전환하는 것을 뜻한다 (아래 Phase 순서).
- 데이터는 페이지당 필요한 만큼만 로드 (전체 스탯 JSON 하나로 만들면 수 MB — 금지).

## 2. 데이터 모델 (신규 파일)

### `assets/data/matches_index.json` — 경기 목록 (목록 페이지용, 가볍게)
```json
[{"slug":"korea-stage-2-owcs-2026-regular-season-week-4-cr-vs-zeta",
  "event_id":"owcs_2026_asia_s2_korea", "region":"Korea", "stage":"Stage 2",
  "phase":"Regular Season", "round":"Week 4", "date":"2026-06-28",
  "team1":"Crazy Raccoon", "team2":"ZETA DIVISION",
  "score1":2, "score2":3, "winner":"ZETA DIVISION", "firstTo":3}]
```

### `assets/data/matches/<slug>.json` — 경기 상세 (상세 페이지용, 경기당 1파일)
```json
{"slug":"…", "meta":{ …matches_index와 동일 필드… },
 "maps":[{"n":1, "name":"Runasapi", "mode":"Push",
          "score1":51.52, "score2":135.44, "winner":2,
          "ban1":"Shion", "ban2":"Lúcio", "firstBan":1, "pickedBy":1,
          "duration_min":null}],
 "stats":[{"map":1, "team":1, "player":"KNIFE", "role":"DPS",
           "E":36, "A":2, "D":9, "DMG":14401, "H":64, "MIT":2145}]}
```
- `duration_min`: PLAN_05에서 사용자가 채우기 전까지 `null`.
- 생성기: `build_site_data.py`에 `build_matches()` 함수 추가 (소스: PLAN_02의 owtv_raw JSON.
  과거 시즌은 데이터가 없으므로 2026 Stage 2부터 시작하고, 추후 소급).

## 3. 페이지 구성

### 신규 `matches.html` — 경기 목록
- 필터: 지역 / 스테이지 / 팀 / phase. 카드형 리스트 (팀 로고 + 점수 + 날짜).
- `matches_index.json`만 로드. 각 카드 → `match.html?m=<slug>`.

### 신규 `match.html` — 경기 상세 (핵심 신규 페이지)
- URL: `match.html?m=<slug>` (정적 호스팅이므로 쿼리 파라미터 라우팅).
- 구성 (owtv 레이아웃 참고):
  1. 헤더: 팀 로고 · 세트 스코어 · 대회/phase/날짜
  2. 맵 타임라인: 맵별 카드 (맵명·모드·점수·승자 하이라이트·**밴 2개 히어로 아이콘/이름**)
  3. 선수 스탯 테이블: 맵 선택 탭 (전체 합계 / Map 1 / Map 2 …), 컬럼 E·A·D·DMG·H·MIT,
     팀별 2개 테이블, 역할 아이콘, 정렬 가능
  4. per-10 표기는 `duration_min`이 채워진 맵만 (없으면 합계만 표시 — PLAN_05 정책)
- 존재하지 않는 slug → "경기를 찾을 수 없습니다" + matches.html 링크.

### 기존 페이지 연결 (Phase 2)
- `tournaments.html`: 이벤트 상세에 "경기 목록" 섹션 추가 → match.html 링크.
- `teams.html`: 팀 카드에 최근 경기 5개 + 링크.
- `ban-calculator.html`: 밴 데이터 소스를 matches 파생으로 일원화 (기존 ban_events와 중복 제거).
- `players.html`: 선수 클릭 → 해당 선수 경기 목록 (Phase 3, 선택).

## 4. 공통 인프라 정리 (개편에 포함)

- **로고 로직 통합**: teams/players/tournaments에 중복된 slugify/EXT맵/fallback을
  `assets/team-logos.js` 하나로 추출, match.html도 이것을 사용.
- **i18n**: 신규 페이지 문자열을 `assets/i18n.js`에 EN/KR로 추가 (기존 패턴:
  `data-i18n` 속성 + `applyI18n()` + `langchange` 이벤트).
- **nav**: `assets/nav.js`의 메뉴 배열에 Matches 추가, `DATA_V` 버전 업.
- 스타일은 `assets/style.css`의 기존 CSS 변수(`--panel`, `--border`, `--accent`, `--radius`)를 재사용.

## 5. 실행 순서 (Phase)

| Phase | 작업 | 완료 기준 |
|---|---|---|
| 1 | 데이터 모델: build_matches() + matches_index.json + matches/*.json 생성 | Korea Stage 2 36경기 JSON 생성, 표본 3경기 owtv 화면과 수치 일치 |
| 2 | match.html + matches.html 구현, nav 추가 | 로컬 서버에서 전 경기 렌더, 콘솔 에러 0 |
| 3 | tournaments/teams에서 경기 링크 연결 | 각 페이지에서 상세로 이동 가능 |
| 4 | ban-calculator 데이터 일원화, players 연동 | 기존 기능 회귀 없음 |

각 Phase 완료 시 커밋 분리. Phase 2부터 DATA_V 버전 업 필요.

## 6. 검증

- 표본 대조: CR vs ZETA (W4) — 세트 2:3, Map5 Runasapi 밴 Shion/Lúcio, KNIFE Map5 E36/A2/D9/DMG14401.
- 모바일(375px)에서 스탯 테이블이 가로 스크롤 컨테이너 안에서 동작하는지.
- Lighthouse 또는 네트워크 탭으로 matches.html 초기 로드 < 300KB 확인.
