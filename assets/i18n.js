/**
 * OWCStats i18n — EN (default) / KO toggle
 * Usage:  t('key')            → translated string
 *         t('key',{x:'val'}) → with {x} placeholder substitution
 *         applyI18n()         → update all data-i18n / data-i18n-ph elements
 *         toggleLang()        → flip EN↔KO, persist to localStorage, dispatch 'langchange'
 */
(function () {
  const S = {
    en: {
      /* ── common ────────────────────────── */
      'no.data':              'No data',
      'bans.made':            'Bans Made',
      'bans.received':        'Bans Received',

      /* ── elo.html ──────────────────────── */
      'elo.hero.desc':        'Global team ratings based on map-by-map results. K=24, Base=1400.',
      'search.placeholder':   'Search team…',
      'nav.rankings':         '📊 Rankings',
      'nav.trend':            '📈 ELO Trend',
      'nav.overall':          'Overall',

      /* ── teams.html ────────────────────── */
      'teams.hero.desc':      'Regional team profiles — ELO history, roster & ban stats',
      'teams.region.header':  'Region',
      'teams.all':            'All',
      'teams.back':           '← Back to list',
      'teams.season.record':  'Season Record',
      'teams.rank':           'Rank',
      'teams.wl':             'W / L',
      'teams.winpct':         'Win %',
      'teams.roster':         'Roster',
      'teams.player':         'Player',
      'teams.role':           'Role',
      'teams.games':          'Games',
      'teams.no.players':     'No player data',
      'teams.elo.trend':      'ELO Trend — First appearance to present',
      'teams.bans.made':      '🔴 Most Banned Heroes',
      'teams.bans.received':  '🛡️ Most Banned Against',
      'teams.no.part':        'Did not participate (ELO held)',

      /* ── clash.html ────────────────────── */
      'clash.made.desc':      'Bans this team used',
      'clash.recv.desc':      'Bans opponents used against this team',
      'clash.made.btn':       '🔴 Bans Made',
      'clash.recv.btn':       '🛡️ Bans Received',

      /* ── ban-calculator.html ────────────── */
      'bc.desc':              'OWCS 2026 ban simulator — select a map, click a ban slot to see historical ban tendencies inline.',
      'bc.reset.all':         'Reset All Sets',
      'bc.reset.set':         'Reset Set',
      'bc.matchup.note':      'Select teams in the ban calculator to auto-fill.',
      'bc.sugg.made':         '🔴 {team} key bans',
      'bc.sugg.recv':         '🛡️ {team} frequently banned against',
      'bc.insight.made':      '🔴 {team} Bans Made',
      'bc.insight.recv':      '🛡️ {team} Bans Received',
      'bc.insight.opp':       '⚔️ {opp} Expected Bans',
      'bc.hero.deselect':     'Deselect',
      'bc.hero.key.ban':      '🔴 Key ban',
      'bc.hero.often.banned': '🛡️ Often banned',
    },
    ko: {
      /* ── common ────────────────────────── */
      'no.data':              '데이터 없음',
      'bans.made':            '밴을 한 것',
      'bans.received':        '밴을 당한 것',

      /* ── elo.html ──────────────────────── */
      'elo.hero.desc':        '맵별 결과 기반 글로벌 팀 레이팅. K=24, Base=1400.',
      'search.placeholder':   '팀 검색…',
      'nav.rankings':         '📊 순위',
      'nav.trend':            '📈 ELO 추이',
      'nav.overall':          '전체',

      /* ── teams.html ────────────────────── */
      'teams.hero.desc':      '지역별 팀 프로필 — ELO 이력, 로스터, 밴 통계',
      'teams.region.header':  '지역',
      'teams.all':            '전체',
      'teams.back':           '← 목록으로',
      'teams.season.record':  '시즌 기록',
      'teams.rank':           '랭킹',
      'teams.wl':             '승 / 패',
      'teams.winpct':         '승률',
      'teams.roster':         '로스터',
      'teams.player':         '플레이어',
      'teams.role':           '포지션',
      'teams.games':          '게임',
      'teams.no.players':     '선수 데이터 없음',
      'teams.elo.trend':      'ELO 추이 — 첫 등장부터 현재까지',
      'teams.bans.made':      '🔴 많이 밴한 영웅',
      'teams.bans.received':  '🛡️ 많이 당한 밴',
      'teams.no.part':        '미출전 (ELO 유지)',

      /* ── clash.html ────────────────────── */
      'clash.made.desc':      '이 팀이 직접 사용한 밴',
      'clash.recv.desc':      '상대가 이 팀 상대로 사용한 밴',
      'clash.made.btn':       '🔴 밴을 한 것',
      'clash.recv.btn':       '🛡️ 밴을 당한 것',

      /* ── ban-calculator.html ────────────── */
      'bc.desc':              'OWCS 2026 밴 시뮬레이터. 맵 선택 후 밴 클릭 시 팀별 역대 밴 경향이 인라인으로 추천됩니다.',
      'bc.reset.all':         '모든 세트 초기화',
      'bc.reset.set':         '세트 초기화',
      'bc.matchup.note':      '밴 계산기에서 팀을 선택하면 자동으로 반영됩니다.',
      'bc.sugg.made':         '🔴 {team}의 주요 밴',
      'bc.sugg.recv':         '🛡️ {team}이 자주 밴당하는 영웅',
      'bc.insight.made':      '🔴 {team} 주요 밴',
      'bc.insight.recv':      '🛡️ {team} 밴당한 영웅',
      'bc.insight.opp':       '⚔️ {opp} 예상 밴',
      'bc.hero.deselect':     '선택 취소',
      'bc.hero.key.ban':      '🔴 주요 밴',
      'bc.hero.often.banned': '🛡️ 밴당함',
    },
  };

  window.SITE_LANG = localStorage.getItem('owcstats-lang') || 'en';

  window.t = function (key, vars) {
    const dict = S[SITE_LANG] || S.en;
    let str = dict[key] !== undefined ? dict[key] : (S.en[key] !== undefined ? S.en[key] : key);
    if (vars) {
      for (const [k, v] of Object.entries(vars)) str = str.replace('{' + k + '}', v);
    }
    return str;
  };

  window.applyI18n = function () {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
      el.placeholder = t(el.getAttribute('data-i18n-ph'));
    });
    document.querySelectorAll('[data-i18n-btn]').forEach(el => {
      el.textContent = t(el.getAttribute('data-i18n-btn'));
    });
    document.documentElement.lang = SITE_LANG === 'ko' ? 'ko' : 'en';
    // Update toggle button label if present
    const btn = document.getElementById('lang-toggle');
    if (btn) btn.textContent = SITE_LANG === 'ko' ? 'EN' : '한';
  };

  window.toggleLang = function () {
    window.SITE_LANG = SITE_LANG === 'en' ? 'ko' : 'en';
    localStorage.setItem('owcstats-lang', SITE_LANG);
    applyI18n();
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: SITE_LANG } }));
  };
})();
