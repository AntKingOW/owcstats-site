"""
Build site data: CSV/markdown -> JSON files for the website.
Output: assets/data/*.json
"""
import csv, json, re, math
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
SITE = Path(__file__).parent
DATA_OUT = SITE / "assets" / "data"
DATA_OUT.mkdir(parents=True, exist_ok=True)

ELO_DIR = BASE / "Elo-Rating"
STATS_DIR = BASE / "OWCStats" / "OWCStats"

# ── ELO rankings (2024/2025/2026) ────────────────────────────────────────────

def build_elo_rankings():
    result = {}
    for year in [2024, 2025, 2026]:
        path = ELO_DIR / f"OWCS_{year}_GLOBAL_ELO_FINAL.csv"
        if not path.exists():
            print(f"  [skip] {path.name}")
            continue
        rows = []
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                try:
                    rows.append({
                        "rank": int(r.get("rank", 0)),
                        "team": r["team"],
                        "elo": round(float(r["elo"]), 1),
                        "region": r.get("home_region", ""),
                        "maps_played": int(r.get("maps_played", 0)),
                        "maps_won": int(r.get("maps_won", 0)),
                        "maps_lost": int(r.get("maps_lost", 0)),
                        "maps_drawn": int(r.get("maps_drawn", 0)),
                        "win_pct": round(float(str(r.get("win_pct", 0)).replace("%", "")), 1),
                    })
                except Exception as e:
                    print(f"  [warn] {year} row skip: {e}")
        result[str(year)] = sorted(rows, key=lambda x: x["rank"])
        print(f"  ELO {year}: {len(rows)} teams")

    out = DATA_OUT / "elo_rankings.json"
    out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {out.name}")

# ── ELO history (all teams, 2024+2025+2026 combined) ─────────────────────────

def build_elo_history():
    """
    Combined ELO history across all three seasons.
    Per team: one entry per event they played in, with their end-of-event ELO.
    Events are sorted by first global occurrence (chronological order).
    """
    # team -> event_id -> { max_order, elo, year, result }
    team_events = defaultdict(dict)
    # event_id -> (year, min_global_order) — used to sort events chronologically
    event_first = {}

    for year in [2024, 2025, 2026]:
        path = ELO_DIR / f"OWCS_{year}_GLOBAL_ELO_HISTORY.csv"
        if not path.exists():
            print(f"  [skip] OWCS_{year}_GLOBAL_ELO_HISTORY.csv")
            continue
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                team  = r.get("team", "")
                event = r.get("event_id", "")
                if not team or not event:
                    continue
                try:
                    order = int(r["global_map_order"])
                    elo   = round(float(r["elo_after"]), 1)
                except Exception:
                    continue
                result = r.get("result", "")

                # Track earliest occurrence of this event (for global sort)
                if event not in event_first:
                    event_first[event] = (year, order)
                else:
                    py, po = event_first[event]
                    if year < py or (year == py and order < po):
                        event_first[event] = (year, order)

                # Per team: keep the LAST (highest-order) entry per event
                cur = team_events[team].get(event)
                if cur is None or order > cur["max_order"]:
                    team_events[team][event] = {
                        "max_order": order,
                        "elo": elo,
                        "year": str(year),
                        "result": result,
                    }

    # Sort all events chronologically
    event_order = {e: i for i, e in enumerate(
        sorted(event_first, key=lambda e: event_first[e])
    )}

    result = {}
    for team, ev_dict in team_events.items():
        sorted_evs = sorted(ev_dict.items(), key=lambda x: event_order.get(x[0], 9999))
        result[team] = [
            {"event": ev, "elo": d["elo"], "year": d["year"], "result": d["result"]}
            for ev, d in sorted_evs
        ]

    out = DATA_OUT / "elo_history.json"
    out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {out.name} ({len(result)} teams across 2024–2026)")

# ── Korea player stats from CSV ───────────────────────────────────────────────

def parse_korea_players():
    """
    Read KOREA_WITH_ASIA_MATCH_REVIEW_CSV_FIXED/KOREA_WITH_ASIA_review_all_matches.csv
    (commit 0eae0f9 — per-game rows for ALL Korea stages + Asia tournament).

    Includes: Regular Season W1-W4, LCQ, Seeding Decider, Playoff, Asia Stage.
    Excludes non-Korean teams (Japan/Pacific: ENTER FORCE.36, VARREL, etc.).
    Falls back to korea_games_long.csv → TOTAL MD if not found.
    """
    # Korean league teams (Japan/Pacific teams excluded per user instruction)
    KOREA_TEAMS = {
        "cheeseburger", "crazy raccoon", "new era", "onside gaming",
        "poker face", "t1", "team falcons", "zan esports", "zeta division",
    }

    csv_path = (STATS_DIR / "KOREA_WITH_ASIA_MATCH_REVIEW_CSV_FIXED"
                / "KOREA_WITH_ASIA_review_all_matches.csv")
    if not csv_path.exists():
        # Fallback to W1+W2 only CSV
        csv_path2 = STATS_DIR / "KOREA_MATCH_REVIEW_CSV" / "korea_games_long.csv"
        if csv_path2.exists():
            print(f"  [warn] Full CSV not found, using {csv_path2.name}")
            csv_path = csv_path2
        else:
            print("  [warn] Korea CSV not found, falling back to TOTAL MD")
            return _parse_korea_total_md()

    players = defaultdict(lambda: {
        "region": "Korea", "team": "", "player": "", "role": "",
        "minutes": 0.0, "games": 0,
        "E": 0, "A": 0, "D": 0, "DMG": 0, "H": 0, "MIT": 0,
    })

    # Sparse CSV: first row of each game fills Event/MatchId/Match/Phase/Minutes,
    # subsequent rows for the same game leave those columns empty → forward-fill.
    last_minutes = 0.0

    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            team   = r.get("Team", "").strip()
            player = r.get("Player", "").strip()
            role   = r.get("Role", "").strip()
            if not team or not player:
                continue
            # Exclude Japan/Pacific teams
            if team.lower() not in KOREA_TEAMS:
                continue

            # Forward-fill Minutes
            raw_mins = r.get("Minutes", "").strip()
            if raw_mins:
                try:
                    last_minutes = float(raw_mins)
                except ValueError:
                    pass
            minutes = last_minutes

            key = (player.lower(), team.lower())
            p = players[key]
            if not p["team"]:
                p["team"]   = team
                p["player"] = player
                p["role"]   = role
            try:
                p["minutes"] += minutes
                p["games"]   += 1
                p["E"]   += int(float(r.get("E",   0) or 0))
                p["A"]   += int(float(r.get("A",   0) or 0))
                p["D"]   += int(float(r.get("D",   0) or 0))
                p["DMG"] += int(float(r.get("DMG", 0) or 0))
                p["H"]   += int(float(r.get("H",   0) or 0))
                p["MIT"] += int(float(r.get("MIT", 0) or 0))
            except Exception as e:
                print(f"  [warn] Korea row error: {e}")

    result = []
    for p in players.values():
        m = p["minutes"]
        if m < 5:
            continue
        E, A, D = p["E"], p["A"], p["D"]
        DMG, H, MIT = p["DMG"], p["H"], p["MIT"]
        result.append({
            "region":       p["region"],
            "team":         p["team"],
            "player":       p["player"],
            "role":         p["role"],
            "games":        p["games"],
            "minutes":      round(m, 1),
            "dmg_per10":    round(DMG / m * 10, 1) if m else 0,
            "heal_per10":   round(H   / m * 10, 1) if m else 0,
            "elim_per10":   round(E   / m * 10, 2) if m else 0,
            "assist_per10": round(A   / m * 10, 2) if m else 0,
            "death_per10":  round(D   / m * 10, 2) if m else 0,
            "ed_ratio":     round(E / D, 2) if D else round(float(E), 2),
            "mit_per10":    round(MIT / m * 10, 1) if m else 0,
        })
    print(f"  Korea+Asia CSV: {len(result)} player records ({csv_path.name})")
    return result


def _parse_korea_total_md():
    """Legacy fallback: parse OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md."""
    path = STATS_DIR / "OWCS_KOREA_2026_TOTAL_PLAYER_RATE_STATS.md"
    if not path.exists():
        print("  [skip] Korea stats not found")
        return []
    records = []
    seen = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or "---" in line or line.startswith("| Team"):
                continue
            cols = [c.strip() for c in line.split("|")]
            cols = [c for c in cols if c]
            if len(cols) < 12:
                continue
            try:
                def num(s): return float(s.replace(",","")) if s and s != "-" else 0.0
                team=cols[0]; player=cols[1]; role=cols[2]
                apps=int(num(cols[3])); minutes=num(cols[4])
                E=int(num(cols[5])); A=int(num(cols[6])); D=int(num(cols[7]))
                DMG=int(num(cols[9])); H=int(num(cols[10])); MIT=int(num(cols[11]))
                key=(player.lower(), team.lower())
                if key in seen:
                    r=records[seen[key]]
                    r["games"]+=apps; r["minutes"]+=minutes
                    r["E"]+=E; r["A"]+=A; r["D"]+=D
                    r["DMG"]+=DMG; r["H"]+=H; r["MIT"]+=MIT
                else:
                    seen[key]=len(records)
                    records.append({"region":"Korea","team":team,"player":player,
                        "role":role,"games":apps,"minutes":minutes,
                        "E":E,"A":A,"D":D,"DMG":DMG,"H":H,"MIT":MIT})
            except: pass
    result = []
    for r in records:
        m=r["minutes"]
        if m<5: continue
        E,A,D=r["E"],r["A"],r["D"]; DMG,H,MIT=r["DMG"],r["H"],r["MIT"]
        result.append({"region":"Korea","team":r["team"],"player":r["player"],
            "role":r["role"],"games":r["games"],"minutes":round(m,1),
            "dmg_per10":round(DMG/m*10,1),"heal_per10":round(H/m*10,1),
            "elim_per10":round(E/m*10,2),"assist_per10":round(A/m*10,2),
            "death_per10":round(D/m*10,2),"ed_ratio":round(E/D,2) if D else float(E),
            "mit_per10":round(MIT/m*10,1)})
    print(f"  Korea MD (fallback): {len(result)} records")
    return result

# ── Player stats (EMEA + NA from CSV) ────────────────────────────────────────

def build_player_stats():
    # EMEA + NA from all_games_long.csv (latest version with pre-calculated Minutes)
    # Falls back to EMEA_NA_PLAYER_STATS_CLEANED.csv if not found
    path = STATS_DIR / "EMEA_NA_MATCH_REVIEW_CSV" / "all_games_long.csv"
    if not path.exists():
        path = STATS_DIR / "EMEA_NA_PLAYER_STATS_CLEANED.csv"
    emea_na = []
    if not path.exists():
        print("  [skip] player stats CSV not found")
    else:
        players = defaultdict(lambda: {
            "region": "", "team": "", "player": "", "role": "",
            "minutes": 0.0,
            "E": 0, "A": 0, "D": 0, "DMG": 0, "H": 0, "MIT": 0,
            "games": 0,
        })

        skipped = 0
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                # Skip rows with unreliable OCR data
                if r.get("NeedsReOCR", "").strip().lower() == "yes":
                    skipped += 1
                    continue
                # Column names differ between files: normalize to lowercase
                region = r.get("Region", r.get("region", ""))
                team   = r.get("Team",   r.get("team",   ""))
                player = r.get("Player", r.get("player", ""))
                role   = r.get("Role",   r.get("role",   ""))
                key = (region, team, player, role)
                p = players[key]
                p["region"] = region
                p["team"]   = team
                p["player"] = player
                p["role"]   = role
                p["games"] += 1
                # Use pre-calculated Minutes if available, else parse Elapsed
                try:
                    minutes_val = r.get("Minutes", r.get("minutes", ""))
                    if minutes_val:
                        p["minutes"] += float(minutes_val)
                    else:
                        elapsed = r.get("Elapsed", r.get("elapsed", "0:00"))
                        parts = elapsed.split(":")
                        mins = float(parts[0]) * 60 + float(parts[1]) if len(parts) == 2 else float(parts[0])
                        p["minutes"] += mins
                except:
                    pass
                for col in ["E","A","D","DMG","H","MIT"]:
                    try:
                        p[col] += int(r.get(col, 0) or 0)
                    except:
                        pass

        if skipped:
            print(f"  [info] skipped {skipped} NeedsReOCR=yes rows")
        for p in players.values():
            m = p["minutes"]
            if m < 5:
                continue
            emea_na.append({
                "region": p["region"],
                "team": p["team"],
                "player": p["player"],
                "role": p["role"],
                "minutes": round(m, 1),
                "games": p["games"],
                "dmg_per10": round(p["DMG"] / m * 10, 1) if m else 0,
                "heal_per10": round(p["H"] / m * 10, 1) if m else 0,
                "elim_per10": round(p["E"] / m * 10, 2) if m else 0,
                "assist_per10": round(p["A"] / m * 10, 2) if m else 0,
                "death_per10": round(p["D"] / m * 10, 2) if m else 0,
                "ed_ratio": round(p["E"] / p["D"], 2) if p["D"] else round(p["E"], 2),
                "mit_per10": round(p["MIT"] / m * 10, 1) if m else 0,
            })
        print(f"  EMEA/NA CSV: {len(emea_na)} player records (from {path.name})")

    # Korea from MD
    korea = parse_korea_players()

    result = korea + emea_na

    out = DATA_OUT / "player_stats.json"
    out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {out.name} ({len(result)} total records: {len(korea)} KR + {len(emea_na)} EMEA/NA)")

# ── Ban history ───────────────────────────────────────────────────────────────

def build_ban_history():
    path = SITE / "ban_history.csv"
    if not path.exists():
        print("  [skip] ban_history.csv not found — run parse_ban_history.py first")
        return

    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    # Ban frequency per team
    team_bans = defaultdict(lambda: defaultdict(int))  # team -> hero -> count
    team_total = defaultdict(int)
    # Matchup-specific bans: (team_A, team_B) -> hero -> count
    matchup_bans = defaultdict(lambda: defaultdict(int))

    for r in rows:
        ti = r["team_initial"]
        hi = r["hero_initial"]
        tf = r["team_followup"]
        hf = r["hero_followup"]

        if ti and hi:
            team_bans[ti][hi] += 1
            team_total[ti] += 1
            matchup_bans[(ti, tf)][hi] += 1

        if tf and hf:
            team_bans[tf][hf] += 1
            team_total[tf] += 1
            matchup_bans[(tf, ti)][hf] += 1

    # Serialize
    team_ban_rates = {}
    for team, hero_counts in team_bans.items():
        total = team_total[team]
        team_ban_rates[team] = {
            hero: round(count / total, 3)
            for hero, count in sorted(hero_counts.items(), key=lambda x: -x[1])
        }

    matchup_ban_rates = {}
    for (ta, tb), hero_counts in matchup_bans.items():
        key = f"{ta}||{tb}"
        total = sum(hero_counts.values())
        matchup_ban_rates[key] = {
            hero: round(count / total, 3)
            for hero, count in sorted(hero_counts.items(), key=lambda x: -x[1])
        }

    result = {
        "records": rows,
        "team_ban_rates": team_ban_rates,
        "matchup_ban_rates": matchup_ban_rates,
    }

    out = DATA_OUT / "ban_history.json"
    out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {out.name} ({len(rows)} records, {len(team_ban_rates)} teams)")

# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Building ELO rankings...")
    build_elo_rankings()

    print("Building ELO history...")
    build_elo_history()

    print("Building player stats...")
    build_player_stats()

    print("Building ban history...")
    build_ban_history()

    print("\nDone. Files in:", DATA_OUT)
