import json
import re
from pathlib import Path


ROOT = Path(r"C:\Users\user\Documents\Playground")
OWCSTATS = ROOT / "OWCStats"
BANCALC = ROOT / "BanCalculatorOW"


def extract_json_block(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(.*?)\s*```", text, re.S)
    if not match:
        raise ValueError(f"No JSON block found in {path}")
    return json.loads(match.group(1))


def build_reference():
    rosters = extract_json_block(OWCSTATS / "TEAM_ROSTERS_2026.md")
    heroes = extract_json_block(OWCSTATS / "HEROES.md")
    maps = extract_json_block(OWCSTATS / "MAP_POOL.md")

    teams = sorted({record["team_name"] for record in rosters})
    hero_records = [
        {
            "hero_name_en": hero["hero_name_en"],
            "hero_name_ko": hero["hero_name_ko"],
            "main_role_en": hero["main_role_en"],
            "main_role_ko": hero["main_role_ko"],
            "subrole_en": hero["subrole_en"],
            "subrole_ko": hero["subrole_ko"],
        }
        for hero in heroes
    ]

    hero_records.sort(key=lambda item: (item["main_role_en"], item["hero_name_en"].lower()))
    map_records = sorted(maps, key=lambda item: (item["map_mode"], item["map_name"]))

    return {
        "scope": "OWCS Korea 2026",
        "teams": teams,
        "heroes": hero_records,
        "maps": map_records,
    }


def write_outputs(reference):
    data_dir = BANCALC / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "shared_owcs_reference.json"
    js_path = data_dir / "shared_owcs_reference.js"

    json_payload = json.dumps(reference, ensure_ascii=False, indent=2)
    json_path.write_text(json_payload + "\n", encoding="utf-8")

    js_payload = "window.OWCS_REFERENCE = " + json_payload + ";\n"
    js_path.write_text(js_payload, encoding="utf-8")


if __name__ == "__main__":
    reference = build_reference()
    write_outputs(reference)
    print("BanCalculatorOW shared reference files generated.")
