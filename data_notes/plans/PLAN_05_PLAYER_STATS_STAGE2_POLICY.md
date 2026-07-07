# PLAN 05 — 선수 스탯: Stage 2 경기시간 공란 정책

## 배경 (그대로 따라야 할 사용자 결정)

- 사이트의 선수 스탯은 **per-10분** 지표이며, 계산에 맵별 경기시간(Minutes)이 필요하다.
- **Stage 1 + Champions Clash까지는** 사용자가 정리한 CSV에 Minutes가 있음
  (`OWCStats/OWCStats/KOREA_WITH_ASIA_MATCH_REVIEW_CSV_FIXED/…`, `clash_player_stats.json` 등).
- **Stage 2는 owtv.gg에 시간 데이터가 없다** (2026-07-08 검증 — PLAN_02 §1).
  → **사용자가 직접 시간을 가져와 채울 예정. 그때까지 Minutes는 공란으로 두고,
  Stage 2 기록은 per-10 스탯 집계에서 제외한다.**

## 구현 규칙

### 1. 수집 시 (PLAN_02 산출물 ③)
`stage2_player_map_stats.csv`의 `Minutes` 컬럼을 **빈 문자열로 생성**. 절대 추정치·평균값으로 채우지 말 것.

### 2. 집계 시 (`owcstats-site/build_site_data.py`)
- 현재 Korea 파서(`parse_korea_players()`)는 Minutes를 **forward-fill**한다
  (같은 게임의 후속 행이 공란이면 직전 값 재사용). ⚠️ Stage 2 행을 같은 CSV에 합치면
  공란이 이전 게임 시간으로 잘못 채워진다 — **Stage 2는 별도 파일로 유지**하고,
  집계 함수는 "Minutes가 실제로 기입된 행만" per-10 계산에 포함하도록 구현할 것.
- 권장 구조: `parse_stage2_players()`를 신설하고,
  `if not row["Minutes"].strip(): continue  # 시간 미기입 → per-10 집계 제외`
- 기존 최소 출전시간 필터(합계 5분 미만 제외)는 동일 적용.

### 3. 사이트 표시
- players.html 산점도는 per-10 기반이므로 **시간이 채워질 때까지 Stage 2는 자동으로 미반영** — 별도 처리 불필요.
- 단, 페이지 부제/필터에 데이터 범위를 명시할 것: "Stage 1 + Champions Clash 기준
  (Stage 2는 경기시간 확보 후 반영 예정)" — i18n.js에 EN/KR 문자열 추가.
- PLAN_04의 match.html에서는 시간이 없어도 **맵별 합계(E/A/D/DMG/H/MIT)는 표시 가능** —
  per-10 파생 컬럼만 `duration_min == null`일 때 숨긴다.

### 4. 사용자가 시간을 채우는 방법 (핸드오프 규격)
사용자가 채울 파일: `OWCStats/OWCStats/STAGE2_OWTV_CSV/stage2_player_map_stats.csv`의 `Minutes` 열.
- 단위: **분 단위 소수** (예: `12.4`) — 기존 Korea CSV와 동일.
- 같은 맵의 모든 선수 행에 동일한 값 (맵 시간 = 모든 선수 공통).
  더 편하게는 맵 단위 별도 파일 `stage2_map_durations.csv`(`match_slug,game_number,minutes`)를 만들어
  빌드 시 join하는 방식도 가능 — 사용자에게 어느 쪽이 편한지 확인 후 결정.
- 채워지면: `build_site_data.py` 실행 → player_stats.json에 Stage 2 반영 →
  matches/*.json의 `duration_min` 채움 → DATA_V 업 → push.

### 5. 검증
- Minutes 공란 상태에서 빌드 → player_stats.json의 games/minutes 수치가 **기존과 완전 동일**해야 함
  (Stage 2가 새어 들어가지 않았다는 증거).
- Minutes 일부만 채워진 경우: 채워진 맵만 반영되는지 표본 확인.
