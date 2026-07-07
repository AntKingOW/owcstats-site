// ── 팀 로고 공용 모듈 ─────────────────────────────────────────────────────────
// 규칙: assets/logos/<slugify(팀명)>.<ext>, 실패 시 이니셜 원형 SVG fallback.
// 새 팀 로고 추가 시: png 외 확장자는 LOGO_EXT_MAP에, slug 예외는 LOGO_SLUG_OVERRIDES에 등록.
// (teams/players/tournaments.html의 중복 구현을 대체하는 단일 소스 — 신규 페이지는 이것을 사용)

const LOGO_SLUG_OVERRIDES = {
  "Tokyo Ta1yo's": 'tokyo-ta1yos',
};

const LOGO_EXT_MAP = {
  'cheeseburger': 'webp', 'jd-gaming': 'webp', 'jdg-gaming': 'webp',
  'naive-piggy': 'webp', 'new-era': 'webp', 'please-not-hero-ban': 'webp',
  'rankres': 'webp', 'zan-esports': 'webp',
  'poker-face': 'svg', 'team-falcons': 'svg', 'the-gatos-guapos': 'svg',
};

function slugify(name) {
  return String(name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

function teamLogoImg(teamName, size) {
  size = size || 52;
  const slug = LOGO_SLUG_OVERRIDES[teamName] || slugify(teamName);
  const ext = LOGO_EXT_MAP[slug] || 'png';
  const src = 'assets/logos/' + slug + '.' + ext;
  const initials = teamName.replace(/[^A-Za-z0-9 ]/g, '').split(/\s+/).filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase() || '?';
  const hue = [...teamName].reduce((h, c) => (h * 31 + c.charCodeAt(0)) & 0xffff, 0) % 360;
  const fb = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="' + size + '" height="' + size + '"><circle cx="' + (size/2) + '" cy="' + (size/2) + '" r="' + (size/2) + '" fill="hsl(' + hue + ',55%,35%)"/><text x="50%" y="50%" dy=".35em" text-anchor="middle" font-size="' + Math.round(size*0.36) + '" font-weight="700" fill="white" font-family="sans-serif">' + initials + '</text></svg>');
  return '<img class="team-logo-img" src="' + src + '" width="' + size + '" height="' + size + '" alt="" onerror="this.onerror=null;this.src=\'' + fb + '\'" loading="lazy" style="object-fit:contain">';
}
