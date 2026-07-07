# 작업 프로세스 규칙

## ⚠️ 데이터 검증 원칙
사용자가 제공한 정보(날짜, 순서, 팀 구성, 수치 등)가 데이터로 검증 가능한 영역이라면,
**작업 시작 전 원본 데이터로 직접 검증 후 진행**한다.

- 검증 출처: `Elo-Rating/*.csv`, `OWCStats/**/*.csv`, `assets/data/*.json`
- 불일치 시: 데이터 근거를 제시하고 사용자 확인을 받은 뒤 진행
- 일치 시: "검증 OK" 한 줄만 알리고 바로 진행
- 예외: 사용자가 "검증 생략" 명시, 또는 검증 불가 영역(주관·미래·외부 정보)

**이유**: 잘못된 데이터를 코드에 반영하면 사이트 전체에 영향이 퍼져 되돌리기 어렵다.

---

## ⚠️ ELO 승계는 사용자가 직접 검토
팀 합병·승계·리브랜드로 ELO를 이전할 때는, 수치를 임의로 결정하거나 자동 적용하지 않는다.

**절차**:
1. 승계 후보 팀과 ELO 수치를 사용자에게 제시
2. 사용자 확인(승인/수정) 후에만 `inject_stage2_initial_elo.py` 또는 JSON에 반영

**이유**: 승계 여부와 수치는 경쟁 맥락·합병 경위에 따라 판단이 갈리며, 사용자가 현장 정보를 더 잘 안다.

---

## GitHub 배포
```bash
git add <파일>
git commit -m "설명"
git push origin main
# → 자동으로 https://antkingow.github.io/owcstats-site/ 배포
```

## 캐시 버스팅
- `nav.js` 상단 `window.DATA_V` 버전 번호 올리기
- 모든 HTML의 `<script src="assets/nav.js?v=YYYYMMDD*">` 도 맞춰서 변경
- JSON fetch 호출은 `?v=${window.DATA_V||'0'}` 형태로 이미 처리됨
