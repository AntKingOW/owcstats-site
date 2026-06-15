import json

PHASE = 'Champions Clash'

new_bans = [
  # TM vs AG - Oasis
  {'region':'Intl','phase':PHASE,'match_label':'TM vs AG - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Symmetra','received_team':'All Gamers'},
  {'region':'Intl','phase':PHASE,'match_label':'TM vs AG - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'All Gamers','banned_hero':'Lucio','received_team':'Twisted Minds'},
  # TM vs AG - New Junk City
  {'region':'Intl','phase':PHASE,'match_label':'TM vs AG - UB QF','game':'2','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'Twisted Minds','banned_hero':'Lucio','received_team':'All Gamers'},
  {'region':'Intl','phase':PHASE,'match_label':'TM vs AG - UB QF','game':'2','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'All Gamers','banned_hero':'Sojourn','received_team':'Twisted Minds'},
  # CR vs DAL - Oasis
  {'region':'Intl','phase':PHASE,'match_label':'CR vs DAL - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Bastion','received_team':'Crazy Raccoon'},
  {'region':'Intl','phase':PHASE,'match_label':'CR vs DAL - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Crazy Raccoon','banned_hero':'Ana','received_team':'Dallas Fuel'},
  # CR vs DAL - Circuit Royal
  {'region':'Intl','phase':PHASE,'match_label':'CR vs DAL - UB QF','game':'2','map':'Circuit Royal','map_mode':'Escort','ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Jetpack Cat','received_team':'Crazy Raccoon'},
  {'region':'Intl','phase':PHASE,'match_label':'CR vs DAL - UB QF','game':'2','map':'Circuit Royal','map_mode':'Escort','ban_stage':'initial','ban_team':'Crazy Raccoon','banned_hero':'Widowmaker','received_team':'Dallas Fuel'},
  # VP vs WBG - Oasis
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Symmetra','received_team':'Virtus.pro'},
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Zarya','received_team':'Weibo Gaming'},
  # VP vs WBG - Numbani
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'2','map':'Numbani','map_mode':'Hybrid','ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Jetpack Cat','received_team':'Weibo Gaming'},
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'2','map':'Numbani','map_mode':'Hybrid','ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Cassidy','received_team':'Virtus.pro'},
  # VP vs WBG - New Junk City
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'3','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'Virtus.pro','banned_hero':'Wuyang','received_team':'Weibo Gaming'},
  {'region':'Intl','phase':PHASE,'match_label':'VP vs WBG - UB QF','game':'3','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Ramattra','received_team':'Virtus.pro'},
  # ZETA vs SSG - Ilios
  {'region':'Intl','phase':PHASE,'match_label':'ZETA vs SSG - UB QF','game':'1','map':'Ilios','map_mode':'Control','ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'D.Va','received_team':'Spacestation Gaming'},
  {'region':'Intl','phase':PHASE,'match_label':'ZETA vs SSG - UB QF','game':'1','map':'Ilios','map_mode':'Control','ban_stage':'initial','ban_team':'Spacestation Gaming','banned_hero':'Ana','received_team':'ZETA DIVISION'},
  # ZETA vs SSG - New Junk City
  {'region':'Intl','phase':PHASE,'match_label':'ZETA vs SSG - UB QF','game':'2','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'Spacestation Gaming','banned_hero':'Illari','received_team':'ZETA DIVISION'},
  {'region':'Intl','phase':PHASE,'match_label':'ZETA vs SSG - UB QF','game':'2','map':'New Junk City','map_mode':'Flashpoint','ban_stage':'initial','ban_team':'ZETA DIVISION','banned_hero':'Sojourn','received_team':'Spacestation Gaming'},
  # DAL vs AG - LB R1 - Antarctic Peninsula
  {'region':'Intl','phase':PHASE,'match_label':'DAL vs AG - LB R1','game':'1','map':'Antarctic Peninsula','map_mode':'Control','ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'D.Va','received_team':'All Gamers'},
  {'region':'Intl','phase':PHASE,'match_label':'DAL vs AG - LB R1','game':'1','map':'Antarctic Peninsula','map_mode':'Control','ban_stage':'initial','ban_team':'All Gamers','banned_hero':'Cassidy','received_team':'Dallas Fuel'},
  # DAL vs AG - LB R1 - Runasapi
  {'region':'Intl','phase':PHASE,'match_label':'DAL vs AG - LB R1','game':'2','map':'Runasapi','map_mode':'Push','ban_stage':'initial','ban_team':'All Gamers','banned_hero':'Ana','received_team':'Dallas Fuel'},
  {'region':'Intl','phase':PHASE,'match_label':'DAL vs AG - LB R1','game':'2','map':'Runasapi','map_mode':'Push','ban_stage':'initial','ban_team':'Dallas Fuel','banned_hero':'Symmetra','received_team':'All Gamers'},
  # WBG vs SSG - LB R1 - Oasis
  {'region':'Intl','phase':PHASE,'match_label':'WBG vs SSG - LB R1','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Spacestation Gaming','banned_hero':'Zarya','received_team':'Weibo Gaming'},
  {'region':'Intl','phase':PHASE,'match_label':'WBG vs SSG - LB R1','game':'1','map':'Oasis','map_mode':'Control','ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Lifeweaver','received_team':'Spacestation Gaming'},
  # WBG vs SSG - LB R1 - King's Row
  {'region':'Intl','phase':PHASE,'match_label':'WBG vs SSG - LB R1','game':'2','map':"King's Row",'map_mode':'Hybrid','ban_stage':'initial','ban_team':'Spacestation Gaming','banned_hero':'Unknown','received_team':'Weibo Gaming'},
  {'region':'Intl','phase':PHASE,'match_label':'WBG vs SSG - LB R1','game':'2','map':"King's Row",'map_mode':'Hybrid','ban_stage':'initial','ban_team':'Weibo Gaming','banned_hero':'Unknown','received_team':'Spacestation Gaming'},
]

be = json.load(open('ban_events.json', encoding='utf-8'))
be = [e for e in be if e.get('phase') != PHASE]
be.extend(new_bans)
with open('ban_events.json', 'w', encoding='utf-8') as f:
    json.dump(be, f, ensure_ascii=False, indent=2)
print(f'ban_events.json: {len(new_bans)}개 밴 이벤트 추가 (총 {len(be)}개)')
