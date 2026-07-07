# PLAN 02 — owtv.gg에서 2026 Stage 2 경기 결과·맵·밴·선수 스탯 수집

> 아래의 URL·스키마는 **2026-07-08에 실제 HTTP 요청으로 검증**한 사실이다.
> 사이트 구조가 바뀌었을 수 있으니, 수행 시 먼저 §2의 샘플 URL 1개로 스키마가 유효한지 재확인할 것.

## 1. 소스 개요 (검증된 사실)

- owtv.gg는 **Next.js(App Router) + Payload CMS** 구성. 페이지 HTML 안의
  `self.__next_f.push([1,"…"])` 청크(flight data)에 **전체 데이터가 JSON으로 embedded** 되어 있다.
- 별도 공개 REST API는 없음 (`/api/matches` → 404). `/api/media/file/*`는 이미지 전용.
- **로그인 불필요, 일반 GET으로 수집 가능.** `User-Agent: Mozilla/5.0` 헤더만 넣으면 200 응답.
- ⚠️ **맵별 경기 시간(duration) 데이터는 없다** — per-10 스탯 계산 불가. PLAN_05 참조.
- 수집 매너: 요청 간 1~2초 sleep, 총 요청 수는 토너먼트 6 + 경기 ~150건 수준이므로 부담 없음.

## 2. URL 구조 (전부 검증됨)

### 토너먼트 페이지 — 경기 목록의 소스
```
https://owtv.gg/tournaments/korea-stage-2-owcs-2026      (200 확인)
https://owtv.gg/tournaments/na-stage-2-owcs-2026
https://owtv.gg/tournaments/emea-stage-2-owcs-2026
https://owtv.gg/tournaments/china-stage-2-owcs-2026
https://owtv.gg/tournaments/pacific-stage-2-owcs-2026    (200 확인)
https://owtv.gg/tournaments/japan-stage-2-owcs-2026      (200 확인)
https://owtv.gg/tournaments/midseason-championship-owcs-2026
```

### 경기 페이지 — 맵·밴·선수 스탯의 소스
```
https://owtv.gg/matches/<slug>
예: https://owtv.gg/matches/korea-stage-2-owcs-2026-regular-season-week-4-cr-vs-zeta  (200, 스키마 검증 완료)
```
slug는 토너먼트 페이지 flight data의 match doc `slug` 필드에서 얻는다 (직접 조합하지 말 것).

## 3. Flight data 추출 방법 (핵심)

HTML 원문에서 flight 청크를 JS 문자열 리터럴로 디코딩 후 이어붙이면 순수 JSON 조각들이 나온다:

```python
import re, json, time, urllib.request

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

CHUNK = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')

def flight_payload(html: str) -> str:
    # 각 청크는 JS 문자열 리터럴 → json.loads로 unescape 후 연결
    return "".join(json.loads('"' + m + '"') for m in CHUNK.findall(html))

def extract_balanced(payload: str, anchor: str, open_ch: str) -> str:
    """anchor 바로 뒤에 오는 균형 잡힌 JSON 배열/오브젝트 문자열을 반환.
    open_ch: '[' 또는 '{'. 문자열 내부의 괄호는 인용부호 상태를 추적해 무시."""
    start = payload.index(anchor) + len(anchor)
    assert payload[start] == open_ch
    close = {'[': ']', '{': '}'}[open_ch]
    depth, in_str, esc = 0, False, False
    for i in range(start, len(payload)):
        c = payload[i]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
        elif c == '"': in_str = True
        elif c == open_ch: depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return payload[start:i+1]
    raise ValueError("unbalanced")
```

## 4. 데이터 스키마 (실측 — 필드명 그대로 인용)

### 4a. 토너먼트 페이지: 경기 목록
payload 안에 라운드별로 `"matches":{"docs":[ … ]}` 블록이 여러 개 존재. match doc:

```json
{"id":284, "tournamentPhase":17,
 "slug":"korea-stage-2-owcs-2026-regular-season-week-4-cr-vs-zeta",
 "team1":33, "team2":34, "team1Score":2, "team2Score":3,
 "winningTeam":34, "resultType":"normal",
 "startDate":"2026-06-28T09:00:00.000Z", "complete":true, "firstTo":3,
 "round":19, "maps":{"docs":[3111,3110,2964,2963,2962]}, "regions":[1]}
```
- `complete:true`인 것만 수집. `team1`/`team2`/`winningTeam`은 팀 **숫자 id**.
- 라운드 doc: `{"id":19,"tournamentPhase":17,"name":"Week 4","order":4}` — phase/주차 매핑용.
- phase 이름(Regular Season / Last Chance Qualifier / Playoffs / Seeding Decider / Regional Playoffs)도 payload에 존재. `tournamentPhase` id로 연결.

### 4b. 경기 페이지: 팀 정보 (id → 이름 해석)
경기 페이지 payload의 `"team1":{`, `"team2":{` 오브젝트:
```json
{"id":33, "name":"Crazy Raccoon", "initials":"CR", "region":"korea",
 "tier":"1", "nationality":"jp", "image":{ …로고 URL… }}
```

### 4c. 경기 페이지: 맵 결과 + **히어로 밴**
`"maps":{"docs":[` 안의 map doc (경기 페이지에는 전체 필드가 들어 있음):
```json
{"id":"3111", "mapNumber":5, "mapName":"Runasapi",
 "team1Score":51.52, "team2Score":135.44,
 "team1BanName":"Shion", "team1BanImageUrl":"https://owtv.gg/api/media/file/Icon-Shion.webp",
 "team2BanName":"Lúcio", "team2BanImageUrl":"…",
 "pickedBy":"team1", "firstBannedBy":"team1",
 "complete":true, "isLive":false}
```
- ⚠️ `team1Score`/`team2Score`가 **소수**인 경우: Control/Flashpoint류의 진행률 점수. 맵 승자는 큰 쪽.
- 밴: 맵마다 팀당 1개 (`team1BanName`/`team2BanName`), `firstBannedBy`가 선밴 팀.
- `mapName`이 "TBD"이고 `complete:false`면 미진행 맵 — 스킵.

### 4d. 경기 페이지: 선수 스탯 (맵 단위)
`"stats":[` 배열:
```json
{"id":"26908", "mapId":"3111", "personId":"101", "personName":"KNIFE",
 "teamId":"34", "role":"DAMAGE",
 "eliminations":36, "assists":2, "deaths":9,
 "damageDealt":14401, "healingDone":64, "damageMitigated":2145,
 "fantasyScore":10, "nationality":"kr"}
```
- `role`: `TANK` / `DAMAGE` / `SUPPORT` (사이트 표기 Tank/DPS/Support로 변환 필요).
- 시간(분) 필드 **없음**.

## 5. 수집 절차

1. **토너먼트 7개 페이지** fetch → payload에서 모든 `"matches":{"docs":[`를 `extract_balanced`로 파싱
   → `complete==true`인 match의 `slug`, 점수, `startDate`, phase/round 이름 수집.
2. 각 match slug에 대해 **경기 페이지** fetch (1초 sleep) →
   `team1`/`team2` 오브젝트, `"maps":{"docs":[`, `"stats":[` 파싱.
3. 원본 보존: 파싱 결과를 그대로 `Elo-Rating/owtv_raw/2026_stage2/<slug>.json`으로 저장
   (재파싱 없이 재가공 가능하도록). 이 폴더는 .gitignore에 추가해도 좋고 커밋해도 좋음(용량 작음).
4. 산출물 3종 생성:

### 산출물 ① 맵 결과 CSV — ELO 파이프라인 입력 (PLAN_03에서 사용)
`Elo-Rating/OWCS_2026_GLOBAL_MAP_RESULTS.csv`의 **기존 헤더에 정확히 맞춰** append용 CSV 생성:
```
global_map_order,event_id,event_region,season_year,stage_label,week_label,day_label,match_date,
match_order,game_number,team_a,team_b,winner,loser,map_name,map_mode,series_format,source_url,source_note
```
- `event_id` 규칙(기존 관례): `owcs_2026_asia_s2_korea`, `owcs_2026_na_s2` 등 기존 Stage 1 id들을 참조해 동일 패턴 유지.
- `winner`: map doc에서 점수 큰 팀. 무승부(동점)는 기존 CSV의 draw 표기 방식을 확인 후 따를 것.
- `map_mode`: mapName → 모드 매핑 테이블 필요 (기존 CSV에서 map_name→map_mode 쌍을 추출해 재사용).
- `source_url`: `https://owtv.gg/matches/<slug>`, `source_note`: `owtv_scrape`.
- ⚠️ **중국 Swiss Stage 결과는 ELO 반영 제외** ([ELO_POLICY.md](../ELO_POLICY.md)). phase 이름으로 필터.

### 산출물 ② 밴 이벤트 — ban-calculator용
기존 `assets/data/ban_history.json`의 record 스키마에 맞춰 변환:
```json
{"region":"Korea", "match_file":"owtv:<slug>", "game_num":"5",
 "team_initial":"<firstBannedBy 팀명>", "hero_initial":"<선밴 히어로>",
 "team_followup":"<상대 팀명>", "hero_followup":"<후밴 히어로>"}
```
- `firstBannedBy=="team1"`이면 initial=team1Ban, followup=team2Ban. 반대면 반대로.
- 생성 스크립트는 `parse_ban_history.py`·`assets/data/update_clash_bans.py`(Clash 때 동일 작업의 선례) 참고.

### 산출물 ③ 선수 맵 스탯 CSV — PLAN_05 입력
`OWCStats/OWCStats/STAGE2_OWTV_CSV/stage2_player_map_stats.csv`:
```
region,event_id,match_slug,match_date,game_number,map_name,team,player,role,
E,A,D,DMG,H,MIT,fantasy,Minutes
```
- owtv 필드 매핑: eliminations→E, assists→A, deaths→D, damageDealt→DMG, healingDone→H, damageMitigated→MIT.
- **Minutes 컬럼은 공란**으로 둔다 (사용자가 나중에 직접 채움 — PLAN_05).

## 6. 팀명 정규화 (필수)

owtv `name` ↔ 사이트 canonical 이름이 다른 사례가 확인됨. 최소 매핑:
| owtv | 사이트/CSV canonical |
|---|---|
| Zeta Division | ZETA DIVISION |
| ZANSIDE GAMING | ZANSIDE GAMING (동일) |
| O2 Blast | O2 BLAST ← 기존 CSV 표기 확인 후 결정 |

수집 후 `OWCS_2026_GLOBAL_ELO_FINAL.csv`의 team 컬럼과 전수 대조해 **불일치 목록을 만들어 사용자에게 보고**하고, 확정된 매핑을 `build_site_data.py`의 `TEAM_NAME_ALIASES`에 추가한다.

## 7. 검증 체크리스트

- [ ] Korea Stage 2 정규시즌: 9팀 × 8경기 / 2 = **36경기** 수집됐는지 (owtv 순위표 W-L 합계와 대조: CR 7-1, ZETA 7-1, T1 6-2, FLC 6-2, O2 4-4, ZSG 3-5, CB 2-6, SB 1-7, PF 0-8)
- [ ] 맵 수 = match doc의 maps.docs 길이와 파싱된 map 수 일치
- [ ] 각 완료 맵에 밴 2개(팀당 1개) 존재
- [ ] 선수 스탯: 완료 맵당 10~14행 (양팀 5인 + 교체)
- [ ] 점수 검증 샘플: CR vs ZETA (Week 4) = 2:3, ZETA 승 (winningTeam=34=ZETA)
