"""
Parse Korea player stats MD files → korea_games_long.csv
Output format matches EMEA_NA_MATCH_REVIEW_CSV/all_games_long.csv

Sources:
  OWCS_KOREA_2026_WEEK1_PLAYER_RATE_STATS.md  → per-match rows (Day1-3, 9 matches)
  OWCS_KOREA_2026_WEEK2_PLAYER_RATE_STATS.md  → per-week aggregate rows

Column layouts detected from markdown table header row:
  Layout A (Week1 match blocks):
    Player | Team | Role | Minutes | E | A | D | DMG | H | MIT | ...
  Layout B (Week1 Overall / Week2):
    Team | Player | Role | Appearances | Minutes | E | A | D | E/D | DMG | H | MIT | ...
  Layout C (Week2 alternate – same as B but col order may vary):
    Player | Team | Role | Appearances | Minutes | E | A | D | E/D | DMG | H | MIT | ...
"""
import re, csv, sys
from pathlib import Path

BASE      = Path(__file__).parent.parent
STATS_DIR = BASE / "OWCStats" / "OWCStats"
OUT_DIR   = STATS_DIR / "KOREA_MATCH_REVIEW_CSV"
OUT_DIR.mkdir(exist_ok=True)
OUT       = OUT_DIR / "korea_games_long.csv"

FIELDNAMES = [
    "Region","MatchId","Match","Phase","ReviewFile","Game","Source","Map",
    "Elapsed","Minutes","Team","Player","Role","Row",
    "CleanReason","NeedsReOCR","ReplacedCells","UnresolvedStats",
    "E","A","D","DMG","H","MIT",
    "E/10","A/10","D/10","DMG/10","H/10","MIT/10","E/D",
]

def mins_to_elapsed(m: float) -> str:
    total_s = int(round(m * 60))
    return f"{total_s // 60}:{total_s % 60:02d}"

def clean_num(s: str) -> str:
    return s.replace(",", "").strip()

def detect_layout(header_cols):
    """
    Given the lowercase stripped column names from the header row,
    return a dict: {'team': idx, 'player': idx, 'role': idx,
                    'minutes': idx, 'E': idx, 'A': idx, 'D': idx,
                    'DMG': idx, 'H': idx, 'MIT': idx}
    Returns None if not a recognised stat table header.
    """
    h = [c.lower() for c in header_cols]

    # Must contain at least 'role' and 'e' and 'dmg'
    if 'role' not in h:
        return None

    def fi(name):
        try:
            return h.index(name)
        except ValueError:
            return None

    role_i = fi('role')
    # team/player order depends on which comes first
    team_i   = fi('team')
    player_i = fi('player')
    if team_i is None or player_i is None or role_i is None:
        return None

    # minutes: look for 'minutes' first, fallback to column after 'appearances'
    minutes_i = fi('minutes')
    if minutes_i is None:
        app_i = fi('appearances')
        if app_i is not None:
            minutes_i = app_i + 1
    if minutes_i is None:
        return None

    # Raw stat columns: after minutes, order is E A D [E/D] DMG H MIT
    # We find them by position relative to minutes
    # Strategy: scan columns after minutes_i for numeric-looking headers
    # Expected order: E, A, D, (E/D optional), DMG, H, MIT
    after = list(enumerate(h[minutes_i+1:], start=minutes_i+1))

    # Map known header names to field
    col_map = {}
    for idx, name in after:
        name_clean = name.replace('/', '').strip()
        if name_clean == 'e':     col_map.setdefault('E', idx)
        elif name_clean == 'a':   col_map.setdefault('A', idx)
        elif name_clean == 'd':   col_map.setdefault('D', idx)
        elif name_clean in ('dmg', 'dmg10', 'dmgmin'):
            # take the first 'dmg' variant that isn't per-10
            if 'dmg' not in name_clean[3:]:
                col_map.setdefault('DMG', idx)
        elif name_clean == 'h':   col_map.setdefault('H', idx)
        elif name_clean == 'mit': col_map.setdefault('MIT', idx)

    # Fallback: if not found by name, use positional offsets after minutes
    # Layout A: minutes | E | A | D | DMG | H | MIT
    # Layout B: minutes | E | A | D | E/D | DMG | H | MIT
    if 'E' not in col_map and len(after) >= 6:
        # Check if col minutes+1 header is 'e'
        # Just use positional: E=+1, A=+2, D=+3, then skip E/D if present
        pos_e   = minutes_i + 1
        pos_a   = minutes_i + 2
        pos_d   = minutes_i + 3
        # DMG: if col minutes+4 header is 'e/d', DMG is minutes+5; else minutes+4
        if len(h) > minutes_i + 4 and h[minutes_i + 4] in ('e/d', 'ed'):
            pos_dmg = minutes_i + 5
        else:
            pos_dmg = minutes_i + 4
        pos_h   = pos_dmg + 1
        pos_mit = pos_dmg + 2
        col_map = {'E': pos_e, 'A': pos_a, 'D': pos_d,
                   'DMG': pos_dmg, 'H': pos_h, 'MIT': pos_mit}

    if len(col_map) < 6:
        return None

    return {
        'team':    team_i,
        'player':  player_i,
        'role':    role_i,
        'minutes': minutes_i,
        **col_map,
    }

def parse_table(text: str):
    """
    Parse all stat tables in `text`.
    Detects column layout from each table's header row.
    Returns list of player-row dicts.
    """
    rows = []
    layout = None
    for line in text.splitlines():
        if not line.startswith("|"):
            layout = None   # reset between tables
            continue

        cols = [c.strip() for c in line.split("|")]
        cols = [c for c in cols if c != ""]
        if not cols:
            continue

        # Separator row
        if all(re.match(r"^-+:?$", c) for c in cols):
            continue

        # Header row?
        if cols[0].lower() in ("player", "team"):
            layout = detect_layout(cols)
            continue

        if layout is None:
            continue

        # Data row
        try:
            def g(key):
                i = layout.get(key)
                if i is None or i >= len(cols):
                    return ""
                return clean_num(cols[i])

            mins = float(g('minutes')) if g('minutes') else 0.0
            if mins <= 0:
                continue

            E   = int(float(g('E')))
            A   = int(float(g('A')))
            D   = int(float(g('D')))
            DMG = int(float(g('DMG')))
            H   = int(float(g('H')))
            MIT = int(float(g('MIT')))

            rows.append({
                'team':   cols[layout['team']],
                'player': cols[layout['player']],
                'role':   cols[layout['role']],
                'minutes': mins,
                'E': E, 'A': A, 'D': D,
                'DMG': DMG, 'H': H, 'MIT': MIT,
                'ed': round(E / D, 4) if D else float(E),
            })
        except Exception:
            continue
    return rows

def make_record(r, region, match_id, match_name, phase, review_file, game, source, row_idx):
    mins = r['minutes']
    return {
        "Region": region,
        "MatchId": match_id,
        "Match": match_name,
        "Phase": phase,
        "ReviewFile": review_file,
        "Game": game,
        "Source": source,
        "Map": "aggregate",
        "Elapsed": mins_to_elapsed(mins),
        "Minutes": round(mins, 4),
        "Team": r['team'],
        "Player": r['player'],
        "Role": r['role'],
        "Row": row_idx,
        "CleanReason": "kept_current",
        "NeedsReOCR": "no",
        "ReplacedCells": 0,
        "UnresolvedStats": "",
        "E": r['E'], "A": r['A'], "D": r['D'],
        "DMG": r['DMG'], "H": r['H'], "MIT": r['MIT'],
        "E/10":   round(r['E']   / mins * 10, 4) if mins else 0,
        "A/10":   round(r['A']   / mins * 10, 4) if mins else 0,
        "D/10":   round(r['D']   / mins * 10, 4) if mins else 0,
        "DMG/10": round(r['DMG'] / mins * 10, 4) if mins else 0,
        "H/10":   round(r['H']   / mins * 10, 4) if mins else 0,
        "MIT/10": round(r['MIT'] / mins * 10, 4) if mins else 0,
        "E/D": r['ed'],
    }


# ── Week 1: per-match blocks ──────────────────────────────────────────────────

def parse_week1(fpath: Path):
    text = fpath.read_text(encoding="utf-8", errors="ignore")

    # Split into sections by any ## header
    sections = re.split(r"(?m)^(## .+)", text)
    # sections: [preamble, '## header', content, '## header', content, ...]

    records = []
    i = 1
    while i + 1 < len(sections):
        header  = sections[i].strip()   # e.g. "## Day 1 Match 1"
        content = sections[i + 1]
        i += 2

        title = header.lstrip("#").strip()

        # Only process Day X Match Y blocks (skip Overall etc.)
        if not re.match(r"Day \d+ Match \d+", title):
            continue

        # Extract games count
        games_m = re.search(r"Games captured.*?(\d+)", content)
        n_games = games_m.group(1) if games_m else "?"

        match_id   = f"korea_week1_{title.lower().replace(' ', '_')}"
        match_name = f"Week 1 {title}"

        rows = parse_table(content)
        for idx, r in enumerate(rows, 1):
            records.append(make_record(
                r, "Korea", match_id, match_name,
                "Regular Season", fpath.name,
                n_games,
                f"{title} ({n_games} games)",
                idx,
            ))
    return records


# ── Week 2: week-aggregate ────────────────────────────────────────────────────

def parse_week2(fpath: Path):
    text = fpath.read_text(encoding="utf-8", errors="ignore")
    rows = parse_table(text)
    records = []
    for idx, r in enumerate(rows, 1):
        records.append(make_record(
            r, "Korea",
            "korea_week2_aggregate", "Week 2 aggregate",
            "Regular Season", fpath.name,
            "aggregate", "Week 2 aggregate",
            idx,
        ))
    return records


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    all_records = []

    sources = [
        (STATS_DIR / "OWCS_KOREA_2026_WEEK1_PLAYER_RATE_STATS.md", parse_week1, "Week1"),
        (STATS_DIR / "OWCS_KOREA_2026_WEEK2_PLAYER_RATE_STATS.md", parse_week2, "Week2"),
    ]

    for fpath, parser, label in sources:
        if fpath.exists():
            recs = parser(fpath)
            all_records.extend(recs)
            print(f"  {label}: {len(recs)}행 파싱 완료")
        else:
            print(f"  [skip] {fpath.name} 없음")

    print()
    print("  [미반영 - PNG만 있음 (OCR 필요)]")
    for p in ["Week3","Week4","LCQ","Seeding Decider","Playoff"]:
        print(f"    Korea {p}")

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"\n[OK] 총 {len(all_records)}행 → {OUT}")

    from collections import Counter
    teams = Counter(r["Team"] for r in all_records)
    players_per_team = {}
    for r in all_records:
        players_per_team.setdefault(r["Team"], set()).add(r["Player"])

    print("\n팀별 행 수 / 선수 수:")
    for t, c in sorted(teams.items()):
        p_count = len(players_per_team.get(t, set()))
        print(f"  {t:<22} {c:>4}행  {p_count}명")

if __name__ == "__main__":
    main()
