"""
Update ELO ratings with Champions Clash Day 2 results.
K=24 per map, applied sequentially within each match.

Day 2 results (map-by-map winners inferred from scoreboard stats):
  UB SF: CR vs TM   → CR 3-0  (CR wins maps 1,2,3)
  UB SF: ZETA vs VP → ZETA 3-1 (ZETA wins 1,3,4; VP wins 2)
  LB QF: VP vs DAL  → VP 3-1  (VP wins 1,3,4; DAL wins 2)
  LB QF: TM vs WBG  → TM 3-1  (TM wins 1,2,3; WBG wins 4)
"""
import json, math, copy

K = 24
YEAR = '2026'
EVENT = 'owcs_2026_champions_clash'

def expected(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def apply_map(elos, winner, loser):
    e = expected(elos[winner], elos[loser])
    delta = round(K * (1 - e), 1)
    elos[winner] = round(elos[winner] + delta, 1)
    elos[loser]  = round(elos[loser]  - delta, 1)

# ── Starting ELOs (post Day 1) ─────────────────────────────────────────────
elos = {
    'Crazy Raccoon':  1792.2,
    'ZETA DIVISION':  1852.0,
    'Twisted Minds':  1922.7,
    'Virtus.pro':     1701.1,
    'Dallas Fuel':    1623.8,
    'Weibo Gaming':   1721.7,
}
print("Starting ELOs:")
for t, e in elos.items():
    print(f"  {t:<25} {e}")

# ── Day 2 matches (in schedule order) ─────────────────────────────────────
# Each match: list of (winner, loser) per map
matches = [
    {
        'label': 'UB SF: CR vs TM (3-0)',
        'maps': [
            ('Crazy Raccoon', 'Twisted Minds'),  # Ilios
            ('Crazy Raccoon', 'Twisted Minds'),  # Rialto
            ('Crazy Raccoon', 'Twisted Minds'),  # King's Row
        ]
    },
    {
        'label': 'UB SF: ZETA vs VP (3-1)',
        'maps': [
            ('ZETA DIVISION', 'Virtus.pro'),     # Ilios
            ('Virtus.pro',    'ZETA DIVISION'),  # New Junk City (VP won)
            ('ZETA DIVISION', 'Virtus.pro'),     # Map 3
            ('ZETA DIVISION', 'Virtus.pro'),     # Map 4
        ]
    },
    {
        'label': 'LB QF: VP vs DAL (3-1)',
        'maps': [
            ('Virtus.pro',  'Dallas Fuel'),      # Ilios
            ('Dallas Fuel', 'Virtus.pro'),       # New Junk City (DAL won)
            ('Virtus.pro',  'Dallas Fuel'),      # Map 3
            ('Virtus.pro',  'Dallas Fuel'),      # Map 4
        ]
    },
    {
        'label': 'LB QF: TM vs WBG (3-1)',
        'maps': [
            ('Twisted Minds', 'Weibo Gaming'),   # Oasis
            ('Twisted Minds', 'Weibo Gaming'),   # King's Row
            ('Twisted Minds', 'Weibo Gaming'),   # Runasapi
            ('Weibo Gaming',  'Twisted Minds'),  # Circuit Royal (WBG won)
        ]
    },
]

# Track per-team results for history entries
team_results = {t: {'wins': 0, 'losses': 0} for t in elos}

for match in matches:
    print(f"\n{match['label']}")
    for w, l in match['maps']:
        before_w, before_l = elos[w], elos[l]
        apply_map(elos, w, l)
        delta = round(elos[w] - before_w, 1)
        print(f"  {w} def {l}: {before_w}→{elos[w]} ({'+' if delta>=0 else ''}{delta})")
        team_results[w]['wins']   += 1
        team_results[l]['losses'] += 1

print("\nFinal ELOs after Day 2:")
for t, e in sorted(elos.items(), key=lambda x: -x[1]):
    r = team_results[t]
    net = r['wins'] - r['losses']
    result = 'win' if net > 0 else ('loss' if net < 0 else 'draw')
    print(f"  {t:<25} {e}  ({r['wins']}W-{r['losses']}L → {result})")

# ── Update elo_history.json ────────────────────────────────────────────────
h = json.load(open(r'assets/data/elo_history.json', encoding='utf-8'))

for team, final_elo in elos.items():
    r = team_results[team]
    net = r['wins'] - r['losses']
    result = 'win' if net > 0 else ('loss' if net < 0 else 'draw')
    eliminated = team in ('Dallas Fuel', 'Weibo Gaming')

    entry = {
        'event': EVENT,
        'elo': final_elo,
        'year': YEAR,
        'result': result,
    }
    if eliminated:
        entry['eliminated'] = True

    if team in h:
        h[team].append(entry)
    else:
        h[team] = [entry]

with open(r'assets/data/elo_history.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=2)
print("\nelo_history.json updated.")

# ── Update elo_rankings.json ───────────────────────────────────────────────
rankings = json.load(open(r'assets/data/elo_rankings.json', encoding='utf-8'))
rows_2026 = rankings.get(YEAR, [])

for row in rows_2026:
    if row['team'] in elos:
        row['elo'] = elos[row['team']]

# Recalculate maps_won / maps_lost / maps_played / win_pct from history
for row in rows_2026:
    if row['team'] not in elos:
        continue
    team_history = h.get(row['team'], [])
    clash_entries = [e for e in team_history if e['event'] == EVENT]
    # Count map wins/losses from team_results
    tr = team_results.get(row['team'], {})
    # Add to existing maps_won/lost
    row['maps_won']   = row.get('maps_won', 0)   + tr.get('wins', 0)
    row['maps_lost']  = row.get('maps_lost', 0)  + tr.get('losses', 0)
    row['maps_played']= row.get('maps_played', 0) + tr.get('wins', 0) + tr.get('losses', 0)
    total = row['maps_played']
    row['win_pct'] = round(row['maps_won'] / total * 100, 1) if total else 0.0

# Re-rank by ELO
rows_2026_sorted = sorted(rows_2026, key=lambda x: -x['elo'])
for i, row in enumerate(rows_2026_sorted, 1):
    row['rank'] = i
rankings[YEAR] = rows_2026_sorted

with open(r'assets/data/elo_rankings.json', 'w', encoding='utf-8') as f:
    json.dump(rankings, f, ensure_ascii=False, indent=2)
print("elo_rankings.json updated.")
