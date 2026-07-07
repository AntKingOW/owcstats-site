# -*- coding: utf-8 -*-
"""
build_matches.py — 매치/세트(맵) 단위 데이터 빌더 (PLAN_06)

MAP_RESULTS CSV를 스파인으로, 선수 맵 스탯 CSV(Korea/Asia·EMEA·NA·Clash)와
밴 이벤트 JSON을 조인해 경기별 JSON을 생성한다.

출력:
  assets/data/matches_index.json      경기 목록 (피드/목록 페이지용)
  assets/data/matches/<match_id>.json 경기 상세 (맵·밴·선수 스탯)
  ../data_notes/match_join_report.md  조인 실패/경고 보고서 (사용자 검토용)
"""
import csv, json, re, unicodedata
from pathlib import Path
from collections import defaultdict

SITE = Path(__file__).parent
BASE = SITE.parent
ELO_DIR = BASE / "Elo-Rating"
STATS_DIR = BASE / "OWCStats" / "OWCStats"
OUT_DIR = SITE / "assets" / "data"
MATCH_DIR = OUT_DIR / "matches"
MATCH_DIR.mkdir(parents=True, exist_ok=True)

REGION_LABEL = {
    "korea": "Korea", "na": "NA", "emea": "EMEA", "japan": "Japan",
    "pacific": "Pacific", "china": "China", "international": "INTL",
}

ROLE_MAP = {"TANK": "Tank", "DAMAGE": "DPS", "SUPPORT": "Support",
            "Tank": "Tank", "DPS": "DPS", "Support": "Support"}

report = {"warn": [], "unmatched_stats": [], "unmatched_bans": [], "info": []}


def norm(name: str) -> str:
    """정규화 키: 악센트 제거(Esperança→esperanca), 소문자, 영숫자만."""
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


# 맵명 표기 변형 (소스별 축약 표기 → 정식 명칭 키)
MAP_ALIASES = {"gibraltar": "watchpointgibraltar", "watchpoint": "watchpointgibraltar"}


def mnorm(name: str) -> str:
    """맵명 정규화 키 (norm + 별칭 해소)."""
    k = norm(name)
    return MAP_ALIASES.get(k, k)


def _clean_phase(s: str, date: str) -> str:
    s = re.sub(r"\s*\[[^\]]*\]", "", s)        # [MANUAL] 등 주석 제거
    s = s.replace(date, "")                     # 날짜는 meta.date로 따로 표시되므로 중복 제거
    return re.sub(r"\s{2,}", " ", s).strip(" ·-")


# ── 1. 스파인: MAP_RESULTS → 매치 뼈대 ────────────────────────────────────────

def build_spine():
    matches = {}  # match_id -> match dict
    path = ELO_DIR / "OWCS_2026_GLOBAL_MAP_RESULTS.csv"
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r["event_id"], r["match_date"], int(r["match_order"]))
            mid = f"{r['event_id']}__{r['match_date']}_{int(r['match_order']):02d}"
            m = matches.get(mid)
            if m is None:
                m = matches[mid] = {
                    "id": mid,
                    "event_id": r["event_id"],
                    "region": REGION_LABEL.get(r["event_region"], r["event_region"]),
                    "stage": r["stage_label"],
                    # 표시용 phase: 주석성 대괄호([MANUAL] 등)와 match_date 중복 표기 제거
                    "phase": _clean_phase(
                        " ".join(x for x in [r["week_label"], r["day_label"]] if x),
                        r["match_date"]),
                    "date": r["match_date"],
                    "match_order": int(r["match_order"]),
                    "team1": r["team_a"], "team2": r["team_b"],
                    "format": r["series_format"],
                    "source_url": r["source_url"],
                    "maps": [],
                }
            # 맵마다 team_a/team_b 순서가 바뀔 수 있으므로 매치 기준으로 승자 인덱스 계산
            t1, t2 = norm(m["team1"]), norm(m["team2"])
            w = norm(r["winner"])
            winner_idx = 1 if w == t1 else 2 if w == t2 else 0
            if winner_idx == 0:
                report["warn"].append(f"spine: winner '{r['winner']}' not in ({m['team1']},{m['team2']}) mid={mid}")
            m["maps"].append({
                "n": int(r["game_number"]),
                "name": r["map_name"], "mode": r["map_mode"],
                "winner": winner_idx,
                "ban1": None, "ban2": None, "firstBan": None,
                "duration_min": None, "stats_available": False,
            })
    for m in matches.values():
        m["maps"].sort(key=lambda x: x["n"])
        m["score1"] = sum(1 for g in m["maps"] if g["winner"] == 1)
        m["score2"] = sum(1 for g in m["maps"] if g["winner"] == 2)
        m["winner"] = 1 if m["score1"] > m["score2"] else 2 if m["score2"] > m["score1"] else 0
    print(f"spine: {len(matches)} matches, {sum(len(m['maps']) for m in matches.values())} maps")
    return matches


# ── 2. 조인 인덱스 ────────────────────────────────────────────────────────────

def index_by_pair(matches):
    """팀쌍(normalized frozenset) -> [match] — 스탯 CSV 조인용."""
    idx = defaultdict(list)
    for m in matches.values():
        idx[frozenset((norm(m["team1"]), norm(m["team2"])))].append(m)
    return idx


def phase_hint(match_id_src: str):
    """스탯 CSV의 MatchId에서 정규시즌/포스트시즌 힌트 추출.
    returns: 'regular' | 'post' | None"""
    s = match_id_src.lower()
    if any(k in s for k in ("playoff", "lcq", "seeding", "_sd_", "last_chance")):
        return "post"
    if any(k in s for k in ("week", "group")):
        return "regular"
    return None


# 자동 판별 불가로 수동 확정한 매핑 (근거: NA S1 플레이오프 브래킷 일정 —
# UB Final 04-11(3:1, 4맵=CSV와 일치), LB Final은 SSG-TL 재대결 중 나중(04-12) 경기)
MANUAL_MATCH_OVERRIDES = {
    "na_owcs_na_2026_playoff_upper_bracket_final": "owcs_2026_na_s1_playoffs__2026-04-11_03",
    "na_owcs_na_2026_playoff_lower_bracket_final": "owcs_2026_na_s1_playoffs__2026-04-12_05",
}


# 스탯 CSV MatchId 접두사 → 스파인 이벤트 스코프 (지역이 겹치는 팀쌍의 오조인 방지:
# 예) asia_playoff_* 는 Korea 팀들끼리지만 Asia Stage(owcs_2026_asia_s1_main) 소속)
SRC_SCOPE = [
    ("asia_",  ("owcs_2026_asia_s1_main",)),
    ("korea_", ("owcs_2026_asia_s1_korea", "owcs_2026_asia_s1_korea_playoffs")),
    ("emea_",  ("owcs_2026_emea_s1", "owcs_2026_emea_s1_playoffs")),
    ("na_",    ("owcs_2026_na_s1", "owcs_2026_na_s1_playoffs")),
    ("clash_", ("owcs_2026_champions_clash_day1", "owcs_2026_champions_clash_day2",
                "owcs_2026_champions_clash_day3")),
]


def find_match(idx, team_x, team_y, maps_seq, src_label, src_mid=""):
    """팀쌍으로 후보를 찾고, 복수면 이벤트 스코프 → phase 힌트 → 맵 시퀀스 점수로 판별."""
    cands = idx.get(frozenset((norm(team_x), norm(team_y))), [])
    for prefix, events in SRC_SCOPE:
        if src_mid.startswith(prefix):
            scoped = [m for m in cands if m["event_id"] in events]
            if scoped:
                cands = scoped
            else:
                report["unmatched_stats"].append(
                    f"{src_label}: no candidates within scope {prefix}* for {team_x} vs {team_y}")
                return None
            break
    if src_mid in MANUAL_MATCH_OVERRIDES:
        target = MANUAL_MATCH_OVERRIDES[src_mid]
        hit = [m for m in cands if m["id"] == target]
        if hit:
            return hit[0]
        report["warn"].append(f"{src_label}: manual override {target} not among candidates")
    if not cands:
        report["unmatched_stats"].append(f"{src_label}: no spine match for {team_x} vs {team_y}")
        return None
    if len(cands) > 1:
        # 1) MatchId의 week/playoff 힌트로 이벤트 필터 (…_playoffs 이벤트 = 포스트시즌)
        hint = phase_hint(src_mid)
        if hint == "post":
            filt = [m for m in cands if m["event_id"].endswith("_playoffs")]
        elif hint == "regular":
            filt = [m for m in cands if not m["event_id"].endswith("_playoffs")]
        else:
            filt = cands
        if filt:
            cands = filt
    if len(cands) == 1:
        return cands[0]
    # 2) 맵 시퀀스 위치 일치 점수 — 유일 최고점이면 채택
    seq = [mnorm(x) for x in maps_seq]
    def score(m):
        names = [mnorm(g["name"]) for g in m["maps"]]
        return sum(1 for a, b in zip(seq, names) if a == b)
    scored = sorted(((score(m), m) for m in cands), key=lambda x: -x[0])
    if scored[0][0] > 0 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]
    report["unmatched_stats"].append(
        f"{src_label}: ambiguous {team_x} vs {team_y} maps={maps_seq} candidates={[m['id'] for m in cands]}")
    return None


def team_idx(m, name):
    n = norm(name)
    return 1 if n == norm(m["team1"]) else 2 if n == norm(m["team2"]) else 0


# ── 3. 스탯 어댑터 ────────────────────────────────────────────────────────────

def attach_stats_group(m, games, src_label):
    """games: game_number -> {'map':str,'minutes':float|None,'rows':[stat rows]}"""
    by_n = {g["n"]: g for g in m["maps"]}
    for gn, g in sorted(games.items()):
        target = by_n.get(gn)
        if target is None:
            report["warn"].append(f"{src_label}: game {gn} not in spine {m['id']}")
            continue
        if mnorm(target["name"]) != mnorm(g["map"]):
            report["warn"].append(
                f"{src_label}: map mismatch {m['id']} g{gn}: spine={target['name']} csv={g['map']}")
        if g["minutes"]:
            target["duration_min"] = round(g["minutes"], 2)
        rows_out = []
        for r in g["rows"]:
            ti = team_idx(m, r["team"])
            if ti == 0:
                report["warn"].append(f"{src_label}: team '{r['team']}' not in {m['id']}")
                continue
            rows_out.append({
                "map": gn, "team": ti, "player": r["player"],
                "role": ROLE_MAP.get(r["role"], r["role"]),
                "E": r["E"], "A": r["A"], "D": r["D"],
                "DMG": r["DMG"], "H": r["H"], "MIT": r["MIT"],
            })
        if rows_out:
            target["stats_available"] = True
            m.setdefault("stats", []).extend(rows_out)


def _num(v, cast=int):
    try:
        return cast(float(str(v).replace(",", "")))
    except (ValueError, TypeError):
        return 0


def parse_stat_row(r):
    return {
        "team": r["Team"].strip(), "player": r["Player"].strip(), "role": r["Role"].strip(),
        "E": _num(r.get("E")), "A": _num(r.get("A")), "D": _num(r.get("D")),
        "DMG": _num(r.get("DMG")), "H": _num(r.get("H")), "MIT": _num(r.get("MIT")),
    }


def adapter_stats_generic(idx, csv_path, src_label, sparse):
    """MatchId 그룹 → 게임별 rows → find_match로 스파인에 부착.
    sparse=True: Korea CSV처럼 게임 첫 행만 메타가 있는 형식 (forward-fill)."""
    if not csv_path.exists():
        report["warn"].append(f"{src_label}: file not found {csv_path}")
        return
    groups = defaultdict(lambda: defaultdict(lambda: {"map": "", "minutes": None, "rows": []}))
    cur_mid, cur_game, cur_map, cur_min = None, None, "", None
    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if not (r.get("Team") or "").strip():
                continue
            if sparse:
                if (r.get("MatchId") or "").strip():
                    cur_mid = r["MatchId"].strip()
                if (r.get("Game") or "").strip():
                    cur_game = int(float(r["Game"]))
                    cur_map = (r.get("Map") or "").strip()
                    cur_min = _num(r.get("Minutes"), float) or None
            else:
                cur_mid = r["MatchId"].strip()
                cur_game = int(float(r["Game"]))
                cur_map = (r.get("Map") or "").strip()
                cur_min = _num(r.get("Minutes"), float) or None
            if not cur_mid or not cur_game:
                continue
            g = groups[cur_mid][cur_game]
            g["map"], g["minutes"] = cur_map, cur_min
            g["rows"].append(parse_stat_row(r))

    attached = 0
    for mid, games in groups.items():
        teams = {r["team"] for g in games.values() for r in g["rows"]}
        if len(teams) != 2:
            report["unmatched_stats"].append(f"{src_label}:{mid}: expected 2 teams, got {sorted(teams)}")
            continue
        tx, ty = sorted(teams)
        maps_seq = [games[k]["map"] for k in sorted(games)]
        m = find_match(idx, tx, ty, maps_seq, f"{src_label}:{mid}", src_mid=mid)
        if m is not None:
            attach_stats_group(m, games, f"{src_label}:{mid}")
            attached += 1
    print(f"{src_label}: {len(groups)} stat-matches, attached {attached}")


# ── 4. 밴 어댑터 ──────────────────────────────────────────────────────────────

def adapter_bans(matches):
    # 날짜+팀쌍 인덱스 (밴 조인용) — S1 밴의 "Match n"은 일차 내 순번이라
    # 스파인의 이벤트 누적 match_order와 다르다. 같은 날짜에 같은 팀쌍이 두 번
    # 붙는 일은 없으므로 (날짜, 팀쌍)이 유일 키.
    by_date_pair = defaultdict(list)
    by_pair = defaultdict(list)
    for m in matches.values():
        pair = frozenset((norm(m["team1"]), norm(m["team2"])))
        by_date_pair[(m["date"], pair)].append(m)
        by_pair[pair].append(m)

    # 날짜 없는 밴 라벨(China/Asia)의 이벤트 스코프
    REGION_EVENTS = {
        "Asia": ("owcs_2026_asia_s1_main",),
        "China": ("owcs_2026_china_s1", "owcs_2026_china_s1_playoffs"),
        "Korea": ("owcs_2026_asia_s1_korea", "owcs_2026_asia_s1_korea_playoffs"),
        "NA": ("owcs_2026_na_s1", "owcs_2026_na_s1_playoffs"),
        "EMEA": ("owcs_2026_emea_s1", "owcs_2026_emea_s1_playoffs"),
    }

    def attach(ev, m, stage):
        gn = int(float(ev["game"]))
        target = next((g for g in m["maps"] if g["n"] == gn), None)
        if target is None:
            report["unmatched_bans"].append(f"game {gn} not in {m['id']} ({ev['ban_team']} ban)")
            return False
        ti = team_idx(m, ev["ban_team"])
        if ti == 0:
            report["unmatched_bans"].append(f"ban_team '{ev['ban_team']}' not in {m['id']}")
            return False
        target[f"ban{ti}"] = ev["banned_hero"]
        if stage == "initial":
            target["firstBan"] = ti
        return True

    def run(path, label, stage_map):
        if not path.exists():
            report["warn"].append(f"bans: file not found {path}")
            return
        events = json.loads(path.read_text(encoding="utf-8"))
        # 같은 매치 라벨의 모든 밴 이벤트에서 (game -> map) 지문 수집 — 재대결 판별용
        fingerprints = defaultdict(dict)
        for ev in events:
            mp = mnorm(ev.get("map", ""))
            if mp:
                fingerprints[(ev.get("region"), ev.get("match_label"))][int(float(ev["game"]))] = mp
        ok, skipped = 0, 0
        for ev in events:
            # Intl(Champions Clash) 레코드는 clash_2026_ban_events.json이 정본 — 중복 부착 방지
            if label == "s1" and ev.get("region") == "Intl":
                skipped += 1
                continue
            # China Swiss Stage는 스파인에 없음 (ELO 미반영 정책과 동일) — 의도적 스킵
            if "swiss" in (ev.get("phase") or "").lower():
                skipped += 1
                continue
            stage = stage_map.get(ev["ban_stage"])
            if stage is None:
                report["unmatched_bans"].append(
                    f"{label}: unknown ban_stage '{ev['ban_stage']}' ({ev.get('match_label','?')} g{ev.get('game')})")
                continue
            pair = frozenset((norm(ev["ban_team"]), norm(ev.get("received_team", ""))))
            # 날짜: clash 스키마는 match_date 필드, S1 스키마는 라벨 안의 날짜 (선두 또는 후미)
            date = ev.get("match_date")
            if not date:
                mm = re.search(r"(\d{4}-\d{2}-\d{2})", ev.get("match_label", ""))
                date = mm.group(1) if mm else None
            if date:
                cands = by_date_pair.get((date, pair), [])
            else:
                # 날짜 없는 라벨(China RR·Asia): 지역 이벤트 스코프 안에서 팀쌍으로 조인
                scope = REGION_EVENTS.get(ev.get("region"))
                if not scope:
                    report["unmatched_bans"].append(
                        f"{label}: no date & no scope for region={ev.get('region')} ({ev.get('match_label','?')})")
                    continue
                # phase 텍스트로 정규시즌/포스트시즌 이벤트를 먼저 좁힌다
                p = (ev.get("phase") or "").lower()
                if any(k in p for k in ("week", "round robin", "group")):
                    scope = tuple(e for e in scope if not e.endswith("_playoffs")) or scope
                elif any(k in p for k in ("playoff", "lcq", "seeding", "final", "bracket")):
                    scope = tuple(e for e in scope if e.endswith("_playoffs")) or scope
                cands = [m for m in by_pair.get(pair, []) if m["event_id"] in scope]
                if len(cands) > 1:
                    # 재대결 구분: 같은 라벨의 전체 (game -> map) 지문과 일치하는 후보만
                    fp = fingerprints.get((ev.get("region"), ev.get("match_label")), {})
                    def fits(m, fp=fp):
                        maps_by_n = {g["n"]: mnorm(g["name"]) for g in m["maps"]}
                        return all(maps_by_n.get(gn) == mp for gn, mp in fp.items())
                    filt = [m for m in cands if fits(m)]
                    cands = filt or cands
            if len(cands) != 1:
                report["unmatched_bans"].append(
                    f"{label}: {ev.get('match_label','?')} g{ev['game']} {ev['ban_team']}→{ev['banned_hero']} "
                    f"(candidates={len(cands)})")
                continue
            if attach(ev, cands[0], stage):
                ok += 1
        print(f"bans[{label}]: {len(events)} events, attached {ok}, skipped {skipped} (intl-dup/swiss)")

    run(OUT_DIR / "ban_events.json", "s1",
        {"initial": "initial", "followup": "followup", "follow_up": "followup"})
    run(OUT_DIR / "clash_2026_ban_events.json", "clash", {"ban_1": "initial", "ban_2": "followup"})


# ── 5. emit ───────────────────────────────────────────────────────────────────

def emit(matches):
    ordered = sorted(matches.values(), key=lambda m: (m["date"], m["match_order"]), reverse=True)
    index = []
    for m in ordered:
        cov = {
            "stats": any(g["stats_available"] for g in m["maps"]),
            "bans": any(g["ban1"] or g["ban2"] for g in m["maps"]),
            "duration": any(g["duration_min"] for g in m["maps"]),
        }
        index.append({
            "id": m["id"], "event_id": m["event_id"], "region": m["region"],
            "stage": m["stage"], "phase": m["phase"], "date": m["date"],
            "team1": m["team1"], "team2": m["team2"],
            "score1": m["score1"], "score2": m["score2"], "winner": m["winner"],
            "format": m["format"], "coverage": cov,
        })
        detail = {
            "id": m["id"],
            "meta": {**index[-1], "source_url": m["source_url"]},
            "maps": m["maps"],
            "stats": m.get("stats", []),
        }
        (MATCH_DIR / f"{m['id']}.json").write_text(
            json.dumps(detail, ensure_ascii=False), encoding="utf-8")
    (OUT_DIR / "matches_index.json").write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8")
    n_stats = sum(1 for i in index if i["coverage"]["stats"])
    n_bans = sum(1 for i in index if i["coverage"]["bans"])
    print(f"emit: {len(index)} matches -> matches_index.json + matches/*.json "
          f"(stats {n_stats}, bans {n_bans})")


def write_report():
    lines = ["# 매치 조인 보고서 (build_matches.py 자동 생성)", ""]
    for key, title in [("unmatched_stats", "스탯 조인 실패"),
                       ("unmatched_bans", "밴 조인 실패"),
                       ("warn", "경고")]:
        lines.append(f"## {title} ({len(report[key])})")
        lines += [f"- {x}" for x in report[key]] or ["- 없음"]
        lines.append("")
    (SITE / "data_notes" / "match_join_report.md").write_text(
        "\n".join(lines), encoding="utf-8")
    print(f"report: stats-fail {len(report['unmatched_stats'])}, "
          f"ban-fail {len(report['unmatched_bans'])}, warn {len(report['warn'])}")


def main():
    matches = build_spine()
    idx = index_by_pair(matches)
    adapter_stats_generic(
        idx, STATS_DIR / "KOREA_WITH_ASIA_MATCH_REVIEW_CSV_FIXED" / "KOREA_WITH_ASIA_review_all_matches.csv",
        "korea", sparse=True)
    adapter_stats_generic(
        idx, STATS_DIR / "EMEA_NA_MATCH_REVIEW_CSV" / "all_games_long.csv",
        "emea_na", sparse=False)
    adapter_stats_generic(
        idx, STATS_DIR / "CLASH_MATCH_REVIEW_CSV" / "clash_2026_per_map.csv",
        "clash", sparse=False)
    adapter_bans(matches)
    emit(matches)
    write_report()


if __name__ == "__main__":
    main()
