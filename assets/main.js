(() => {
  const doc = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  requestAnimationFrame(() => setTimeout(() => {
    doc.classList.add('ready');
    $('.nav-wrap').classList.add('show');
  }, 80));

  // --- thème clair / sombre
  $('.theme').addEventListener('click', () => {
    const dark = doc.dataset.theme !== 'dark';
    doc.dataset.theme = dark ? 'dark' : 'light';
    try { localStorage.setItem('cm-theme', doc.dataset.theme); } catch (_) {}
  });

  // --- email assemblé côté client
  const mail = $('.mail');
  if (mail) { const a = mail.dataset.u + '@' + mail.dataset.d; mail.textContent = a; mail.href = 'mailto:' + a; }

  // --- aperçu du CV
  const modal = $('.cv-modal');
  $$('[data-open-cv]').forEach(b => b.addEventListener('click', () => modal.showModal()));
  $('[data-close]', modal).addEventListener('click', () => modal.close());
  modal.addEventListener('click', e => { if (e.target === modal) modal.close(); });

  // --- sonnette de réception
  let actx;
  const bell = $('.bell');
  bell.addEventListener('click', () => {
    bell.classList.remove('ring'); void bell.offsetWidth; bell.classList.add('ring');
    try {
      actx = actx || new (window.AudioContext || window.webkitAudioContext)();
      const t = actx.currentTime;
      [[2093, .35], [2637, .18], [4186, .08]].forEach(([f, g]) => {
        const o = actx.createOscillator(), v = actx.createGain();
        o.type = 'sine'; o.frequency.value = f;
        v.gain.setValueAtTime(0, t); v.gain.linearRampToValueAtTime(g, t + .005); v.gain.exponentialRampToValueAtTime(.0001, t + 1.6);
        o.connect(v).connect(actx.destination); o.start(t); o.stop(t + 1.7);
      });
    } catch (_) {}
  });

  // --- apparitions
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
  }), { threshold: .2 });
  $$('[data-reveal]').forEach(el => io.observe(el));

  // --- Zuma : les rôles s'enchaînent
  const roles = $$('.roles li');
  let roleTimer;
  const playRoles = () => {
    let i = 0;
    roles.forEach(r => r.classList.remove('on', 'cur'));
    clearInterval(roleTimer);
    const step = () => {
      roles.forEach((r, k) => { r.classList.toggle('on', k <= i); r.classList.toggle('cur', k === i); });
      if (++i >= roles.length) { clearInterval(roleTimer); setTimeout(playRoles, 3200); }
    };
    step(); roleTimer = setInterval(step, 1100);
  };
  if (roles.length) {
    if (reduce) roles.forEach(r => r.classList.add('on'));
    else new IntersectionObserver((es, o) => { if (es[0].isIntersecting) { playRoles(); o.disconnect(); } }, { threshold: .4 }).observe($('.zuma'));
  }

  // --- 7Pines : inclinaison
  if (matchMedia('(pointer: fine)').matches && !reduce) {
    $$('[data-tilt]').forEach(el => {
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = `perspective(900px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  // --- scroll : mur, New York, nav active
  const wallSec = $('.wall-sec');
  const bricks = $$('.brick').sort((a, b) => a.dataset.n - b.dataset.n);
  const layerOf = bricks.map(b => +b.closest('.wall-row').dataset.layer);
  const count = $('[data-wall-count]');
  const cards = $$('.wall-card');
  const dots = $$('.dots i');
  const ny = $('[data-ny]');
  const nySteps = $$('.ny-step');
  const navLinks = $$('.nav-links a');
  const secs = navLinks.map(a => $(a.getAttribute('href')));
  let lastN = -1, lastStep = -1;

  const progress = el => {
    const r = el.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, el.offsetHeight - innerHeight));
  };

  const onScroll = () => {
    const p = progress(wallSec);
    const n = reduce ? bricks.length : Math.round(clamp(p / .9) * bricks.length);
    if (n !== lastN) {
      lastN = n;
      bricks.forEach((b, i) => b.classList.toggle('on', i < n));
      count.textContent = String(n).padStart(2, '0');
      const layer = n === 0 ? -1 : layerOf[n - 1];
      cards.forEach(c => c.classList.toggle('is-on', +c.dataset.card === layer));
      dots.forEach((d, i) => d.classList.toggle('on', i === layer + 1));
    }

    const s = Math.min(nySteps.length - 1, Math.floor(progress(ny) * nySteps.length));
    if (s !== lastStep) {
      lastStep = s; ny.dataset.step = s;
      nySteps.forEach((el, i) => el.classList.toggle('on', i === s));
    }

    let cur = -1;
    secs.forEach((sec, i) => { if (sec && sec.getBoundingClientRect().top < innerHeight * .4) cur = i; });
    navLinks.forEach((a, i) => a.classList.toggle('on', i === cur));
  };
  let raf = 0;
  addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; onScroll(); }); }, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();
})();
