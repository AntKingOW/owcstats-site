"""
Merge clash_player_stats.json into player_stats.json.
- Existing players: weighted-average merge by minutes
- New players (WBG + unmatched): append with region tag
"""
import json, re

PER10 = ['dmg_per10','heal_per10','elim_per10','assist_per10','death_per10','mit_per10']

REGION_MAP = {
    'Crazy Raccoon': 'Korea', 'ZETA DIVISION': 'Korea',
    'Twisted Minds': 'EMEA',  'Virtus.pro': 'EMEA',
    'Dallas Fuel': 'NA',
    'Weibo Gaming': 'China',
}

def norm(name):
    """Normalize player name: uppercase, 0→O."""
    return re.sub(r'0', 'O', str(name).upper())

def merge(base, clash):
    """Weighted-average merge clash entry into base entry."""
    m1, m2 = base['minutes'], clash['minutes']
    total = m1 + m2
    result = dict(base)
    result['games']   = base['games'] + clash['games']
    result['minutes'] = round(total, 1)
    for k in PER10:
        result[k] = round((base[k]*m1 + clash[k]*m2) / total, 2)
    # Recalculate ed_ratio from merged elim/death per10
    e = result['elim_per10']
    d = result['death_per10']
    result['ed_ratio'] = round(e/d, 2) if d else 0
    return result

ps = json.load(open(r'assets/data/player_stats.json', encoding='utf-8'))
cs = json.load(open(r'assets/data/clash_player_stats.json', encoding='utf-8'))

# Build lookup: norm_name+team → index in ps
lookup = {}
for i, p in enumerate(ps):
    key = (norm(p['player']), p['team'])
    lookup[key] = i

added, updated = 0, 0
for c in cs:
    key = (norm(c['player']), c['team'])
    if key in lookup:
        idx = lookup[key]
        ps[idx] = merge(ps[idx], c)
        updated += 1
        print(f'  MERGE  {c["team"]} - {c["player"]}')
    else:
        region = REGION_MAP.get(c['team'], 'Intl')
        new_entry = {'region': region, **{k: c[k] for k in
            ['team','player','role','games','minutes']+PER10+['ed_ratio']}}
        ps.append(new_entry)
        added += 1
        print(f'  ADD    {c["team"]} - {c["player"]}')

with open(r'assets/data/player_stats.json', 'w', encoding='utf-8') as f:
    json.dump(ps, f, ensure_ascii=False, indent=2)

print(f'\nDone: {updated} merged, {added} added. Total: {len(ps)} players.')
