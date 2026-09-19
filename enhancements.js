'use strict';
const navigation = document.getElementById('navOverlay');
const navigationToggle = document.querySelector('.nav-toggle');
if (navigation && navigationToggle) {
  function setNavigation(open) {
    navigation.classList.toggle('active', open);
    navigationToggle.classList.toggle('open', open);
    navigation.inert = !open;
    navigationToggle.setAttribute('aria-expanded', String(open));
    navigationToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  }
  window.toggleNav = () => setNavigation(!navigation.classList.contains('active'));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navigation.classList.contains('active')) {
      setNavigation(false);
      navigationToggle.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!navigation.contains(event.target) && !navigationToggle.contains(event.target)) setNavigation(false);
  });
  document.addEventListener('focusin', event => {
    if (!navigation.contains(event.target) && !navigationToggle.contains(event.target)) setNavigation(false);
  });
}
document.querySelectorAll('a[target="_blank"]').forEach(a => a.rel = 'noopener noreferrer');
document.querySelectorAll('a').forEach(a => {
  if (!a.textContent.trim() && !a.getAttribute('aria-label')) {
    const icon = a.querySelector('[class*="fa-"]');
    const label = icon?.className.match(/fa-(discord|x-twitter|instagram|tiktok|twitch)/)?.[1];
    if (label) a.setAttribute('aria-label', label === 'x-twitter' ? 'Everbloom on X' : `Everbloom on ${label}`);
  }
});
const feedButton = document.querySelector('.feed-load');
feedButton?.addEventListener('click', () => {
  const script = document.createElement('script');
  script.src = 'https://elfsightcdn.com/platform.js';
  script.async = true;
  feedButton.disabled = true;
  feedButton.textContent = 'Loading feed…';
  script.onload = () => feedButton.remove();
  script.onerror = () => { feedButton.disabled = false; feedButton.textContent = 'Retry loading feed'; script.remove(); };
  document.head.append(script);
});
if (document.querySelector('.team-grid')) {
  fetch('ranks.json').then(r => { if (!r.ok) throw new Error('Ranks unavailable'); return r.json(); }).then(data => {
    for (const p of Object.values(data.players || {})) {
      const badge = document.getElementById('rank-' + p.id);
      if (badge && typeof p.rank === 'string') badge.textContent = p.rank;
    }
    const updated = document.getElementById('ranks-updated');
    if (updated && typeof data.updated === 'string') updated.textContent = 'Last rank update: ' + data.updated;
  }).catch(() => { /* Keep generated rank data when offline. */ });
}
