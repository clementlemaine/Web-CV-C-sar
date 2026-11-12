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

  // --- aperçu mobile : le site dans un cadre de téléphone
  if (window.self !== window.top) doc.classList.add('in-frame');
  const phoneModal = $('.phone-modal');
  if (phoneModal) {
    const frame = $('iframe', phoneModal);
    const fit = () => phoneModal.style.setProperty('--s', Math.min(1, (innerHeight - 48) / 868, (innerWidth - 32) / 414));
    $('[data-phone]').addEventListener('click', () => {
      if (!frame.getAttribute('src')) frame.src = location.pathname;
      fit(); phoneModal.showModal();
    });
    $('[data-phone-close]', phoneModal).addEventListener('click', () => phoneModal.close());
    phoneModal.addEventListener('click', e => { if (e.target === phoneModal) phoneModal.close(); });
    addEventListener('resize', fit);
  }

  // --- QR code plein écran (aussi via l'adresse …/#qr)
  const qrModal = $('.qr-modal');
  $$('[data-open-qr]').forEach(b => b.addEventListener('click', () => qrModal.showModal()));
  $('[data-close]', qrModal).addEventListener('click', () => qrModal.close());
  qrModal.addEventListener('click', e => { if (e.target === qrModal) qrModal.close(); });
  if (location.hash === '#qr') qrModal.showModal();

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

  // --- reflet qui suit la souris sur les cartes
  if (matchMedia('(pointer: fine)').matches) {
    $$('.spot').forEach(el => el.addEventListener('mousemove', e => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
    }));
  }

  // --- New York : les chiffres défilent jusqu'à leur valeur
  const counts = $$('[data-count]');
  if (counts.length && !reduce) {
    counts.forEach(el => { el.textContent = '0'; });
    new IntersectionObserver((es, o) => {
      if (!es[0].isIntersecting) return;
      o.disconnect();
      const t0 = performance.now();
      const tick = now => {
        const k = clamp((now - t0) / 1400);
        const ease = 1 - Math.pow(1 - k, 3);
        counts.forEach(el => { el.textContent = Math.round(+el.dataset.count * ease); });
        if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }, { threshold: .4 }).observe($('.ny-card'));
  }

  // --- scroll : trajet, nav active
  const routeSec = $('.route-sec');
  const line = $('.route-line', routeSec);
  const plane = $('.plane', routeSec);
  const stops = $$('.stop', routeSec);
  const legs = $$('.leg', routeSec);
  const L = line.getTotalLength();
  line.style.strokeDasharray = L;
  // position de chaque escale le long du tracé (0, 1/3, 2/3, 1)
  const at = stops.map((g, i) => {
    const len = L * i / (stops.length - 1);
    const pt = line.getPointAtLength(len);
    g.setAttribute('transform', `translate(${pt.x} ${pt.y})`);
    return len;
  });
  const navLinks = $$('.nav-links a');
  const secs = navLinks.map(a => $(a.getAttribute('href')));
  let lastLeg = -1;

  const progress = el => {
    const r = el.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, el.offsetHeight - innerHeight));
  };

  const onScroll = () => {
    const d = reduce ? L : clamp(progress(routeSec) / .92) * L;
    line.style.strokeDashoffset = L - d;
    const p1 = line.getPointAtLength(Math.max(0, d)), p2 = line.getPointAtLength(Math.min(L, d + 1));
    const ang = Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;
    plane.setAttribute('transform', `translate(${p1.x} ${p1.y}) rotate(${ang})`);
    plane.classList.toggle('done', d >= L - 1);
    let leg = 0;
    at.forEach((len, i) => { if (d >= len - 2) leg = i; });
    stops.forEach((g, i) => { g.classList.toggle('on', d >= at[i] - 2); g.classList.toggle('cur', i === leg); });
    if (leg !== lastLeg) {
      lastLeg = leg;
      legs.forEach((el, i) => el.classList.toggle('is-on', i === leg));
    }

    doc.classList.toggle('past-hero', scrollY > innerHeight * .6);

    let cur = -1;
    secs.forEach((sec, i) => { if (sec && sec.getBoundingClientRect().top < innerHeight * .4) cur = i; });
    navLinks.forEach((a, i) => a.classList.toggle('on', i === cur));
  };
  let raf = 0;
  addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; onScroll(); }); }, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();
})();
