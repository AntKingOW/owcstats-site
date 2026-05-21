# OWCStats.com — Claude Code 컨텍스트

## 프로젝트 개요
Overwatch Champions Series(OWCS) 2026 통계 사이트.
GitHub Pages로 배포 중: https://antkingow.github.io/owcstats-site/
레포: https://github.com/AntKingOW/owcstats-site

## 관련 레포 (같은 상위 폴더에 나란히 클론)
```
owcstats-site/   ← 사이트 파일 (이 레포)
OWCStats/        ← 선수 통계 원본 데이터 (github.com/AntKingOW/OWCStats)
Elo-Rating/      ← ELO 원본 데이터    (github.com/AntKingOW/Elo-Rating)
```

## 사이트 구조
```
owcstats-site/
├── index.html              ← 홈 (ELO 요약 + 네비게이션)
├── clash.html              ← Champion Clash 2026 국제전 전용 페이지
├── elo.html                ← ELO 전체 순위
├── players.html            ← 선수 Scatter 통계
├── ban-calculator.html     ← 밴 계산기 + 인라인 밴 추천
├── assets/
│   ├── style.css           ← 공통 다크 테마 (CSS 변수: --bg, --panel, --accent 등)
│   ├── nav.js              ← 공통 네비게이션 (모든 페이지 자동 삽입)
│   ├── logos/              ← 팀 로고 이미지 (slug 기반 파일명)
│   ├── heroes/             ← 영웅 초상화 이미지
│   └── data/
│       ├── elo_rankings.json     ← ELO 순위 (2024/2025/2026)
│       ├── elo_history.json      ← ELO 히스토리 (차트용)
│       ├── player_stats.json     ← 선수 통계 (scatter용)
│       ├── ban_summary.json      ← 팀별 밴 요약 (bans_made / bans_received)
│       └── ban_events.json       ← 게임별 밴 이벤트 (per-game)
├── build_site_data.py      ← CSV/MD → JSON 변환 스크립트
├── parse_ban_history.py    ← 밴 결과 MD → ban_history.json
├── parse_korea_to_csv.py   ← 한국 MD 통계 → CSV
└── audit_data.py           ← 데이터 품질 검수 리포트
```

## 디자인 토큰 (style.css :root)
```css
--bg: #08141f
--panel: #0f2236
--panel2: #132a42
--border: #1a3a5c
--text: #ddeaf7
--text-dim: #7a9bb5
--accent: #f5a524      ← 주요 강조색 (주황)
--accent2: #4da6ff     ← 보조 강조색 (파랑)
--good: #3ddc84
--bad: #ff5c5c
```

## 주요 페이지별 특이사항

### clash.html — Champion Clash 2026
- 참가 8팀: Twisted Minds(EMEA), Virtus.pro(EMEA), Dallas Fuel(NA), Spacestation Gaming(NA),
  Crazy Raccoon(Korea), ZETA DIVISION(Korea), Weibo Gaming(China), All Gamers(China)
- 좌측 사이드바(220px) + 우측 콘텐츠 구조
- 섹션: Overview / ELO Rankings / Player Stats / Ban Analysis
- Ban Analysis: bans_made(🔴 내가 밴한 영웅) / bans_received(🛡️ 상대가 나한테 쓴 밴) 토글
- 중국 팀(Weibo Gaming, All Gamers)은 선수 데이터 없음 → 안내 메시지 표시

### players.html — 선수 Scatter
- 좌측 사이드바(240px): 뷰 탭(Scatter/Rankings) + 필터
- SVG scatter plot: 팀 로고 원형 클립 + 플레이어 이름 텍스트 레이블
- slugify() 함수: 아포스트로피/점 → `-` 로 변환 (제거 X)
  예) "Anyone's Legend" → "anyone-s-legend", "D.Va" → "d-va"

### ban-calculator.html — 밴 계산기
- 기존 BanCalculatorOW 로직 유지, 사이트 다크 테마로 흡수
- ban_summary.json 로드 후 영웅 선택 모달에 인라인 추천 표시
  A) 추천 칩 (히어로 그리드 위)
  B) 사이드 인사이트 패널 (bans_made / bans_received / 상대 밴 예측)
- heroSlug(): 아포스트로피/점 → `-` 변환
  예) "D.Va" → "d-va", "Soldier: 76" → "soldier--76"

### ban_summary.json 구조
```json
{ "region": "Korea", "team": "Crazy Raccoon", "map_mode": "Control",
  "hero": "Zarya", "bans_made": 5, "bans_received": 3,
  "initial_bans_made": 3, "follow_up_bans_made": 2 }
```

## GitHub 업로드 방법
```bash
git add .
git commit -m "수정 내용"
git push origin main
# → 자동으로 https://antkingow.github.io/owcstats-site/ 에 배포
```

## 지금까지 완료된 작업
- [x] Phase 0: 데이터 검수 리포트 (audit_data.py)
- [x] Phase 1: 밴 데이터 파싱 (parse_ban_history.py)
- [x] Phase 2: 사이트 구조 + 공통 CSS/nav + 데이터 변환 스크립트
- [x] Phase 3: ELO 순위 페이지 (elo.html)
- [x] Phase 4: 선수 Scatter 통계 페이지 (players.html)
- [x] Phase 5: 밴 계산기 + 인라인 예측 (ban-calculator.html)
- [x] Phase 6: GitHub Pages 배포 완료
- [x] Champion Clash 2026 전용 페이지 (clash.html)
