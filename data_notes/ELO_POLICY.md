# ELO 정책

## 기본값
- 신생팀 초기 ELO: **1400**
- K factor: 24
- 연도 이월: 전년도 최종 ELO를 이듬해 시작값으로 사용

## 스테이지 간 승계 규칙

### 합병 (Merge)
두 팀이 하나로 합쳐질 때 → **더 높은 쪽 ELO 승계**
예) ZANSIDE GAMING ← Onside Gaming (1499.6) + 제트스트림(낮음)

### 팀 승계 (Succession)
로스터 핵심이 이동하며 팀명만 바뀔 때 → **구 팀 ELO 승계**
예) SHENGSHI Esports ← The Gatos Guapos (1527.5)

### 리브랜드 (Rebrand, 데이터 없는 경우)
구 팀이 OWCS에 데이터가 없으면 → **신생팀 취급 (1400)**
예) Kitsune Kage ← Team KK (S1 데이터 없음)

### 지역 이동 승계 (Cross-region Succession)
다른 지역 팀의 로스터가 이전될 때 → **사례별 사용자 판단 필요**
예) 1234 ← Anyone's Legend (EMEA←China, 1407.4)

---

## ⚠️ 승계 검토 절차 (→ PROCESS_RULES.md 참조)
ELO 승계 수치는 **사용자 확인 후** 반영. 임의 결정 금지.

---

## 중국 대회 특이사항
- Swiss Stage 결과는 ELO에 반영 **안 함**
- Round Robin Stage + Playoffs 결과만 반영 (S1과 동일 방침)

---

## 관련 스크립트
| 스크립트 | 역할 |
|---|---|
| `inject_stage2_initial_elo.py` | S2 시작 ELO를 JSON에 직접 주입 (단발성) |
| `Elo-Rating/build_owcs_2026_global_elo.py` | CSV → ELO 전체 재계산 (STAGE2_REBRAND_MAP 포함) |

## elo_history.json 구조
```json
{
  "팀명": [
    { "event": "event_id", "elo": 1450.2, "year": "2026", "result": "win" },
    { "event": "owcs_2026_asia_s2_korea", "elo": 1499.6, "year": "2026", "result": "start" }
  ]
}
```
- `result:"start"` → 스테이지 시작 마커 (tournaments.html의 hasStageData 감지용)

## 2026 Stage 2 승계 현황
| 신규 팀 | 구 팀 | ELO | 분류 |
|---|---|---|---|
| ZANSIDE GAMING | Onside Gaming | 1499.6 | 합병 |
| SHENGSHI Esports | The Gatos Guapos | 1527.5 | 승계 |
| Najdorf Esports | Rankers | 1440.5 | 승계 |
| Trap12 | Quasar Esports | 1377.0 | 승계 |
| The Kafe | Extinction | 1339.3 | 승계 |
| 1234 | Anyone's Legend | 1407.4 | 승계(지역이동) |
| Kitsune Kage | Team KK | 1400 | 리브랜드(데이터없음) |
