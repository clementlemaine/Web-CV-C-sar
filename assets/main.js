(() => {
  const doc = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  // --- loader : une fois par session
  let seen = false;
  try { seen = sessionStorage.getItem('cm-seen') === '1'; sessionStorage.setItem('cm-seen', '1'); } catch (_) {}
  if (seen || reduce) doc.classList.add('skip-loader');
  const ready = () => requestAnimationFrame(() => doc.classList.add('loaded'));
  setTimeout(ready, seen || reduce ? 50 : 1500);

  // --- heure de Madrid
  const fmt = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
  const tick = () => document.querySelectorAll('[data-clock]').forEach(el => { el.textContent = fmt.format(new Date()); });
  tick(); setInterval(tick, 15000);

  // --- email assemblé côté client
  const mail = document.querySelector('.mail');
  if (mail) {
    const addr = mail.dataset.u + '@' + mail.dataset.d;
    mail.textContent = addr; mail.href = 'mailto:' + addr;
    const toast = document.querySelector('.toast');
    const btn = document.querySelector('.copy');
    btn.addEventListener('click', () => {
      const done = () => { toast.textContent = btn.dataset.copied; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 1800); };
      (navigator.clipboard ? navigator.clipboard.writeText(addr) : Promise.reject()).then(done, () => { location.href = mail.href; });
    });
  }

  // --- manifeste : mots qui s'allument au scroll
  const words = document.querySelector('[data-words]');
  let wordEls = [];
  if (words) {
    words.innerHTML = words.textContent.split(' ').map(w => `<span class="w">${w}</span>`).join(' ');
    wordEls = [...words.querySelectorAll('.w')];
  }

  // --- tableau des départs : palettes
  const CHARS = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-';
  document.querySelectorAll('.flap').forEach(f => {
    f.innerHTML = [...f.dataset.text].map(c => `<span class="c${c === ' ' ? ' sp' : ''}" data-c="${c}">${c === ' ' ? '' : ' '}</span>`).join('');
  });
  const runFlaps = row => row.querySelectorAll('.flap .c:not(.sp)').forEach((c, i) => {
    const target = c.dataset.c;
    if (reduce) { c.textContent = target; return; }
    let n = 6 + i * 2 + Math.floor(Math.random() * 6);
    const step = () => {
      if (n-- <= 0) { c.textContent = target; return; }
      c.textContent = CHARS[Math.floor(Math.random() * CHARS.length)];
      c.classList.remove('flip'); void c.offsetWidth; c.classList.add('flip');
      setTimeout(step, 55);
    };
    setTimeout(step, i * 25);
  });

  // --- compteurs
  const count = el => {
    const to = +el.dataset.count, t0 = performance.now(), dur = reduce ? 0 : 1600;
    const f = now => {
      const p = dur ? clamp((now - t0) / dur) : 1;
      el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(f);
    };
    requestAnimationFrame(f);
  };

  // --- révélations
  const io = new IntersectionObserver(entries => entries.forEach(en => {
    if (!en.isIntersecting) return;
    const el = en.target;
    el.classList.add('in');
    if (el.classList.contains('board-row')) runFlaps(el);
    el.querySelectorAll('[data-count]').forEach(count);
    if (el.dataset.count) count(el);
    io.unobserve(el);
  }), { threshold: .25 });
  document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));

  // --- scroll latéral (parcours)
  const hs = document.querySelector('.hscroll');
  const track = hs && hs.querySelector('.track');
  const ghost = hs && hs.querySelector('.hscroll-ghost');
  const bar = hs && hs.querySelector('.hscroll-progress i');
  let dist = 0;
  const size = () => {
    if (!hs) return;
    dist = Math.max(0, track.scrollWidth - innerWidth);
    hs.style.height = (dist + innerHeight) + 'px';
  };

  const onScroll = () => {
    if (hs) {
      const r = hs.getBoundingClientRect();
      const p = clamp(-r.top / Math.max(1, dist));
      track.style.transform = `translate3d(${-p * dist}px,0,0)`;
      ghost.style.transform = `translate3d(${-p * dist * .45}px,0,0)`;
      bar.style.transform = `scaleX(${p})`;
    }
    if (wordEls.length) {
      const r = words.getBoundingClientRect();
      const p = clamp((innerHeight * .85 - r.top) / (r.height + innerHeight * .35));
      const lit = Math.round(p * wordEls.length);
      wordEls.forEach((w, i) => w.classList.toggle('on', i < lit));
    }
  };
  let raf = 0;
  addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; onScroll(); }); }, { passive: true });
  addEventListener('resize', () => { size(); onScroll(); });
  addEventListener('load', () => { size(); onScroll(); });
  size(); onScroll();

  // --- inclinaison 3D (carte, CV) + curseur — souris uniquement
  if (matchMedia('(pointer: fine)').matches && !reduce) {
    document.querySelectorAll('[data-tilt]').forEach(el => {
      const base = el.classList.contains('sheet') ? 'rotate(2deg)' : '';
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        const k = el.classList.contains('sheet') ? 12 : 4;
        el.style.transform = `rotateY(${x * k}deg) rotateX(${-y * k}deg)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = base; });
    });

    const cur = document.querySelector('.cursor');
    let cx = 0, cy = 0, tx = 0, ty = 0;
    addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; cur.classList.add('on'); });
    document.addEventListener('mouseleave', () => cur.classList.remove('on'));
    document.addEventListener('mouseover', e => cur.classList.toggle('big', !!e.target.closest('a, button, .ticket')));
    const loop = () => { cx += (tx - cx) * .2; cy += (ty - cy) * .2; cur.style.transform = `translate(${cx}px,${cy}px)`; requestAnimationFrame(loop); };
    loop();
  }
})();
