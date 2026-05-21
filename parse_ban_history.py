"""
Parse ban history from OWCS RESULTS markdown files → ban_history.csv
Format in markdown:
  1. Game 1 - initial ban: Poker Face Emre / follow-up ban: Cheeseburger Zarya
"""
import re, csv
from pathlib import Path

BASE = Path(__file__).parent.parent
STATS_DIR = BASE / "OWCStats" / "OWCStats"
OUT = Path(__file__).parent / "ban_history.csv"

# Regex to parse ban lines
BAN_RE = re.compile(
    r'(?:Game\s+)?(\d+)\s*[.\-]\s*(?:Game\s+\d+\s*[-–]\s*)?'
    r'initial ban:\s*(.+?)\s*/\s*follow-up ban:\s*(.+)',
    re.IGNORECASE
)

# Known hero names from shared_owcs_reference to help split "team hero"
# We'll use a heuristic: heroes are single words or two-word names
# Teams can be multiple words. We split by finding the last word as hero.
# Better: load hero list from shared_owcs_reference.js

def load_heroes():
    ref_path = BASE / "BanCalculatorOW" / "data" / "shared_owcs_reference.js"
    if not ref_path.exists():
        return set()
    text = ref_path.read_text(encoding="utf-8")
    # Extract hero_name_en values
    heroes = set(re.findall(r'"hero_name_en"\s*:\s*"([^"]+)"', text))
    return heroes

HEROES = load_heroes()

def split_team_hero(s: str):
    """Split 'Team Name HeroName' into (team, hero).
    Strategy: try matching known heroes from the end of string.
    """
    s = s.strip()
    # Try two-word hero first, then one-word
    words = s.split()
    for hero_len in [2, 1]:
        if len(words) > hero_len:
            hero = " ".join(words[-hero_len:])
            team = " ".join(words[:-hero_len])
            if hero in HEROES:
                return team, hero
    # Fallback: last word is hero
    if len(words) >= 2:
        return " ".join(words[:-1]), words[-1]
    return s, ""

def parse_results_md(fpath: Path):
    """Parse a single RESULTS.md and yield ban records."""
    text = fpath.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # Extract region from filename
    fname = fpath.stem  # e.g. OWCS_KOREA_2026_WEEK1_RESULTS
    region = "Unknown"
    if "KOREA" in fname.upper():
        region = "Korea"
    elif "_NA_" in fname.upper():
        region = "NA"
    elif "EMEA" in fname.upper():
        region = "EMEA"
    elif "CHINA" in fname.upper():
        region = "China"
    elif "ASIA" in fname.upper():
        region = "Asia"
    elif "JAPAN" in fname.upper():
        region = "Japan"
    elif "PACIFIC" in fname.upper():
        region = "Pacific"

    # Extract match context (winner/loser) — look for "Winner:" lines
    winner = ""
    loser = ""
    match_block_winners = []
    for i, line in enumerate(lines):
        if re.match(r'^\*\*Winner\*\*:', line, re.I) or re.match(r'^Winner:', line, re.I):
            w = re.sub(r'\*\*Winner\*\*:|Winner:', '', line, flags=re.I).strip()
            match_block_winners.append(w)

    # Parse bans section
    in_bans = False
    match_idx = 0  # which match block we're in
    records = []

    for line in lines:
        # Detect start of Bans section
        if re.match(r'^\s*bans\s*:', line, re.I):
            in_bans = True
            continue

        # Detect new section (## or ###) to exit bans
        if in_bans and re.match(r'^#{1,3}\s', line):
            in_bans = False
            continue

        if in_bans:
            m = BAN_RE.search(line)
            if m:
                game_num = int(m.group(1))
                initial_raw = m.group(2).strip()
                followup_raw = m.group(3).strip()

                team_i, hero_i = split_team_hero(initial_raw)
                team_f, hero_f = split_team_hero(followup_raw)

                # Skip records with unread/empty team or hero
                def bad(s): return not s or s.lower() == "unread" or "unread" in s.lower()
                if bad(team_i) or bad(hero_i) or bad(team_f) or bad(hero_f):
                    continue

                records.append({
                    "region": region,
                    "match_file": fpath.name,
                    "game_num": game_num,
                    "team_initial": team_i,
                    "hero_initial": hero_i,
                    "team_followup": team_f,
                    "hero_followup": hero_f,
                })

    return records

def main():
    files = sorted(STATS_DIR.glob("OWCS_*_2026_*_RESULTS.md"))
    print(f"RESULTS.md 파일 {len(files)}개 발견")

    all_records = []
    for fpath in files:
        recs = parse_results_md(fpath)
        all_records.extend(recs)
        print(f"  {fpath.name}: {len(recs)}개 밴 기록")

    fieldnames = ["region","match_file","game_num","team_initial","hero_initial","team_followup","hero_followup"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"\n[OK] Total {len(all_records)} ban records -> {OUT}")

    # Quick sanity: count per team
    from collections import Counter
    team_counts = Counter()
    hero_counts = Counter()
    for r in all_records:
        team_counts[r["team_initial"]] += 1
        team_counts[r["team_followup"]] += 1
        hero_counts[r["hero_initial"]] += 1
        hero_counts[r["hero_followup"]] += 1

    print("\n팀별 밴 횟수 Top 10:")
    for team, cnt in team_counts.most_common(10):
        print(f"  {team}: {cnt}")

    print("\n영웅별 밴 횟수 Top 10:")
    for hero, cnt in hero_counts.most_common(10):
        print(f"  {hero}: {cnt}")

if __name__ == "__main__":
    main()
