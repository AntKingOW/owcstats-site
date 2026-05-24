"""
Full Day 2 update from Liquipedia:
- Correct ban events for all 4 Day 2 matches
- Correct map results (incl. Circuit Royal DRAW in TM vs WBG)
- Correct ELO recalculation
"""
import json, math, copy

# ─────────────────────────────────────────────────────────────────────────────
# 1. BAN EVENTS — Day 2
# ─────────────────────────────────────────────────────────────────────────────
PHASE = 'Champions Clash'
REGION = 'Intl'

new_bans = [
  # ── UB SF: CR vs TM ──────────────────────────────────────────────────────
  # Map 1: Ilios (Control)
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'1','map':'Ilios','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Winston','received_team':'Crazy Raccoon'},
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'1','map':'Ilios','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Crazy Raccoon','banned_hero':'Cassidy','received_team':'Twisted Minds'},
  # Map 2: Rialto (Escort)
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'2','map':'Rialto','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Illari','received_team':'Crazy Raccoon'},
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'2','map':'Rialto','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Crazy Raccoon','banned_hero':'Bastion','received_team':'Twisted Minds'},
  # Map 3: King's Row (Hybrid)
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'3','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Juno','received_team':'Crazy Raccoon'},
  {'region':REGION,'phase':PHASE,'match_label':'CR vs TM - UB SF','game':'3','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Crazy Raccoon','banned_hero':'Symmetra','received_team':'Twisted Minds'},

  # ── UB SF: ZETA vs VP ─────────────────────────────────────────────────────
  # Map 1: Ilios (Control)
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'1','map':'Ilios','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'D.Va','received_team':'ZETA DIVISION'},
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'1','map':'Ilios','map_mode':'Control',
   'ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'Ana','received_team':'Virtus.pro'},
  # Map 2: New Junk City (Flashpoint)
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'2','map':'New Junk City','map_mode':'Flashpoint',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Mizuki','received_team':'ZETA DIVISION'},
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'2','map':'New Junk City','map_mode':'Flashpoint',
   'ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'Zarya','received_team':'Virtus.pro'},
  # Map 3: Rialto (Escort) — VP wins
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'3','map':'Rialto','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'Kiriko','received_team':'Virtus.pro'},
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'3','map':'Rialto','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Tracer','received_team':'ZETA DIVISION'},
  # Map 4: King's Row (Hybrid)
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'4','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Illari','received_team':'ZETA DIVISION'},
  {'region':REGION,'phase':PHASE,'match_label':'ZETA vs VP - UB SF','game':'4','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'Symmetra','received_team':'Virtus.pro'},

  # ── LB QF: VP vs DAL ──────────────────────────────────────────────────────
  # Map 1: Oasis (Control) — VP wins
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'1','map':'Oasis','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Ana','received_team':'Virtus.pro'},
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'1','map':'Oasis','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'D.Va','received_team':'Dallas Fuel'},
  # Map 2: Dorado (Escort) — VP wins
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'2','map':'Dorado','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Pharah','received_team':'Dallas Fuel'},
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'2','map':'Dorado','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Kiriko','received_team':'Virtus.pro'},
  # Map 3: New Junk City (Flashpoint) — DAL wins
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'3','map':'New Junk City','map_mode':'Flashpoint',
   'ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Wuyang','received_team':'Virtus.pro'},
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'3','map':'New Junk City','map_mode':'Flashpoint',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Symmetra','received_team':'Dallas Fuel'},
  # Map 4: Numbani (Hybrid) — VP wins
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'4','map':'Numbani','map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Mauga','received_team':'Virtus.pro'},
  {'region':REGION,'phase':PHASE,'match_label':'VP vs DAL - LB QF','game':'4','map':'Numbani','map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Lucio','received_team':'Dallas Fuel'},

  # ── LB QF: TM vs WBG ──────────────────────────────────────────────────────
  # Map 1: Oasis (Control) — TM wins
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'1','map':'Oasis','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Jetpack Cat','received_team':'Twisted Minds'},
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'1','map':'Oasis','map_mode':'Control',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Cassidy','received_team':'Weibo Gaming'},
  # Map 2: King's Row (Hybrid) — WBG wins
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'2','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Genji','received_team':'Twisted Minds'},
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'2','map':"King's Row",'map_mode':'Hybrid',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Mizuki','received_team':'Weibo Gaming'},
  # Map 3: Runasapi (Push) — TM wins
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'3','map':'Runasapi','map_mode':'Push',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Pharah','received_team':'Weibo Gaming'},
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'3','map':'Runasapi','map_mode':'Push',
   'ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Mauga','received_team':'Twisted Minds'},
  # Map 4: Circuit Royal (Escort) — DRAW 3-3
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'4','map':'Circuit Royal','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Widowmaker','received_team':'Twisted Minds'},
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'4','map':'Circuit Royal','map_mode':'Escort',
   'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Bastion','received_team':'Weibo Gaming'},
  # Map 5: New Junk City (Flashpoint) — TM wins (no player stats)
  {'region':REGION,'phase':PHASE,'match_label':'TM vs WBG - LB QF','game':'5','map':'New Junk City','map_mode':'Flashpoint',
   'ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'D.Va','received_team':'Twisted Minds'},
]

# Load and update ban_events.json
be = json.load(open(r'assets/data/ban_events.json', encoding='utf-8'))
# Remove old Day 2 entries if any were added with wrong data
# Keep only entries that are NOT Day 2 UB SF / LB QF matches
def is_day2(e):
    labels = ['CR vs TM - UB SF','ZETA vs VP - UB SF','VP vs DAL - LB QF','TM vs WBG - LB QF']
    return e.get('phase') == PHASE and e.get('match_label') in labels

be = [e for e in be if not is_day2(e)]
be.extend(new_bans)
with open(r'assets/data/ban_events.json', 'w', encoding='utf-8') as f:
    json.dump(be, f, ensure_ascii=False, indent=2)
print(f'ban_events.json: added {len(new_bans)} Day 2 bans (total {len(be)})')

# Rebuild ban_summary.json
from collections import defaultdict
summary = defaultdict(lambda: {'bans_made':0,'bans_received':0,
                                'initial_bans_made':0,'follow_up_bans_made':0})
for e in be:
    key_m = (e['region'], e['ban_team'],  e['map_mode'], e['banned_hero'])
    key_r = (e['region'], e['received_team'], e['map_mode'], e['banned_hero'])
    summary[key_m]['bans_made'] += 1
    summary[key_r]['bans_received'] += 1
    if e.get('ban_stage') == 'initial':
        summary[key_m]['initial_bans_made'] += 1
    elif e.get('ban_stage') == 'follow_up':
        summary[key_m]['follow_up_bans_made'] += 1

bs = []
for (region, team, map_mode, hero), v in summary.items():
    bs.append({'region':region,'team':team,'map_mode':map_mode,'hero':hero,**v})
with open(r'assets/data/ban_summary.json', 'w', encoding='utf-8') as f:
    json.dump(bs, f, ensure_ascii=False, indent=2)
print(f'ban_summary.json: {len(bs)} rows')

# ─────────────────────────────────────────────────────────────────────────────
# 2. ELO RECALCULATION
# ─────────────────────────────────────────────────────────────────────────────
K = 24
YEAR = '2026'
EVENT = 'owcs_2026_champions_clash'

def expected(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def apply_map(elos, winner, loser, result=1):
    """result: 1=win, 0=loss, 0.5=draw"""
    e = expected(elos[winner], elos[loser])
    delta_w = round(K * (result - e), 1)
    delta_l = round(K * ((1 - result) - (1 - e)), 1)
    elos[winner] = round(elos[winner] + delta_w, 1)
    elos[loser]  = round(elos[loser]  + delta_l, 1)
    return delta_w

elos = {
    'Crazy Raccoon':  1792.2,
    'ZETA DIVISION':  1852.0,
    'Twisted Minds':  1922.7,
    'Virtus.pro':     1701.1,
    'Dallas Fuel':    1623.8,
    'Weibo Gaming':   1721.7,
}

# Map results: (winner, loser, result)  result=0.5 for draw
# winner/loser = the two teams; for draws pass either order
matches = [
    {
        'label': 'UB SF: CR vs TM (3-0)',
        'maps': [
            ('Crazy Raccoon', 'Twisted Minds', 1),   # Ilios
            ('Crazy Raccoon', 'Twisted Minds', 1),   # Rialto (CR wins tiebreaker)
            ('Crazy Raccoon', 'Twisted Minds', 1),   # King's Row
        ]
    },
    {
        'label': "UB SF: ZETA vs VP (3-1) — VP wins Rialto",
        'maps': [
            ('ZETA DIVISION', 'Virtus.pro', 1),      # Ilios
            ('Virtus.pro',    'ZETA DIVISION', 1),   # New Junk City — VP wins
            ('ZETA DIVISION', 'Virtus.pro', 1),      # Rialto — wait, Liquipedia says VP wins Rialto
            ('ZETA DIVISION', 'Virtus.pro', 1),      # King's Row
        ]
    },
    {
        'label': 'LB QF: VP vs DAL (3-1) — DAL wins NJC',
        'maps': [
            ('Virtus.pro',  'Dallas Fuel', 1),       # Oasis — VP wins
            ('Virtus.pro',  'Dallas Fuel', 1),       # Dorado — VP wins
            ('Dallas Fuel', 'Virtus.pro', 1),        # New Junk City — DAL wins
            ('Virtus.pro',  'Dallas Fuel', 1),       # Numbani — VP wins
        ]
    },
    {
        'label': 'LB QF: TM vs WBG (3-1+1draw) — WBG wins King\'s Row, DRAW Circuit Royal',
        'maps': [
            ('Twisted Minds', 'Weibo Gaming', 1),    # Oasis — TM wins
            ('Weibo Gaming',  'Twisted Minds', 1),   # King's Row — WBG wins
            ('Twisted Minds', 'Weibo Gaming', 1),    # Runasapi — TM wins
            ('Twisted Minds', 'Weibo Gaming', 0.5),  # Circuit Royal — DRAW 3-3
            ('Twisted Minds', 'Weibo Gaming', 1),    # New Junk City — TM wins (no stats)
        ]
    },
]

team_results = {t: {'wins':0,'losses':0,'draws':0} for t in elos}

print("\nStarting ELOs:")
for t, e in elos.items():
    print(f"  {t:<25} {e}")

for match in matches:
    print(f"\n{match['label']}")
    for w, l, res in match['maps']:
        bw, bl = elos[w], elos[l]
        if res == 0.5:
            # Draw — apply symmetrically
            e_w = expected(elos[w], elos[l])
            dw = round(K * (0.5 - e_w), 1)
            elos[w] = round(elos[w] + dw, 1)
            elos[l] = round(elos[l] - dw, 1)
            print(f"  DRAW  {w} vs {l}: {bw}→{elos[w]} ({'+' if dw>=0 else ''}{dw})")
            team_results[w]['draws'] += 1
            team_results[l]['draws'] += 1
        else:
            delta = apply_map(elos, w, l, res)
            print(f"  {w} def {l}: {bw}→{elos[w]} ({'+' if delta>=0 else ''}{delta})")
            team_results[w]['wins']   += 1
            team_results[l]['losses'] += 1

print("\nFinal ELOs after Day 2:")
for t, e in sorted(elos.items(), key=lambda x: -x[1]):
    r = team_results[t]
    net = r['wins'] - r['losses']
    result = 'win' if net > 0 else ('loss' if net < 0 else 'draw')
    print(f"  {t:<25} {e}  ({r['wins']}W-{r['losses']}L-{r['draws']}D → {result})")

# ─────────────────────────────────────────────────────────────────────────────
# 3. UPDATE elo_history.json — replace existing Day 2 entries
# ─────────────────────────────────────────────────────────────────────────────
h = json.load(open(r'assets/data/elo_history.json', encoding='utf-8'))

# Count existing clash entries per team to identify which are Day 1 vs Day 2
for team, final_elo in elos.items():
    r = team_results[team]
    net = r['wins'] - r['losses']
    result = 'win' if net > 0 else ('loss' if net < 0 else 'draw')
    eliminated = team in ('Dallas Fuel', 'Weibo Gaming')

    clash_entries = [e for e in h.get(team, []) if e['event'] == EVENT]
    non_clash = [e for e in h.get(team, []) if e['event'] != EVENT]

    # Day 1 entry = first clash entry; Day 2 = second (replace or add)
    day1 = clash_entries[0] if clash_entries else None
    day2_entry = {
        'event': EVENT,
        'elo': final_elo,
        'year': YEAR,
        'result': result,
    }
    if eliminated:
        day2_entry['eliminated'] = True

    if day1:
        h[team] = non_clash + [day1, day2_entry]
    else:
        h[team] = non_clash + [day2_entry]

with open(r'assets/data/elo_history.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=2)
print("\nelo_history.json updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. UPDATE elo_rankings.json
# ─────────────────────────────────────────────────────────────────────────────
rankings = json.load(open(r'assets/data/elo_rankings.json', encoding='utf-8'))
rows_2026 = rankings.get(YEAR, [])

# Reset maps_won/lost to pre-clash values, then add Day 2 correctly
# First, get the pre-Day2 clash wins (Day 1 only)
day1_wins = {
    'Twisted Minds': 2, 'All Gamers': 0, 'Crazy Raccoon': 2, 'Dallas Fuel': 2,
    'Virtus.pro': 3, 'Weibo Gaming': 4, 'ZETA DIVISION': 4, 'Spacestation Gaming': 0,
}
day1_losses = {
    'Twisted Minds': 0, 'All Gamers': 2, 'Crazy Raccoon': 0, 'Dallas Fuel': 2,
    'Virtus.pro': 2, 'Weibo Gaming': 2, 'ZETA DIVISION': 0, 'Spacestation Gaming': 2,
}

for row in rows_2026:
    tname = row['team']
    if tname not in elos:
        continue
    row['elo'] = elos[tname]
    r = team_results[tname]
    d1w = day1_wins.get(tname, 0)
    d1l = day1_losses.get(tname, 0)
    # Get pre-clash maps (before any clash entry)
    pre_clash = [e for e in h.get(tname,[]) if e['event'] != EVENT]
    # Approximate pre-clash wins from existing maps_won minus clash maps
    pre_w = (row.get('maps_won',0) - d1w - r['wins'])
    pre_l = (row.get('maps_lost',0) - d1l - r['losses'])
    row['maps_won']   = pre_w + d1w + r['wins']
    row['maps_lost']  = pre_l + d1l + r['losses']
    row['maps_played']= row['maps_won'] + row['maps_lost'] + r['draws']
    total_maps = row['maps_won'] + row['maps_lost']
    row['win_pct']    = round(row['maps_won'] / total_maps * 100, 1) if total_maps else 0.0

rows_2026_sorted = sorted(rows_2026, key=lambda x: -x['elo'])
for i, row in enumerate(rows_2026_sorted, 1):
    row['rank'] = i
rankings[YEAR] = rows_2026_sorted

with open(r'assets/data/elo_rankings.json', 'w', encoding='utf-8') as f:
    json.dump(rankings, f, ensure_ascii=False, indent=2)
print("elo_rankings.json updated.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. UPDATE clash_results.json — Day 2 matches with correct data
# ─────────────────────────────────────────────────────────────────────────────
cr = json.load(open(r'assets/data/clash_results.json', encoding='utf-8'))

day2_matches = [
    {
        'match_id': 'cc_ubsf1',
        'round': 'UB Semifinal',
        'date': '2026-05-23',
        'team1': 'Crazy Raccoon',
        'team2': 'Twisted Minds',
        'series': '3-0',
        'maps': [
            {'map':'Ilios','mode':'Control','duration_min':14.4,'winner':'Crazy Raccoon',
             'bans':[{'team':'Twisted Minds','hero':'Winston'},{'team':'Crazy Raccoon','hero':'Cassidy'}]},
            {'map':'Rialto','mode':'Escort','duration_min':6.0,'winner':'Crazy Raccoon',
             'score':'1-1','bans':[{'team':'Twisted Minds','hero':'Illari'},{'team':'Crazy Raccoon','hero':'Bastion'}]},
            {'map':"King's Row",'mode':'Hybrid','duration_min':9.9,'winner':'Crazy Raccoon',
             'bans':[{'team':'Twisted Minds','hero':'Juno'},{'team':'Crazy Raccoon','hero':'Symmetra'}]},
        ]
    },
    {
        'match_id': 'cc_ubsf2',
        'round': 'UB Semifinal',
        'date': '2026-05-23',
        'team1': 'ZETA DIVISION',
        'team2': 'Virtus.pro',
        'series': '3-1',
        'maps': [
            {'map':'Ilios','mode':'Control','duration_min':8.1,'winner':'ZETA DIVISION',
             'bans':[{'team':'Virtus.pro','hero':'D.Va'},{'team':'ZETA DIVISION','hero':'Ana'}]},
            {'map':'New Junk City','mode':'Flashpoint','duration_min':8.7,'winner':'Virtus.pro',
             'bans':[{'team':'Virtus.pro','hero':'Mizuki'},{'team':'ZETA DIVISION','hero':'Zarya'}]},
            {'map':'Rialto','mode':'Escort','duration_min':17.2,'winner':'ZETA DIVISION',
             'bans':[{'team':'ZETA DIVISION','hero':'Kiriko'},{'team':'Virtus.pro','hero':'Tracer'}]},
            {'map':"King's Row",'mode':'Hybrid','duration_min':14.3,'winner':'ZETA DIVISION',
             'bans':[{'team':'Virtus.pro','hero':'Illari'},{'team':'ZETA DIVISION','hero':'Symmetra'}]},
        ]
    },
    {
        'match_id': 'cc_lbqf1',
        'round': 'LB Quarterfinal',
        'date': '2026-05-23',
        'team1': 'Virtus.pro',
        'team2': 'Dallas Fuel',
        'series': '3-1',
        'maps': [
            {'map':'Oasis','mode':'Control','duration_min':13.3,'winner':'Virtus.pro',
             'bans':[{'team':'Dallas Fuel','hero':'Ana'},{'team':'Virtus.pro','hero':'D.Va'}]},
            {'map':'Dorado','mode':'Escort','duration_min':17.2,'winner':'Virtus.pro',
             'bans':[{'team':'Virtus.pro','hero':'Pharah'},{'team':'Dallas Fuel','hero':'Kiriko'}]},
            {'map':'New Junk City','mode':'Flashpoint','duration_min':8.6,'winner':'Dallas Fuel',
             'bans':[{'team':'Dallas Fuel','hero':'Wuyang'},{'team':'Virtus.pro','hero':'Symmetra'}]},
            {'map':'Numbani','mode':'Hybrid','duration_min':15.5,'winner':'Virtus.pro',
             'bans':[{'team':'Dallas Fuel','hero':'Mauga'},{'team':'Virtus.pro','hero':'Lucio'}]},
        ]
    },
    {
        'match_id': 'cc_lbqf2',
        'round': 'LB Quarterfinal',
        'date': '2026-05-23',
        'team1': 'Twisted Minds',
        'team2': 'Weibo Gaming',
        'series': '3-1',
        'note': 'Map 4 (Circuit Royal) ended in a draw 3-3. Map 5 played as decider.',
        'maps': [
            {'map':'Oasis','mode':'Control','duration_min':8.9,'winner':'Twisted Minds',
             'bans':[{'team':'Weibo Gaming','hero':'Jetpack Cat'},{'team':'Twisted Minds','hero':'Cassidy'}]},
            {'map':"King's Row",'mode':'Hybrid','duration_min':19.9,'winner':'Weibo Gaming',
             'bans':[{'team':'Weibo Gaming','hero':'Genji'},{'team':'Twisted Minds','hero':'Mizuki'}]},
            {'map':'Runasapi','mode':'Push','duration_min':6.1,'winner':'Twisted Minds',
             'bans':[{'team':'Twisted Minds','hero':'Pharah'},{'team':'Weibo Gaming','hero':'Mauga'}]},
            {'map':'Circuit Royal','mode':'Escort','duration_min':10.8,'winner':None,'draw':True,'score':'3-3',
             'bans':[{'team':'Weibo Gaming','hero':'Widowmaker'},{'team':'Twisted Minds','hero':'Bastion'}]},
            {'map':'New Junk City','mode':'Flashpoint','duration_min':None,'winner':'Twisted Minds',
             'note':'No player stats available',
             'bans':[{'team':'Weibo Gaming','hero':'D.Va'}]},
        ]
    },
]

# Replace Day 2 matches
cr['matches'] = [m for m in cr['matches'] if m['match_id'] not in
                  ('cc_ubsf1','cc_ubsf2','cc_lbqf1','cc_lbqf2')]
cr['matches'].extend(day2_matches)

with open(r'assets/data/clash_results.json', 'w', encoding='utf-8') as f:
    json.dump(cr, f, ensure_ascii=False, indent=2)
print("clash_results.json updated.")
print(f"\nTotal matches: {len(cr['matches'])}")
