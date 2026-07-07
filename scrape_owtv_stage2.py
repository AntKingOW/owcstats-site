# -*- coding: utf-8 -*-
"""
scrape_owtv_stage2.py — owtv.gg에서 2026 Stage 2(+Midseason) 경기 수집 (PLAN_02)

방식: 페이지 HTML의 Next.js flight data(self.__next_f.push)에서 embedded JSON 추출.
출력: owtv_raw/2026_stage2/<slug>.json  (경기당 1파일: meta/teams/maps/stats)
      owtv_raw/2026_stage2/_index.json  (수집 요약)
"""
import json, re, time, sys, urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "owtv_raw" / "2026_stage2"
OUT.mkdir(parents=True, exist_ok=True)

TOURNAMENTS = [
    "korea-stage-2-owcs-2026",
    "na-stage-2-owcs-2026",
    "emea-stage-2-owcs-2026",
    "china-stage-2-owcs-2026",
    "pacific-stage-2-owcs-2026",
    "japan-stage-2-owcs-2026",
    "midseason-championship-owcs-2026",
]

CHUNK = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (OWCStats data sync)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")


def flight_payload(html):
    return "".join(json.loads('"' + m + '"') for m in CHUNK.findall(html))


def extract_balanced(payload, start):
    """payload[start]가 '[' 또는 '{'인 위치에서 균형 잡힌 JSON 조각을 반환."""
    open_ch = payload[start]
    close = {"[": "]", "{": "}"}[open_ch]
    depth, in_str, esc = 0, False, False
    for i in range(start, len(payload)):
        c = payload[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        elif c == '"': in_str = True
        elif c == open_ch: depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return payload[start:i + 1]
    raise ValueError("unbalanced json")


def extract_after(payload, anchor, from_idx=0):
    i = payload.index(anchor, from_idx)
    return extract_balanced(payload, i + len(anchor) - 1), i


def collect_match_docs(payload):
    """토너먼트 페이지의 모든 "matches":{"docs":[...] 배열을 파싱."""
    docs, pos = [], 0
    while True:
        i = payload.find('"matches":{"docs":[', pos)
        if i < 0:
            break
        frag = extract_balanced(payload, i + len('"matches":{"docs":'))
        pos = i + len(frag)
        try:
            arr = json.loads(frag)
            docs += [d for d in arr if isinstance(d, dict) and d.get("slug")]
        except json.JSONDecodeError:
            pass
    return docs


def scrape_match(slug):
    html = fetch(f"https://owtv.gg/matches/{slug}")
    p = flight_payload(html)
    anchor = f'"slug":"{slug}","team1":{{'
    t1_frag, at = extract_after(p, anchor[:-1] + "{")
    team1 = json.loads(t1_frag)
    t2_frag, _ = extract_after(p, '"team2":{', at)
    team2 = json.loads(t2_frag)
    maps_frag, _ = extract_after(p, '"maps":{"docs":[', at)
    # extract_after는 '['부터 균형 배열을 돌려줌
    maps = json.loads(maps_frag)
    try:
        stats_frag, _ = extract_after(p, '"stats":[', at)
        stats = json.loads(stats_frag)
    except ValueError:
        stats = []
    return {"team1": team1, "team2": team2, "maps": maps, "stats": stats}


def main():
    index = []
    upcoming = []
    for t in TOURNAMENTS:
        try:
            html = fetch(f"https://owtv.gg/tournaments/{t}")
        except Exception as e:
            print(f"[skip] {t}: {e}")
            continue
        docs = collect_match_docs(flight_payload(html))
        done = {d["slug"]: d for d in docs if d.get("complete")}
        # 미완료 경기 = 예정 일정. 팀은 숫자 id 또는 placeholder(Winner of G1 등).
        for d in docs:
            if d.get("complete") or d["slug"] in done:
                continue
            upcoming.append({
                "slug": d["slug"], "tournament": t,
                "startDate": d.get("startDate"), "firstTo": d.get("firstTo"),
                "team1": d.get("team1"), "team2": d.get("team2"),
                "team1Placeholder": d.get("team1Placeholder"),
                "team2Placeholder": d.get("team2Placeholder"),
            })
        print(f"{t}: {len(docs)} matches in payload, {len(done)} complete, "
              f"{sum(1 for d in docs if not d.get('complete'))} upcoming")
        time.sleep(1)
        for slug, doc in done.items():
            out = OUT / f"{slug}.json"
            meta = {
                "slug": slug, "tournament": t,
                "team1Score": doc.get("team1Score"), "team2Score": doc.get("team2Score"),
                "winningTeam": doc.get("winningTeam"), "startDate": doc.get("startDate"),
                "firstTo": doc.get("firstTo"), "resultType": doc.get("resultType"),
            }
            if out.exists():
                # 이미 수집됨 — meta만 갱신
                data = json.loads(out.read_text(encoding="utf-8"))
                data["meta"] = meta
                out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                index.append({**meta, "cached": True})
                continue
            try:
                detail = scrape_match(slug)
            except Exception as e:
                print(f"  [fail] {slug}: {e}")
                index.append({**meta, "error": str(e)})
                time.sleep(1)
                continue
            detail["meta"] = meta
            out.write_text(json.dumps(detail, ensure_ascii=False), encoding="utf-8")
            index.append(meta)
            print(f"  ok {slug} ({meta['team1Score']}:{meta['team2Score']}, maps={len(detail['maps'])}, stats={len(detail['stats'])})")
            time.sleep(1.2)
    (OUT / "_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    # 예정 경기의 팀 id -> 이름 해석: 완료 경기 raw의 team1/team2 오브젝트에서 사전 구축
    team_names = {}
    for f in OUT.glob("*.json"):
        if f.name.startswith("_"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for tk in ("team1", "team2"):
                obj = data.get(tk)
                if isinstance(obj, dict) and obj.get("id") is not None:
                    team_names[obj["id"]] = obj.get("name")
        except (json.JSONDecodeError, OSError):
            pass
    for u in upcoming:
        for tk, pk in (("team1", "team1Placeholder"), ("team2", "team2Placeholder")):
            v = u.get(tk)
            if isinstance(v, dict):
                u[tk + "Name"] = v.get("name")
            elif isinstance(v, int):
                u[tk + "Name"] = team_names.get(v)
            else:
                u[tk + "Name"] = None
            if not u[tk + "Name"]:
                u[tk + "Name"] = u.get(pk) or "TBD"
    (OUT / "_upcoming.json").write_text(json.dumps(upcoming, ensure_ascii=False, indent=1), encoding="utf-8")
    errs = [x for x in index if x.get("error")]
    print(f"done: {len(index)} matches, {len(errs)} errors, {len(upcoming)} upcoming")


if __name__ == "__main__":
    sys.exit(main())
