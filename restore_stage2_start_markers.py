# -*- coding: utf-8 -*-
"""
restore_stage2_start_markers.py — build_site_data.py 재실행 후
elo_history.json에 Stage 2 시작 마커(result:"start")를 복원한다.

배경: 시작 마커는 inject_stage2_initial_elo.py가 JSON에 직접 주입한 것이라
CSV 파이프라인으로 재생성하면 사라진다. 원본 수치는 재계산 시점의 ELO가 아니라
'S2 시작 시점' 값이어야 하므로, 재계산 전에 떠 둔 스냅샷
(Elo-Rating/stage2_start_snapshot.json)에서 복원한다.

삽입 위치: 같은 event_id의 첫 매치 엔트리 '앞' (스테이지 시작점이므로).
"""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parent
HISTORY = SITE / "assets" / "data" / "elo_history.json"
SNAPSHOT = SITE.parent / "Elo-Rating" / "stage2_start_snapshot.json"


def main():
    hist = json.loads(HISTORY.read_text(encoding="utf-8"))
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8-sig"))

    restored = 0
    for team, starts in snap.items():
        if not isinstance(starts, list):
            starts = [starts]
        entries = hist.setdefault(team, [])
        for s in starts:
            ev, elo = s["event"], s["elo"]
            if any(e.get("event") == ev and e.get("result") == "start" for e in entries):
                continue
            marker = {"event": ev, "elo": elo, "year": "2026", "result": "start"}
            pos = next((i for i, e in enumerate(entries) if e.get("event") == ev), len(entries))
            entries.insert(pos, marker)
            restored += 1

    HISTORY.write_text(json.dumps(hist, ensure_ascii=False), encoding="utf-8")
    print(f"restored {restored} start markers for {len(snap)} teams")


if __name__ == "__main__":
    main()
