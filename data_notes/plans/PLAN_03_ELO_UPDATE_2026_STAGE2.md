# PLAN 03 — ELO 최신화 (2026 Stage 2 반영)

의존: [PLAN_02](PLAN_02_OWTV_STAGE2_SCRAPING.md) 산출물 ① (맵 결과 CSV), 또는 대안 경로(Liquipedia).
정책: [ELO_POLICY.md](../ELO_POLICY.md) — K=24, Base=1400, 승계 수치는 **사용자 승인 필수**.

## 현재 상태 (2026-07-08 기준)

- `Elo-Rating/OWCS_2026_GLOBAL_MAP_RESULTS.csv`: Stage 1 + Champions Clash까지 반영됨 (Stage 2 없음).
- Stage 2 **시작 ELO는 이미 주입 완료**: `owcstats-site/inject_stage2_initial_elo.py`로
  elo_history.json에 `result:"start"` 엔트리 추가됨 (신생 1400, 승계팀은 ELO_POLICY.md의 표 참조).
  → 커밋 `338cbcc`, `c1e106b` 참고.
- ⚠️ 주의: inject 스크립트는 **사이트 JSON에 직접** 주입한 단발성 작업이다. CSV 파이프라인으로
  전체 재계산하면 이 주입이 덮어써질 수 있으므로 §3의 재계산 절차를 그대로 따를 것.

## 경로 A (권장) — owtv 수집 결과 사용

1. PLAN_02 산출물 ①을 검토: 팀명이 canonical인지, 중국 Swiss 제외됐는지, 무승부 표기가 기존 CSV와 같은지.
2. `OWCS_2026_GLOBAL_MAP_RESULTS.csv` 맨 뒤에 append. `global_map_order`는 기존 마지막 값에서 연속 증가.
   경기 정렬: `match_date` → `match_order` → `game_number`.
3. §3 재계산 실행.

## 경로 B (대안) — Liquipedia 스크레이핑

기존 스크레이퍼가 `Elo-Rating/`에 있다. Stage 1 때 쓴 것을 Stage 2 URL로 확장:
- `scrape_group_stages_2026.py`, `scrape_stage1_playoffs_2026.py`, `parse_korea_playoffs_2026.py` — 선례.
- 소스 URL 패턴: `https://liquipedia.net/overwatch/Overwatch_Champions_Series/2026/<Region>/Stage_2/...`
  (Stage 1 CSV의 `source_url` 컬럼에서 실제 패턴 확인 가능)
- Liquipedia 요청 매너: User-Agent에 연락처 명시, 요청 간 2초 이상, `?action=raw` 활용 가능.
- 장점: 검증된 파서 존재. 단점: 밴/선수 스탯은 Liquipedia에 없거나 부실 → **경기 결과는 A/B 어느 쪽이든
  가능하지만 밴·스탯은 owtv(PLAN_02)가 유일한 통합 소스.**
- 두 경로를 병행하면 상호 검증 가능 (권장: A로 수집, B로 표본 대조).

## §3. 재계산 및 배포 절차

```bash
cd Elo-Rating
python build_owcs_2026_global_elo.py     # CSV → OWCS_2026_GLOBAL_ELO_FINAL.csv / _HISTORY.csv
```
- 이 스크립트에는 `STAGE2_REBRAND_MAP`(승계 매핑)이 포함되어 있음 — Stage 2 팀명이 새로 들어오면
  이 맵과 ELO_POLICY.md의 승계 표가 일치하는지 먼저 확인. 새 승계 케이스 발견 시 **사용자 확인 후** 추가.
- 시작 ELO 주입값(§현재 상태)과 재계산 결과의 Stage 2 시작값이 일치하는지 확인
  (불일치 시 inject 스크립트와 REBRAND_MAP 중 어느 쪽이 맞는지 사용자에게 질의).

```bash
cd ../owcstats-site
python build_site_data.py                # → assets/data/*.json 재생성
```

배포 전 체크:
1. `elo_rankings.json`의 "2026" 팀 수가 기대값(기존 59 + Stage 2 신규팀)인지
2. `elo_history.json`에서 표본 팀(예: Crazy Raccoon)의 Stage 2 이벤트 엔트리가 추가됐는지
3. 로컬 서버로 elo.html / tournaments.html / index.html Top5 렌더 확인
4. `assets/nav.js`의 `window.DATA_V`를 새 날짜로 (예: `20260712a`) + 모든 HTML의 `nav.js?v=` 동기화
5. `git add … && git commit && git push origin main`

## 갱신 주기

Stage 2 진행 중(~7/12 Korea, ~7/9 Pacific)이므로, 플레이오프 종료 후 1회 일괄 반영이 효율적.
Midseason Championship(7/29~8/2)도 같은 절차로 반영 (owtv 슬러그: `midseason-championship-owcs-2026`).
