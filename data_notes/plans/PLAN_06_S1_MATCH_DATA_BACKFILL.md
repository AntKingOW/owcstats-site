# PLAN 06 — S1(Stage 1 + Champions Clash) 경기별/세트별 스탯 구조화

목표: owtv.gg가 S2에서 제공하는 **대회별 → 경기별 → 세트(맵)별** 3계층 스탯 구조를
우리가 보유한 S1 데이터로도 동일하게 구축한다. PLAN_04의 데이터 모델을 그대로 사용하며,
이 문서는 "S1 소스를 그 모델로 변환하는 방법"을 정의한다.

## 1. 보유 데이터 실측 (2026-07-08 확인)

### 경기/맵 결과 (전 지역·전 스테이지) — ✅ 완비
`Elo-Rating/OWCS_2026_GLOBAL_MAP_RESULTS.csv` — 맵 단위 1행, 컬럼:
`global_map_order, event_id, event_region, season_year, stage_label, week_label, day_label,
match_date, match_order, game_number, team_a, team_b, winner, loser, map_name, map_mode,
series_format, source_url, source_note`
→ **매치 스파인(spine)의 원천**: `(event_id, match_date, match_order)`로 그룹핑하면 매치가 되고,
맵 승자를 세면 세트 스코어가 나온다.

### 선수 맵 스탯 (Minutes 포함) — 지역별 상이
| 소스 | 커버리지 | 형식 |
|---|---|---|
| `OWCStats/OWCStats/KOREA_WITH_ASIA_MATCH_REVIEW_CSV_FIXED/KOREA_WITH_ASIA_review_all_matches.csv` | Korea 전체 + Asia Stage, **54 매치** | 헤더: `Event,MatchId,Match,Phase,Game,Source,Map,Elapsed,Minutes,Team,Player,Role,Row,E,A,D,DMG,H,MIT`. **sparse — 게임 첫 행만 메타 기입, 이후 행은 공란(forward-fill 필요)** |
| `OWCStats/OWCStats/EMEA_NA_MATCH_REVIEW_CSV/all_games_long.csv` | EMEA + NA 전체 | 헤더에 `Region, MatchId(예: emea_owcs_emea_2026_playoff_grand_final), CleanReason, NeedsReOCR` 등 검수 컬럼 + per-10 파생 컬럼 포함. dense(전 행 메타 기입) |
| `OWCStats/OWCStats/CLASH_MATCH_REVIEW_CSV/clash_2026_per_map.csv` | Champions Clash 전체 | EMEA_NA와 동일 구조. **MatchId·Source가 이미 owtv 슬러그/URL** (예: `clash_2026_tm_vs_ag`, `https://owtv.gg/matches/champions-clash-owcs-2026-playoffs-tm-vs-ag`) — S2 owtv 수집과 자연스럽게 이어지는 선례 |
| Japan / Pacific / China | ❌ 선수 스탯 CSV 없음 (`OWCStats/OWCStats/Match Results/`에 스크린샷 원본만 일부) | 스탯 없이 결과·밴만 제공, 추후 보강 |

### 밴 데이터 — ✅ (KR/NA/EMEA/Asia)
`owcstats-site/assets/data/ban_events.json` — **1,110 이벤트**, 스키마:
```json
{"region":"Korea","phase":"Week 1","match_label":"2026-03-20 Match 1","game":"1",
 "map":"Busan","map_mode":"Control","ban_stage":"initial","ban_team":"Poker Face",
 "banned_hero":"Emre","received_team":"Cheeseburger"}
```
- `ban_stage`: `initial`(선밴) / `followup`(후밴). `match_label` = `날짜 + Match n` → 스파인과 조인 가능.
- ⚠️ `banned_hero`에 OCR 오류 의심값 존재 (예: "Emre"는 히어로명 아님) — 변환 시 히어로 사전으로 검증, 미매칭은 보고서에 수집해 사용자 확인.

## 2. 변환 설계

### 2a. canonical match_id
소스마다 id 체계가 다르므로 (`asia_group_stage_day1_match1` / `emea_owcs_emea_2026_playoff_grand_final` / owtv 슬러그) **스파인에서 새로 발급**한다:
```
match_id = f"{event_id}__{match_date}_{match_order:02d}"   예: owcs_2026_korea_s1__2026-03-20_01
```
원본 id들은 `source_ids: {"stats_csv": "...", "owtv": "...", "ban_label": "..."}`로 보존 (역추적·디버깅용).

### 2b. 빌더 구조 — `owcstats-site/build_matches.py` (신규)
```
1. adapter_spine()      : MAP_RESULTS CSV → 매치·세트 뼈대 (전 지역·전 스테이지)
2. adapter_bans()       : ban_events.json → (region, match_label 날짜, game) 키로 세트에 밴 부착
3. adapter_stats_kr()   : Korea+Asia CSV  → forward-fill 후 (팀쌍, Phase/Game) 키로 부착
4. adapter_stats_emea_na(): all_games_long.csv → MatchId 파싱 + (팀쌍, Game) 키로 부착
5. adapter_stats_clash(): clash_2026_per_map.csv → 동일
6. adapter_owtv()       : PLAN_02 산출물(S2) → 동일 모델로 합류
7. emit()               : matches_index.json + matches/<match_id>.json + 대회별 집계
```
- 조인 키는 **정규화된 팀쌍 + 날짜(또는 phase) + game_number**. 팀명 정규화는
  `build_site_data.py`의 `TEAM_NAME_ALIASES`를 공유 모듈로 추출해 재사용.
- **매칭 실패는 절대 조용히 버리지 말 것**: `data_notes/match_join_report.md`에
  (소스, 키, 후보) 목록을 생성해 사용자 검토를 받는다 (PROCESS_RULES 검증 원칙).

### 2c. 출력 (PLAN_04 모델과 동일 + 확장 필드)
`matches/<match_id>.json`의 map 오브젝트에 S1 확장:
```json
{"n":1, "name":"Lijiang Tower", "mode":"Control",
 "winner":1, "score1":2, "score2":1,
 "ban1":"D.Va", "ban2":"Ana", "firstBan":1,
 "duration_min":9.33,                      // S1: CSV Elapsed에서. S2: null (PLAN_05)
 "stats_available":true}                   // Japan/Pacific/China 등 스탯 없는 맵 구분
```
매치 meta에 `"data_coverage": {"stats":true,"bans":true,"duration":true}` — 프런트가
지역별 데이터 격차를 우아하게 표시할 수 있도록.

### 2d. 대회별 집계 (owtv의 tournament stats 상당)
`assets/data/tournaments/<event_id>_stats.json`:
- 팀 순위(세트 득실 포함), 선수 리더보드(합계 + Minutes 있는 경우 per-10), 밴 리더보드(히어로별 횟수).
- 빌더의 emit 단계에서 matches JSON을 다시 읽지 말고 메모리에서 함께 집계.

## 3. 실행 순서

1. `build_matches.py` 스파인 + Korea 어댑터 구현 → Korea S1 54매치로 파이프라인 검증
2. 밴 어댑터 + EMEA/NA/Clash 어댑터 추가 → join_report 생성 → **사용자 검토**
3. Japan/Pacific/China: 결과+밴만으로 emit (stats_available=false)
4. PLAN_02(S2 owtv) 산출물을 adapter_owtv로 합류
5. 검증(§4) 통과 후 커밋. 프런트 작업은 PLAN_04/PLAN_07에서 소비

## 4. 검증 체크리스트

- [ ] 스파인 매치 수 = MAP_RESULTS의 (event_id,date,match_order) 유니크 수와 일치
- [ ] Korea 54 매치 전부 스탯 부착 (미부착 0)
- [ ] 세트 스코어 합 = 맵 행 수 (draw 포함 규칙 확인)
- [ ] ban_events 1,110건 중 부착 실패 목록 → 사용자 보고
- [ ] 표본 대조: EMEA Playoff Grand Final Game 1 = Lijiang Tower, VP eisgnom E13/A5/D6/DMG10462, 10.35분
- [ ] player_stats.json 기존 집계와 새 구조 합계 일치 (E/A/D/DMG/H/MIT 총합 교차 검증)
