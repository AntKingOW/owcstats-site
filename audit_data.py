"""
Data audit script for owcstats.com
Generates audit_report.html with data quality checks.
"""
import os, re, json, math, csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
ELO_DIR = BASE / "Elo-Rating"
STATS_DIR = BASE / "OWCStats" / "OWCStats"

issues = []
sections = []

# ── helpers ──────────────────────────────────────────────────────────────────

def add_issue(section, severity, msg):
    issues.append({"section": section, "severity": severity, "msg": msg})

def badge(sev):
    color = {"error": "#e74c3c", "warn": "#f39c12", "ok": "#27ae60"}[sev]
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px">{sev.upper()}</span>'

# ── Phase A: ELO CSV ──────────────────────────────────────────────────────────

def audit_elo():
    rows = []
    path = ELO_DIR / "OWCS_2026_GLOBAL_ELO_FINAL.csv"
    if not path.exists():
        add_issue("ELO", "error", f"파일 없음: {path.name}")
        return "<p>파일 없음</p>"

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    elos = []
    html_rows = []
    ok = warn = err = 0

    for r in rows:
        team = r.get("team", "?")
        try:
            elo = float(r["elo"])
            elos.append(elo)
        except:
            add_issue("ELO", "error", f"ELO 값 파싱 실패: {team}")
            err += 1
            continue

        problems = []
        # 누락 필드
        for col in ["rank", "home_region", "maps_played", "win_pct"]:
            if not r.get(col, "").strip():
                problems.append(f"{col} 누락")

        # 승률 범위
        try:
            wp = float(r["win_pct"])
            if not (0 <= wp <= 100):
                problems.append(f"승률 이상: {wp}")
        except:
            problems.append("승률 파싱 실패")

        # 맵 수
        try:
            mp = int(r["maps_played"])
            mw = int(r["maps_won"])
            ml = int(r["maps_lost"])
            md = int(r.get("maps_drawn", 0))
            if mw + ml + md != mp:
                problems.append(f"맵 합계 불일치: {mw}+{ml}+{md}≠{mp}")
        except:
            problems.append("맵 수 파싱 실패")

        if problems:
            warn += 1
            add_issue("ELO", "warn", f"{team}: {', '.join(problems)}")
            sev = "warn"
        else:
            ok += 1
            sev = "ok"

        html_rows.append(
            f"<tr><td>{r.get('rank','')}</td><td>{team}</td>"
            f"<td>{r.get('home_region','')}</td><td>{r.get('elo','')}</td>"
            f"<td>{r.get('win_pct','')}</td>"
            f"<td>{badge(sev) if problems else badge('ok')}</td></tr>"
        )

    # 이상치 (±3σ)
    if elos:
        mean = sum(elos)/len(elos)
        std = math.sqrt(sum((e-mean)**2 for e in elos)/len(elos))
        for r in rows:
            try:
                e = float(r["elo"])
                if abs(e - mean) > 3*std:
                    add_issue("ELO", "warn", f"ELO 이상치({e:.1f}, 평균{mean:.1f}±{std:.1f}): {r['team']}")
            except:
                pass

    summary = f"총 {len(rows)}팀 | ✅ {ok} | ⚠️ {warn} | ❌ {err}"
    table = f"""
    <p>{summary}</p>
    <table><thead><tr><th>Rank</th><th>Team</th><th>Region</th><th>ELO</th><th>Win%</th><th>Status</th></tr></thead>
    <tbody>{"".join(html_rows)}</tbody></table>
    """
    return table

# ── Phase B: Player Stats CSV ─────────────────────────────────────────────────

def audit_players():
    path = STATS_DIR / "EMEA_NA_PLAYER_STATS_CLEANED.csv"
    if not path.exists():
        add_issue("Players", "error", f"파일 없음: {path.name}")
        return "<p>파일 없음</p>"

    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total = len(rows)
    needs_reocr = sum(1 for r in rows if r.get("NeedsReOCR","").strip().lower() == "yes")
    missing_any = 0
    negative_any = 0
    stat_cols = ["E","A","D","DMG","H","MIT"]
    missing_detail = {}
    negative_detail = {}

    for r in rows:
        pid = f"{r.get('Player','?')} ({r.get('Region','?')})"
        for col in stat_cols:
            v = r.get(col,"").strip()
            if v == "":
                missing_detail.setdefault(col, 0)
                missing_detail[col] += 1
                missing_any += 1
            else:
                try:
                    if float(v) < 0:
                        negative_detail.setdefault(col, 0)
                        negative_detail[col] += 1
                        negative_any += 1
                except:
                    pass

    reocr_pct = needs_reocr/total*100 if total else 0
    if reocr_pct > 10:
        add_issue("Players", "warn", f"NeedsReOCR 비율 높음: {reocr_pct:.1f}% ({needs_reocr}/{total}행)")
    if negative_any:
        add_issue("Players", "error", f"음수 통계값: {negative_detail}")
    if missing_any:
        add_issue("Players", "warn", f"누락값: {missing_detail}")

    rows_by_region = {}
    players_by_region = {}
    for r in rows:
        reg = r.get("Region","?")
        rows_by_region[reg] = rows_by_region.get(reg,0) + 1
        p = r.get("Player","?")
        players_by_region.setdefault(reg, set()).add(p)

    region_html = "".join(
        f"<tr><td>{reg}</td><td>{rows_by_region[reg]}</td><td>{len(players_by_region[reg])}</td></tr>"
        for reg in sorted(rows_by_region)
    )

    html = f"""
    <p>총 {total}행 | NeedsReOCR: {needs_reocr}행 ({reocr_pct:.1f}%) | 누락값: {missing_any} | 음수값: {negative_any}</p>
    <table><thead><tr><th>Region</th><th>행 수</th><th>선수 수</th></tr></thead>
    <tbody>{region_html}</tbody></table>
    <p>통계 컬럼 누락 상세: {missing_detail or "없음"}</p>
    <p>음수값 상세: {negative_detail or "없음"}</p>
    """
    return html

# ── Phase C: Ban Data in Markdown ─────────────────────────────────────────────

def audit_bans():
    pattern = re.compile(
        r'Game\s+\d+\s*-\s*initial ban:\s*(.+?)\s*\/\s*follow-up ban:\s*(.+)',
        re.IGNORECASE
    )
    files = list(STATS_DIR.glob("OWCS_*_2026_*_RESULTS.md"))
    total_files = len(files)
    total_games = 0
    parse_ok = 0
    parse_fail = 0
    fail_lines = []

    for fpath in sorted(files):
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        in_bans = False
        for line in text.splitlines():
            if line.strip().lower().startswith("bans:"):
                in_bans = True
                continue
            if in_bans:
                if re.match(r'^\s*\d+\.\s+Game', line):
                    total_games += 1
                    if pattern.search(line):
                        parse_ok += 1
                    else:
                        parse_fail += 1
                        fail_lines.append(f"{fpath.name}: {line.strip()}")
                elif line.strip() == "" and total_games > 0:
                    continue
                elif re.match(r'^#+\s', line):
                    in_bans = False

    if parse_fail:
        add_issue("Bans", "warn", f"파싱 실패 라인 {parse_fail}개")
    if total_files == 0:
        add_issue("Bans", "error", "RESULTS.md 파일을 찾을 수 없음")

    fail_html = ""
    if fail_lines:
        fail_html = "<details><summary>파싱 실패 라인</summary><pre>" + "\n".join(fail_lines[:20]) + "</pre></details>"

    html = f"""
    <p>RESULTS.md 파일 수: {total_files} | 총 게임 밴 기록: {total_games} | 파싱 성공: {parse_ok} | 실패: {parse_fail}</p>
    {fail_html}
    """
    return html

# ── Phase D: ELO History ─────────────────────────────────────────────────────

def audit_elo_history():
    path = ELO_DIR / "OWCS_2026_GLOBAL_ELO_HISTORY.csv"
    if not path.exists():
        add_issue("ELO History", "warn", "히스토리 파일 없음")
        return "<p>파일 없음</p>"

    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    teams = set(r.get("team","") for r in rows)
    events = set(r.get("event_id","") for r in rows)
    add_issue("ELO History", "ok", f"히스토리: {len(rows)}행, {len(teams)}팀, {len(events)}이벤트")
    return f"<p>총 {len(rows)}행 | 팀 {len(teams)}개 | 이벤트 {len(events)}개</p>"

# ── Render HTML ───────────────────────────────────────────────────────────────

def render():
    elo_html = audit_elo()
    player_html = audit_players()
    ban_html = audit_bans()
    hist_html = audit_elo_history()

    sev_counts = {"error": 0, "warn": 0, "ok": 0}
    for iss in issues:
        sev_counts[iss["severity"]] = sev_counts.get(iss["severity"], 0) + 1

    issue_rows = "".join(
        f"<tr><td>{i['section']}</td><td>{badge(i['severity'])}</td><td>{i['msg']}</td></tr>"
        for i in issues
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>OWCStats 데이터 검수 리포트</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1b2a; color: #e0eaf4; margin: 0; padding: 24px; }}
  h1 {{ color: #f5a524; }} h2 {{ color: #8db9ff; border-bottom: 1px solid #1e3a5f; padding-bottom: 6px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
  th {{ background: #1a3a5c; color: #8db9ff; padding: 8px 12px; text-align: left; }}
  td {{ padding: 6px 12px; border-bottom: 1px solid #1e3a5f; }}
  tr:hover {{ background: #132234; }}
  .summary {{ display: flex; gap: 16px; margin: 16px 0; }}
  .card {{ background: #132234; border-radius: 8px; padding: 16px 24px; text-align: center; }}
  .card .num {{ font-size: 32px; font-weight: bold; }}
  .err {{ color: #e74c3c; }} .warn {{ color: #f39c12; }} .ok {{ color: #27ae60; }}
  pre {{ background: #0a1520; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; }}
  details summary {{ cursor: pointer; color: #8db9ff; }}
</style>
</head>
<body>
<h1>OWCStats 데이터 검수 리포트</h1>
<p>생성 시각: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

<div class="summary">
  <div class="card"><div class="num err">{sev_counts['error']}</div><div>오류</div></div>
  <div class="card"><div class="num warn">{sev_counts['warn']}</div><div>경고</div></div>
  <div class="card"><div class="num ok">{sev_counts['ok']}</div><div>정상</div></div>
</div>

<h2>전체 이슈 목록</h2>
<table><thead><tr><th>섹션</th><th>심각도</th><th>내용</th></tr></thead>
<tbody>{issue_rows}</tbody></table>

<h2>A. ELO 순위 데이터</h2>
{elo_html}

<h2>B. 선수 통계 데이터</h2>
{player_html}

<h2>C. 밴 데이터 (마크다운)</h2>
{ban_html}

<h2>D. ELO 히스토리</h2>
{hist_html}

</body>
</html>"""

    out = Path(__file__).parent / "audit_report.html"
    out.write_text(html, encoding="utf-8")
    print(f"[OK] Report generated: {out}")
    return sev_counts

if __name__ == "__main__":
    counts = render()
    print(f"Errors: {counts['error']} | Warnings: {counts['warn']}")
