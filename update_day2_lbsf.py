"""
Day 2 LB SF: TM vs VP (3-1)
- Map 1: Ilios (Control)       9.05 min  TM wins
- Map 2: New Junk City (Flash) 12.62 min TM wins
- Map 3: Rialto (Escort)       11.27 min VP wins
- Map 4: King's Row (Hybrid)   no stats  TM wins
Bans from Liquipedia.
"""
import json, math
from collections import defaultdict

PHASE = 'Champions Clash'
REGION = 'Intl'
K = 24
YEAR = '2026'
EVENT = 'owcs_2026_champions_clash'

# ─── 1. BAN EVENTS ────────────────────────────────────────────────────────────
new_bans = [
    # Map 1: Ilios (Control)
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'1','map':'Ilios','map_mode':'Control',
     'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Cassidy','received_team':'Twisted Minds'},
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'1','map':'Ilios','map_mode':'Control',
     'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Winston','received_team':'Virtus.pro'},
    # Map 2: New Junk City (Flashpoint)
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'2','map':'New Junk City','map_mode':'Flashpoint',
     'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Illari','received_team':'Twisted Minds'},
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'2','map':'New Junk City','map_mode':'Flashpoint',
     'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Bastion','received_team':'Virtus.pro'},
    # Map 3: Rialto (Escort)
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'3','map':'Rialto','map_mode':'Escort',
     'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Tracer','received_team':'Twisted Minds'},
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'3','map':'Rialto','map_mode':'Escort',
     'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Symmetra','received_team':'Virtus.pro'},
    # Map 4: King's Row (Hybrid)
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'4','map':"King's Row",'map_mode':'Hybrid',
     'ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Juno','received_team':'Twisted Minds'},
    {'region':REGION,'phase':PHASE,'match_label':'TM vs VP - LB SF','game':'4','map':"King's Row",'map_mode':'Hybrid',
     'ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'D.Va','received_team':'Virtus.pro'},
]

be = json.load(open(r'assets/data/ban_events.json', encoding='utf-8'))
be = [e for e in be if not (e.get('phase') == PHASE and e.get('match_label') == 'TM vs VP - LB SF')]
be.extend(new_bans)
with open(r'assets/data/ban_events.json', 'w', encoding='utf-8') as f:
    json.dump(be, f, ensure_ascii=False, indent=2)
print(f'ban_events.json: +{len(new_bans)} bans (total {len(be)})')

# Rebuild ban_summary.json
summary = defaultdict(lambda: {'bans_made':0,'bans_received':0,'initial_bans_made':0,'follow_up_bans_made':0})
for e in be:
    km = (e['region'], e['ban_team'], e['map_mode'], e['banned_hero'])
    kr = (e['region'], e['received_team'], e['map_mode'], e['banned_hero'])
    summary[km]['bans_made'] += 1
    summary[kr]['bans_received'] += 1
    if e.get('ban_stage') == 'initial':
        summary[km]['initial_bans_made'] += 1
    else:
        summary[km]['follow_up_bans_made'] += 1
bs = [{'region':r,'team':t,'map_mode':m,'hero':h,**v} for (r,t,m,h),v in summary.items()]
with open(r'assets/data/ban_summary.json', 'w', encoding='utf-8') as f:
    json.dump(bs, f, ensure_ascii=False, indent=2)
print(f'ban_summary.json: {len(bs)} rows')

# ─── 2. ELO ───────────────────────────────────────────────────────────────────
def expected(a, b): return 1 / (1 + 10 ** ((b - a) / 400))

def apply_map(elos, winner, loser):
    e = expected(elos[winner], elos[loser])
    delta = round(K * (1 - e), 1)
    elos[winner] = round(elos[winner] + delta, 1)
    elos[loser]  = round(elos[loser]  - delta, 1)
    return delta

# Starting ELOs (post previous Day 2 matches)
elos = {'Twisted Minds': 1876.5, 'Virtus.pro': 1708.5}

maps = [
    ('Twisted Minds', 'Virtus.pro'),   # Ilios — TM wins
    ('Twisted Minds', 'Virtus.pro'),   # New Junk City — TM wins
    ('Virtus.pro',    'Twisted Minds'),# Rialto — VP wins
    ('Twisted Minds', 'Virtus.pro'),   # King's Row — TM wins
]

print('\nLB SF: TM vs VP (3-1)')
for w, l in maps:
    bw = elos[w]
    d = apply_map(elos, w, l)
    print(f'  {w} def {l}: {bw}→{elos[w]} ({"+"+str(d) if d>=0 else d})')

print(f'\nFinal: TM={elos["Twisted Minds"]}  VP={elos["Virtus.pro"]}')

# ─── 3. elo_history.json ──────────────────────────────────────────────────────
h = json.load(open(r'assets/data/elo_history.json', encoding='utf-8'))

updates = {
    'Twisted Minds': {'elo': elos['Twisted Minds'], 'result': 'win'},
    'Virtus.pro':    {'elo': elos['Virtus.pro'],    'result': 'loss', 'eliminated': True},
}

for team, info in updates.items():
    clash_entries = [e for e in h.get(team, []) if e['event'] == EVENT]
    non_clash     = [e for e in h.get(team, []) if e['event'] != EVENT]
    day1 = clash_entries[0] if len(clash_entries) >= 1 else None
    day2 = clash_entries[1] if len(clash_entries) >= 2 else None

    day3_entry = {'event': EVENT, 'elo': info['elo'], 'year': YEAR, 'result': info['result']}
    if info.get('eliminated'):
        day3_entry['eliminated'] = True

    rebuilt = non_clash
    if day1: rebuilt.append(day1)
    if day2: rebuilt.append(day2)
    rebuilt.append(day3_entry)
    h[team] = rebuilt

with open(r'assets/data/elo_history.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=2)
print('elo_history.json updated.')

# ─── 4. elo_rankings.json ────────────────────────────────────────────────────
rankings = json.load(open(r'assets/data/elo_rankings.json', encoding='utf-8'))
rows_2026 = rankings.get(YEAR, [])

# TM: 3W 1L across LB SF; VP: 1W 3L
match_results = {
    'Twisted Minds': {'wins': 3, 'losses': 1},
    'Virtus.pro':    {'wins': 1, 'losses': 3},
}

for row in rows_2026:
    tname = row['team']
    if tname not in elos:
        continue
    row['elo'] = elos[tname]
    r = match_results[tname]
    row['maps_won']    = row.get('maps_won', 0)    + r['wins']
    row['maps_lost']   = row.get('maps_lost', 0)   + r['losses']
    row['maps_played'] = row.get('maps_played', 0) + r['wins'] + r['losses']
    total = row['maps_won'] + row['maps_lost']
    row['win_pct'] = round(row['maps_won'] / total * 100, 1) if total else 0.0

rows_sorted = sorted(rows_2026, key=lambda x: -x['elo'])
for i, row in enumerate(rows_sorted, 1):
    row['rank'] = i
rankings[YEAR] = rows_sorted

with open(r'assets/data/elo_rankings.json', 'w', encoding='utf-8') as f:
    json.dump(rankings, f, ensure_ascii=False, indent=2)
print('elo_rankings.json updated.')

# ─── 5. clash_results.json ───────────────────────────────────────────────────
cr = json.load(open(r'assets/data/clash_results.json', encoding='utf-8'))

lbsf_match = {
    'match_id': 'cc_lbsf1',
    'round': 'LB Semifinal',
    'date': '2026-05-23',
    'team1': 'Twisted Minds',
    'team2': 'Virtus.pro',
    'series': '3-1',
    'maps': [
        {'map': 'Ilios', 'mode': 'Control', 'duration_min': 9.05, 'winner': 'Twisted Minds',
         'bans': [{'team': 'Virtus.pro', 'hero': 'Cassidy'}, {'team': 'Twisted Minds', 'hero': 'Winston'}]},
        {'map': 'New Junk City', 'mode': 'Flashpoint', 'duration_min': 12.62, 'winner': 'Twisted Minds',
         'bans': [{'team': 'Virtus.pro', 'hero': 'Illari'}, {'team': 'Twisted Minds', 'hero': 'Bastion'}]},
        {'map': 'Rialto', 'mode': 'Escort', 'duration_min': 11.27, 'winner': 'Virtus.pro',
         'bans': [{'team': 'Virtus.pro', 'hero': 'Tracer'}, {'team': 'Twisted Minds', 'hero': 'Symmetra'}]},
        {'map': "King's Row", 'mode': 'Hybrid', 'duration_min': None, 'winner': 'Twisted Minds',
         'note': 'No player stats available',
         'bans': [{'team': 'Virtus.pro', 'hero': 'Juno'}, {'team': 'Twisted Minds', 'hero': 'D.Va'}]},
    ]
}

# Remove old entry if exists, then append
cr['matches'] = [m for m in cr['matches'] if m['match_id'] != 'cc_lbsf1']
cr['matches'].append(lbsf_match)

with open(r'assets/data/clash_results.json', 'w', encoding='utf-8') as f:
    json.dump(cr, f, ensure_ascii=False, indent=2)
print(f'clash_results.json updated. Total matches: {len(cr["matches"])}')
