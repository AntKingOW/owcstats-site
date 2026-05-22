// Inject shared navigation
(function() {
  const pages = [
    { href: 'index.html', label: 'Home' },
    { href: 'clash.html', label: '🌏 Champion Clash', special: true },
    { href: 'elo.html',   label: 'ELO Rating' },
    { href: 'teams.html', label: 'Teams' },
    { href: 'players.html', label: 'Player Stats' },
    { href: 'ban-calculator.html', label: 'Ban Calculator' },
  ];

  const current = location.pathname.split('/').pop() || 'index.html';

  const nav = document.createElement('nav');
  nav.innerHTML = `
    <a class="nav-logo" href="index.html">OWCStats</a>
    <ul class="nav-links">
      ${pages.map(p => `
        <li><a href="${p.href}" class="${current === p.href ? 'active' : ''}${p.special ? ' nav-special' : ''}">${p.label}</a></li>
      `).join('')}
    </ul>
  `;
  document.body.prepend(nav);
})();
