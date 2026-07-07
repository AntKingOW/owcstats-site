# 사이트 아키텍처

## 관련 레포 (같은 상위 폴더에 나란히 클론)
```
owcstats-site/   ← 사이트 파일 (이 레포)
OWCStats/        ← 선수 통계 원본 데이터 (github.com/AntKingOW/OWCStats)
Elo-Rating/      ← ELO 원본 데이터    (github.com/AntKingOW/Elo-Rating)
```

## 사이트 구조
```
owcstats-site/
├── index.html              ← 홈
├── tournaments.html        ← 대회 허브 (연도→스테이지→지역 3단계 필터)
├── elo.html                ← ELO 전체 순위
├── teams.html              ← 팀별 ELO 히스토리
├── players.html            ← 선수 통계 (Scatter + Rankings)
├── ban-calculator.html     ← 밴 계산기
├── assets/
│   ├── style.css           ← 공통 다크 테마
│   ├── nav.js              ← 공통 네비게이션 (모든 페이지 자동 삽입)
│   ├── logos/              ← 팀 로고 (slug 기반 파일명, png/webp/svg)
│   ├── heroes/             ← 영웅 초상화
│   └── data/
│       ├── elo_rankings.json     ← ELO 순위 (2024/2025/2026)
│       ├── elo_history.json      ← ELO 히스토리 (차트용)
│       ├── tournaments_meta.json ← 연도·지역별 스테이지 메타
│       ├── player_stats.json     ← 선수 통계
│       ├── ban_summary.json      ← 팀별 밴 요약
│       └── ban_events.json       ← 게임별 밴 이벤트
└── data_notes/             ← 운영 문서 (이 폴더)
```

## 디자인 토큰 (style.css :root)
```css
--bg: #08141f
--panel: #0f2236
--panel2: #132a42
--border: #1a3a5c
--text: #ddeaf7
--text-dim: #7a9bb5
--accent: #f5a524      ← 주황 (주요 강조)
--accent2: #4da6ff     ← 파랑 (보조 강조)
--good: #3ddc84
--bad: #ff5c5c
```

## 페이지별 특이사항

### tournaments.html
- 연도 탭 → 스테이지 카드 행 → (지역 대회만) 지역 탭 → ELO + 선수 통계
- `tournaments_meta.json`의 `type:"international"` 스테이지는 지역 탭 숨김, 전체 참가팀 표시
- `hasStageData(stage)`: elo_history에서 stage.events 내 event_id를 가진 항목 존재 여부로 활성화 판단
- `result:"start"` 항목이 S2 활성화의 트리거 (inject_stage2_initial_elo.py가 주입)
- LOGO_EXT: `{ cheeseburger:webp, jd-gaming:webp, ..., poker-face:svg, team-falcons:svg, the-gatos-guapos:svg }`

### players.html
- 좌측 사이드바: 뷰 탭(Scatter/Rankings) + 필터
- `slugify()`: 아포스트로피/점 → `-`, 연속 `-` 합침, 앞뒤 `-` 제거
  예) "Anyone's Legend" → "anyone-s-legend"

### ban-calculator.html
- `heroSlug()`: `"D.Va"` → `"d-va"`, `"Soldier: 76"` → `"soldier--76"`
- ban_summary.json 로드 후 밴 추천 칩 + 사이드 인사이트 패널 표시

### ban_summary.json 구조
```json
{ "region": "Korea", "team": "Crazy Raccoon", "map_mode": "Control",
  "hero": "Zarya", "bans_made": 5, "bans_received": 3,
  "initial_bans_made": 3, "follow_up_bans_made": 2 }
```
