// ── Data version (cache-busting) ──────────────────────────────────────────────
// 데이터 파일(JSON) 업데이트 시 이 번호를 올려주세요 → 브라우저 캐시 자동 무효화
window.DATA_V = '20260708c';

// Inject shared navigation
(function() {
  const pages = [
    { href: 'index.html', label: 'Matches' },
    { href: 'tournaments.html', label: 'Tournaments' },
    { href: 'teams.html', label: 'Teams' },
    { href: 'players.html', label: 'Player Stats' },
    { href: 'elo.html',   label: 'ELO Rating' },
    { href: 'ban-calculator.html', label: 'Ban Calculator' },
  ];

  // match.html은 Matches(index)의 하위 페이지로 취급
  let current = location.pathname.split('/').pop() || 'index.html';
  if (current === 'match.html') current = 'index.html';

  const nav = document.createElement('nav');
  nav.innerHTML = `
    <a class="nav-logo" href="index.html">OWCStats</a>
    <ul class="nav-links">
      ${pages.map(p => `
        <li><a href="${p.href}" class="${current === p.href ? 'active' : ''}${p.special ? ' nav-special' : ''}">${p.label}</a></li>
      `).join('')}
    </ul>
    <button id="lang-toggle" class="nav-lang-toggle" title="Toggle language / 언어 전환">한</button>
    <button class="nav-hamburger" aria-label="Toggle menu" aria-expanded="false">&#9776;</button>
  `;
  document.body.prepend(nav);

  // Language toggle
  const langBtn = nav.querySelector('#lang-toggle');
  if (langBtn) {
    // Show correct initial label
    langBtn.textContent = (window.SITE_LANG === 'ko') ? 'EN' : '한';
    langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (typeof window.toggleLang === 'function') window.toggleLang();
    });
  }

  const hamburger = nav.querySelector('.nav-hamburger');

  function openMenu() {
    nav.classList.add('nav-open');
    hamburger.setAttribute('aria-expanded', 'true');
    hamburger.innerHTML = '&#10005;';
  }
  function closeMenu() {
    nav.classList.remove('nav-open');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.innerHTML = '&#9776;';
  }

  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    nav.classList.contains('nav-open') ? closeMenu() : openMenu();
  });

  nav.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', closeMenu));

  document.addEventListener('click', (e) => { if (!nav.contains(e.target)) closeMenu(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

  // ── Mobile sidebar toggle ──────────────────────────────────────────────────
  // Runs after DOM is ready; injects a "▾ 필터" button above any sidebar layout.
  const LAYOUT_SELECTORS = '.elo-layout, .teams-layout, .clash-layout, .layout';
  const SIDEBAR_LABELS = {
    'elo-layout':   '📊 시즌 선택',
    'teams-layout': '🗂️ 지역 / 년도',
    'clash-layout': '🗂️ 팀 메뉴',
    'layout':       '⚙️ 필터',
  };

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(LAYOUT_SELECTORS).forEach(layout => {
      const sidebar = layout.firstElementChild;
      if (!sidebar) return;

      // Determine label
      const layoutClass = Array.from(layout.classList).find(c => SIDEBAR_LABELS[c]) || '';
      const label = SIDEBAR_LABELS[layoutClass] || '☰ 메뉴';

      const btn = document.createElement('button');
      btn.className = 'mobile-sidebar-toggle';
      btn.innerHTML = `<span class="mst-arrow">▾</span> ${label}`;
      layout.parentNode.insertBefore(btn, layout);

      btn.addEventListener('click', () => {
        const isOpen = sidebar.classList.toggle('mob-sidebar-open');
        btn.querySelector('.mst-arrow').textContent = isOpen ? '▴' : '▾';
      });
    });
  });
})();
