# PLAN 07 — 사이트 전체 구조(IA) 개편안

배경: 사용자 방향 — ① owtv.gg처럼 대회별/경기별/세트별 스탯이 중심이 되어야 하고
② **독립된 메인 홈(랜딩) 페이지는 불필요**.
의존: PLAN_06(데이터), PLAN_04(match 상세 페이지 설계 — 본 문서가 IA 상위 문서).

## 1. 개편 원칙

- 홈을 없애는 방식: **index.html을 삭제하지 않고 "경기 피드"로 교체**한다.
  GitHub Pages는 index.html이 진입점이므로 파일은 유지하되, hero/feature-card 랜딩을 버리고
  owtv처럼 최신 경기 결과가 바로 보이는 페이지로 만든다. (기존 외부 링크·북마크 호환 유지)
- 계층: **대회(Tournament) → 경기(Match) → 세트(Map)** 를 1급 객체로. 나머지(ELO, 선수, 밴)는
  이 계층을 다른 각도로 집계한 뷰로 재정의.
- 빅뱅 금지: 페이지 단위로 전환하고 각 단계에서 배포 가능 상태 유지.

## 2. 새 사이트 맵

```
index.html          = 경기 피드 (신규 콘텐츠로 교체) ─ 최근 결과·진행중·예정, 지역 필터
├─ match.html?m=<match_id>       경기 상세 (PLAN_04 §3) ─ 세트별 맵·밴·선수 스탯 탭
├─ tournaments.html              대회 허브 (기존 확장)
│    └─ 대회 선택 시 탭: 순위/ELO ─ 경기 목록 ─ 선수 리더보드 ─ 밴 통계
│       (owtv의 tournament 페이지 상당. PLAN_06 §2d 집계 JSON 소비)
├─ teams.html                    팀 프로필 (기존 유지 + 최근 경기 목록 → match.html 링크)
├─ players.html                  선수 산점도 (기존 유지, 데이터 범위 문구 추가 — PLAN_05)
├─ elo.html                      ELO 순위/추이 (기존 유지)
└─ ban-calculator.html           밴 계산기 (기존 유지, 소스를 matches 파생 데이터로 일원화)
```

### 내비게이션 (assets/nav.js)
`Matches(=index) · Tournaments · Teams · Players · ELO · Ban Calculator`
- 기존 "Home" 항목 제거. 로고 클릭 = index(경기 피드).
- 기존 nav의 Tournaments/ELO/Teams/Player Stats/Ban Calculator 순서는 사용 빈도에 맞게 위처럼 재배열.

## 3. index.html (경기 피드) 상세

- 상단: 지역 필터 칩 (All · Korea · NA · EMEA · Japan · Pacific · China · INTL) — owtv의 지역 탭 상당.
- 본문: 날짜 역순 경기 카드 (팀 로고·세트 스코어·대회 badge·phase) → match.html 링크.
  `matches_index.json`만 로드 (상세 JSON은 match.html에서 lazy).
- 사이드/하단 위젯 (기존 홈 요소의 계승): 2026 Global ELO Top5 (elo_rankings.json 재사용) + 각 페이지로의 짧은 링크 행.
  → 기존 홈의 quick-stats 카드(팀 수/밴 레코드 등)는 폐기.
- 예정 경기: S2 진행 중에는 owtv 수집 시 `complete:false` 경기의 startDate로 표시 가능 (선택).

## 4. 전환 단계 (배포 단위)

| 단계 | 작업 | 선행 |
|---|---|---|
| 1 | PLAN_06 데이터 빌드 (matches_index + matches/* + 대회 집계) | PLAN_02 |
| 2 | match.html 신규 (PLAN_04 §3) — 데이터만 있으면 독립 배포 가능 | 1 |
| 3 | index.html을 경기 피드로 교체 + nav 개편 (Home 제거) | 2 |
| 4 | tournaments.html에 경기 목록·선수 리더보드·밴 통계 탭 추가 | 2 |
| 5 | teams.html 최근 경기, players.html 데이터 범위 문구, ban-calculator 소스 일원화 | 3 |

각 단계마다: 로컬 서버 검증(콘솔 에러 0, 6페이지 회귀 확인) → DATA_V 업 → 커밋 → 푸시.

## 5. 공통 리팩터링 (단계 3에 포함)

- 로고 로직(slugify/EXT맵/fallback SVG)을 `assets/team-logos.js`로 통합 — 현재 3개 HTML에 중복.
- i18n: 신규 문자열 EN/KR 추가 (`assets/i18n.js`, `data-i18n` 패턴).
- style.css의 기존 CSS 변수 재사용, 카드 컴포넌트 클래스(`.feature-card`→`.match-card`) 정리.

## 6. 결정 필요 사항 (사용자 확인)

1. index = 경기 피드 안 vs. index = tournaments로 리다이렉트 안 → **권장: 경기 피드** (owtv 사용 패턴과 동일, 재방문 가치 높음)
2. 예정 경기(미완료) 노출 여부 — owtv 수집 주기에 의존
3. 기존 홈의 feature-card 3개(ELO/Players/Ban) 완전 제거 vs. 피드 하단에 축소 유지
