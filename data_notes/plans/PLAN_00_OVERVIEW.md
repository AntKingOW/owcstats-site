# 작업 계획 총괄 (2026-07-08 작성)

> **이 문서 세트의 목적**: 어떤 AI 모델/에이전트든 이 폴더의 문서만 읽고 동일한 작업을 수행할 수 있도록,
> 검증된 사실·경로·스키마·실행 순서를 자체 완결적으로 기록한다.
> 작업 전 반드시 [PROCESS_RULES.md](../PROCESS_RULES.md)(검증 원칙·배포·캐시 버스팅)를 먼저 읽을 것.

## 저장소 구조 (부모 폴더 `OWCStats.com/` 기준)

| 폴더 | 역할 | git |
|---|---|---|
| `owcstats-site/` | 배포 사이트 (GitHub Pages: https://antkingow.github.io/owcstats-site/) | ✅ https://github.com/AntKingOW/owcstats-site |
| `Elo-Rating/` | ELO 계산 파이프라인·MAP_RESULTS CSV 원본·Liquipedia 스크레이퍼 | ✅ (로컬) |
| `OWCStats/` | 경기 리뷰 엑셀/CSV (선수 스탯 원본, `OWCStats/OWCStats/` 하위) | ✅ (로컬) |
| `CardNews/` | 홍보용 PPTX | — |

## 계획 문서 인덱스 및 실행 순서

| 순서 | 문서 | 내용 | 의존성 |
|---|---|---|---|
| 1 | [PLAN_01_SITE_ISSUE_FIXES.md](PLAN_01_SITE_ISSUE_FIXES.md) | 사이트 검토에서 발견된 이슈 해결 (일부 완료) | 없음 |
| 2 | [PLAN_02_OWTV_STAGE2_SCRAPING.md](PLAN_02_OWTV_STAGE2_SCRAPING.md) | owtv.gg에서 2026 Stage 2 경기 결과·맵·밴·선수 스탯 수집 | 없음 |
| 3 | [PLAN_03_ELO_UPDATE_2026_STAGE2.md](PLAN_03_ELO_UPDATE_2026_STAGE2.md) | Stage 2 결과로 ELO 최신화 (owtv 또는 Liquipedia) | PLAN_02 |
| 4 | [PLAN_04_MATCH_STATS_SITE_REVAMP.md](PLAN_04_MATCH_STATS_SITE_REVAMP.md) | owtv처럼 경기별 스탯 제공하는 사이트 개편 | PLAN_02 |
| 5 | [PLAN_05_PLAYER_STATS_STAGE2_POLICY.md](PLAN_05_PLAYER_STATS_STAGE2_POLICY.md) | Stage 2 선수 스탯: 경기시간 공란 정책 및 per-10 제외 처리 | PLAN_02 |
| 6 | [PLAN_06_S1_MATCH_DATA_BACKFILL.md](PLAN_06_S1_MATCH_DATA_BACKFILL.md) | S1+Champions Clash 데이터를 경기별/세트별 구조로 변환 (스파인+어댑터 설계) | 없음 (S2 합류만 PLAN_02) |
| 7 | [PLAN_07_SITE_IA_REDESIGN.md](PLAN_07_SITE_IA_REDESIGN.md) | 사이트 전체 IA 개편: 홈 제거 → 경기 피드, 대회 허브 중심 재편 | PLAN_04·06 |

## 공통 규칙 (모든 계획에 적용)

1. **데이터 검증**: 수치를 반영하기 전 원본(CSV/JSON/스크레이핑 결과)으로 교차 확인. 불일치 시 사용자에게 보고 후 진행.
2. **ELO 승계 수치는 사용자 승인 필수** — [ELO_POLICY.md](../ELO_POLICY.md) 참조. 임의 결정 금지.
3. **배포**: `git push origin main` → GitHub Pages 자동 배포. JSON 데이터가 바뀌면 `assets/nav.js` 상단 `window.DATA_V` 버전과 모든 HTML의 `nav.js?v=...` 쿼리를 함께 올린다.
4. **팀명 정규화**: CSV/사이트 전반에서 팀명 표기가 소스마다 다르다. `build_site_data.py`의 `TEAM_NAME_ALIASES`, `Elo-Rating/OWCS_KOREA_ELO_TEAM_ALIASES.md`, owtv 팀명(예: "Zeta Division" vs 사이트의 "ZETA DIVISION")을 대조해 **canonical 이름으로 통일**할 것. 새 소스(owtv)를 추가하면 alias 맵을 반드시 확장한다.
5. **인코딩**: 모든 파일은 UTF-8. Windows PowerShell에서 파일 쓸 때 `-Encoding utf8` 주의.

## 현재 데이터 파이프라인 (참고)

```
Elo-Rating/OWCS_{year}_GLOBAL_MAP_RESULTS.csv   ← 맵 단위 결과 (스크레이핑 산출물)
        │  Elo-Rating/build_owcs_{year}_global_elo.py
        ▼
Elo-Rating/OWCS_{year}_GLOBAL_ELO_FINAL.csv / _HISTORY.csv
        │  owcstats-site/build_site_data.py        ← OWCStats/ 선수 CSV도 여기서 합류
        ▼
owcstats-site/assets/data/*.json (elo_rankings, elo_history, player_stats, ban_* …)
        │  git push (DATA_V 버전 올리기)
        ▼
https://antkingow.github.io/owcstats-site/
```
