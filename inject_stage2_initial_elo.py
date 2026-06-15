"""
Stage 2 시작 시점 ELO 주입 스크립트.

신규/승계/합병 팀을 elo_rankings.json + elo_history.json에 반영한다.

규칙:
- 신생팀: ELO 1400, region 명시
- 승계팀: 구 팀의 마지막 ELO를 새 이름으로 entry 추가 (구 entry는 S1 history용으로 유지)
- 합병팀: 강한 쪽 ELO 승계 (예: ZANSIDE GAMING ← Onside Gaming 1499.6)
- 리브랜드: 구 팀명에 history 없으면 신생 처리 (예: Team KK → Kitsune Kage)
"""
from __future__ import annotations

import json
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
RANKINGS = ROOT / "assets" / "data" / "elo_rankings.json"
HISTORY = ROOT / "assets" / "data" / "elo_history.json"

# (team_name, region) -> elo. 신생팀 + 승계팀.
STAGE2_NEW_TEAMS: list[dict] = [
    # Korea — 합병 (Onside 승계) + 신생 2팀 + S1 유지 2팀
    {"team": "ZANSIDE GAMING",       "region": "Korea",   "elo": 1499.6, "source": "merge:Onside Gaming"},
    {"team": "O2 Blast",             "region": "Korea",   "elo": 1400,   "source": "new"},
    {"team": "SuperBad",             "region": "Korea",   "elo": 1400,   "source": "new"},

    # Japan — 신생 3팀
    {"team": "REVATI",               "region": "Japan",   "elo": 1400,   "source": "new"},
    {"team": "Uwinks",               "region": "Japan",   "elo": 1400,   "source": "new"},
    {"team": "MURASH GAMING",        "region": "Japan",   "elo": 1400,   "source": "new"},

    # Pacific — 승계 3팀 + 신생 2팀
    {"team": "SHENGSHI Esports",     "region": "Pacific", "elo": 1527.5, "source": "succession:The Gatos Guapos"},
    {"team": "Najdorf Esports",      "region": "Pacific", "elo": 1440.5, "source": "succession:Rankers"},
    {"team": "Trap12",               "region": "Pacific", "elo": 1377.0, "source": "succession:Quasar Esports"},
    {"team": "MENG GONG 3",          "region": "Pacific", "elo": 1400,   "source": "new"},
    {"team": "ELMT",                 "region": "Pacific", "elo": 1400,   "source": "new"},

    # China — 리브랜드 1팀 + 신생 3팀
    {"team": "HUNENG Gaming",        "region": "China",   "elo": 1400,   "source": "new"},
    {"team": "Four Angry Men",       "region": "China",   "elo": 1400,   "source": "new"},
    {"team": "Kitsune Kage",         "region": "China",   "elo": 1400,   "source": "rebrand:Team KK (no S1 data)"},
    {"team": "ReturnZ",              "region": "China",   "elo": 1400,   "source": "new"},

    # EMEA — 승계 1팀 (AL→1234) + 신생 1팀
    {"team": "1234",                 "region": "EMEA",    "elo": 1407.4, "source": "succession:Anyone's Legend"},
    {"team": "Telacy",               "region": "EMEA",    "elo": 1400,   "source": "new"},

    # NA — 승계 1팀
    {"team": "The Kafe",             "region": "NA",      "elo": 1339.3, "source": "succession:Extinction"},
]

# Stage 2 시작 entry를 history에 박을 때 사용할 event_id (지역별 정규시즌)
STAGE2_REGION_EVENT: dict[str, str] = {
    "Korea":   "owcs_2026_asia_s2_korea",
    "Japan":   "owcs_2026_asia_s2_japan",
    "Pacific": "owcs_2026_asia_s2_pacific",
    "China":   "owcs_2026_china_s2",
    "EMEA":    "owcs_2026_emea_s2",
    "NA":      "owcs_2026_na_s2",
}

# S1 시드로 Stage 2에 참가하는 기존 팀들 (지역별).
# 이들은 현재 elo_rankings의 ELO를 그대로 S2 시작점으로 사용.
STAGE2_RETURNING_TEAMS: dict[str, list[str]] = {
    "Korea": [
        "ZETA DIVISION", "Team Falcons", "Crazy Raccoon", "T1",
        "Cheeseburger", "Poker Face",  # S1 ELO 유지 (Open Qualifier 통과한 기존 팀)
    ],
    "Japan": [
        "VARREL", "Enter Force.36", "99DIVINE",
        "Please Not Hero Ban", "Lazuli",  # Open Qualifier로 재진입
    ],
    "Pacific": [
        "Team Secret",
    ],
    "China": [
        "Weibo Gaming", "All Gamers", "JD Gaming", "Solus Victorem",
    ],
    "EMEA": [
        "Twisted Minds", "Virtus.pro", "Geekay Esports", "Al Qadsiah",
    ],
    "NA": [
        "Dallas Fuel", "Spacestation Gaming", "Team Liquid", "LuneX Gaming",
        "Disguised",  # P/R 통과
    ],
}


def update_rankings():
    data = json.loads(RANKINGS.read_text(encoding="utf-8"))
    existing_teams = {t["team"] for t in data["2026"]}

    added = []
    for new in STAGE2_NEW_TEAMS:
        if new["team"] in existing_teams:
            print(f"  [SKIP] {new['team']} already in rankings")
            continue
        entry = {
            "rank": 0,  # 재정렬 시 갱신
            "team": new["team"],
            "elo": new["elo"],
            "region": new["region"],
            "maps_played": 0,
            "maps_won": 0,
            "maps_lost": 0,
            "maps_drawn": 0,
            "win_pct": 0.0,
        }
        data["2026"].append(entry)
        added.append(new["team"])

    # rank 재정렬
    data["2026"].sort(key=lambda t: -t["elo"])
    for i, t in enumerate(data["2026"], 1):
        t["rank"] = i

    RANKINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nrankings: {len(added)}팀 추가됨")
    for t in added: print(f"  + {t}")


def update_history():
    data = json.loads(HISTORY.read_text(encoding="utf-8"))
    rankings = json.loads(RANKINGS.read_text(encoding="utf-8"))
    elo_by_team = {t["team"]: t["elo"] for t in rankings["2026"]}

    added = []

    def add_start_entry(team: str, region: str, elo: float):
        event_id = STAGE2_REGION_EVENT[region]
        if team not in data:
            data[team] = []
        if any(e.get("event") == event_id and e.get("result") == "start" for e in data[team]):
            print(f"  [SKIP] {team} already has stage 2 start entry")
            return False
        data[team].append({
            "event": event_id,
            "elo": elo,
            "year": "2026",
            "result": "start",
        })
        return True

    # 신생/승계 팀
    for new in STAGE2_NEW_TEAMS:
        if add_start_entry(new["team"], new["region"], new["elo"]):
            added.append(f"{new['team']} (new/succession, {new['elo']})")

    # 기존 시드 팀
    for region, teams in STAGE2_RETURNING_TEAMS.items():
        for team in teams:
            if team not in elo_by_team:
                print(f"  [WARN] {team} not in rankings; skipping")
                continue
            elo = elo_by_team[team]
            if add_start_entry(team, region, elo):
                added.append(f"{team} (returning, {elo})")

    HISTORY.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nhistory: {len(added)}팀에 Stage 2 시작점 entry 추가됨")
    for t in added: print(f"  + {t}")


if __name__ == "__main__":
    print("=== Stage 2 시작 ELO 주입 ===\n")
    print("[1] elo_rankings.json 업데이트")
    update_rankings()
    print("\n[2] elo_history.json 업데이트")
    update_history()
    print("\n완료.")
