# PLAN 01 — 사이트 검토 이슈 해결

2026-07-08 전 페이지 렌더링 검증(콘솔 에러 0, 네트워크 실패 0) 후 발견된 이슈 목록과 해결 방법.
아래 ✅ 항목은 이미 로컬 커밋(`43bcb97`)으로 해결됨. 남은 항목만 수행하면 된다.

## ✅ 완료된 항목 (커밋 43bcb97, 푸시 대기)

| # | 이슈 | 해결 내용 |
|---|---|---|
| 1 | `data_notes/*.md` 3개가 untracked (CLAUDE.md가 링크하는데 저장소에 없음) | PROCESS_RULES/ARCHITECTURE/ELO_POLICY.md 커밋 |
| 2 | `index.html` "Ban Records 315" 하드코딩 | `ban_history.json`을 fetch해 `records.length`(현재 518)와 지역 라벨을 동적 계산. 요소 id: `ban-count`, `ban-regions` |
| 3 | `players.html` 산점도 축에 음수 눈금(-1514.3 등) 표시 | 렌더 함수의 `xMin`/`yMin`을 `Math.max(0, …)`로 클램프 (per-10 스탯은 음수 불가) |
| 4 | 대용량 로고 (huneng 2.4MB, tokyo-ta1yos 1.8MB 등 9개) | PIL로 최대 512px 리사이즈 + PNG optimize, 파일명 유지. 합계 6.9MB → 1.5MB |
| 5 | 미사용 중복 로고 `twisted-mind.png` (twisted-minds.png와 SHA-256 동일) | 삭제. 로고는 `slugify(팀명)`으로 참조되므로 단수형 파일은 참조 불가능했음 |

## ⬜ 남은 작업

### A. 로컬 커밋 푸시 (사용자 확인 후)
```bash
cd owcstats-site
git push origin main
```
- HTML만 변경 시 캐시 버스팅 불필요. JSON 데이터 변경이 없으므로 DATA_V 유지.
- 푸시 후 https://antkingow.github.io/owcstats-site/ 에서 홈 "Ban Records"가 518로 나오는지,
  players.html 축 최소값이 0 이상인지 확인.

### B. 로고 참조 규칙 문서화 (선택)
로고 로딩 규칙이 teams/players/tournaments.html에 각각 중복 구현되어 있다:
- `slug = LOGO_SLUG_OVERRIDES[팀명] || slugify(팀명)`
- `ext = LOGO_EXT_MAP[slug] || 'png'` (webp/svg 예외는 각 파일 상단 맵에 등록)
- 로드 실패 시 이니셜 원형 SVG fallback

새 팀 로고 추가 절차: ① `assets/logos/<slug>.png` (512px 이하, 200KB 이하) 저장
② 확장자가 png가 아니면 **세 HTML 모두**의 EXT 맵에 등록 ③ 팀명 slug가 규칙과 다르면 OVERRIDES에 등록.
장기적으로는 이 맵들을 `assets/logos.js` 하나로 통합하는 리팩터링 권장 (PLAN_04에서 함께 수행).

### C. 중복 로고 잔여 확인 (선택)
`jd-gaming.webp` == `jdg-gaming.webp` (동일 파일 2KB). 두 slug 모두 EXT 맵에 등록되어 있어
어느 팀명 표기가 와도 동작하도록 의도된 것으로 보임 — **삭제하지 말 것**. 통합하려면 참조 slug를 먼저 통일해야 한다.

### D. 검증 방법 (수행 후 필수)
```bash
# 로컬 정적 서버로 확인 (아무 정적 서버나 가능)
python -m http.server 3333 --directory owcstats-site
```
1. 6개 페이지(index/elo/players/teams/tournaments/ban-calculator) 브라우저 콘솔 에러 0 확인
2. teams.html에서 `[...document.images].filter(i=>i.complete&&!i.naturalWidth)` == 빈 배열 (로고 깨짐 없음)
3. index.html quick-stats 4개 카드 값이 모두 실데이터로 채워지는지
