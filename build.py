#!/usr/bin/env python3
"""Génère le portfolio de César Mateu : /fr /en /es + CV (HTML → PDF + aperçu PNG via Chrome headless).

Usage : python3 build.py          (site + CV)
        python3 build.py --no-cv  (site seul, plus rapide)
"""
import html
import subprocess
import sys
from pathlib import Path

from content import ADDRESS, EDUCATION, EMAIL, EXPERIENCES, LANGS, LINKEDIN, NAME, PHONE, T, WALL

ROOT = Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = "https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700&display=swap"

e = html.escape

# Icônes au trait (24×24) pour les briques du mur
ICONS = {
    "plate": '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3.5"/>',
    "run": '<path d="M5 12h11M12 7l5 5-5 5"/><path d="M3 8h4M3 16h4"/>',
    "roof": '<path d="M3 11l9-6 9 6"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/>',
    "glass": '<path d="M6 4h12l-6 8z"/><path d="M12 12v7M8 20h8"/>',
    "wave": '<path d="M3 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M3 18c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><circle cx="16" cy="7" r="2.5"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17"/>',
    "spark": '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"/>',
    "chat": '<path d="M4 5h16v10H9l-5 4z"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
    "key": '<circle cx="8" cy="8" r="4.5"/><path d="M11.2 11.2 20 20M16 16l2.2-2.2M18.2 18.2l2-2"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.8-4.5 4.2 1.1 6.1L12 16.8 6.6 19.7l1.1-6.1L3.2 9.4l6.1-.8z"/>',
    "bell": '<path d="M4 17h16M5 17a7 7 0 0114 0"/><path d="M12 8V6M10 6h4"/><path d="M3 20h18"/>',
    "tray": '<path d="M3 15h18M5 15a7 7 0 0114 0"/><path d="M12 8V7"/><path d="M8 19h8"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'
DOWN = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M8 2v10M4 8l4 4 4-4M3 14h10"/></svg>'
MOON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z"/></svg>'


def pdf_name(lang):
    return f"Cesar-Mateu-CV-{lang.upper()}.pdf"


def letters(word, start):
    return "".join(f'<span class="l" style="--i:{start + i}">{e(c)}</span>' for i, c in enumerate(word))


# ---------------------------------------------------------------- site

def page(lang):
    t = T[lang]
    cv_href = f"../cv/{pdf_name(lang)}"
    cur = ' aria-current="true"'
    langs = "".join(f'<a href="../{l}/" hreflang="{l}"{cur if l == lang else ""}>{l.upper()}</a>' for l in LANGS)
    nav = "".join(f'<a href="#{i}">{e(l)}</a>' for i, l in zip(["parcours", "experiences", "formation", "contact"], t["nav"]))

    # mur
    total = sum(len(r) for r in WALL)
    rows, n = [], 0
    for li, row in enumerate(WALL):
        bricks = []
        for label, ic in row:
            bricks.append(f'<span class="brick" data-n="{n}">{icon(ic)}<span>{e(label)}</span></span>')
            n += 1
        rows.append(f'<div class="wall-row" data-layer="{li}">{"".join(bricks)}</div>')
    intro = t["wall_intro"]
    layer_cards = [f'<div class="wall-card is-on" data-card="-1"><p class="eyebrow-sm">{e(intro[0])}</p><h3>{e(intro[1])}</h3><p>{e(intro[2])}</p></div>']
    layer_cards += [f'<div class="wall-card" data-card="{i}"><p class="eyebrow-sm">{e(a)}</p><h3>{e(b)}</h3><p>{e(c)}</p></div>'
                    for i, (a, b, c) in enumerate(t["wall_layers"])]

    z = t["zuma"]
    zuma_roles = "".join(f'<li style="--k:{i}"><span class="role-n">{i + 1}</span><div><strong>{e(a)}</strong><small>{e(b)}</small></div></li>'
                         for i, (a, b) in enumerate(z["roles"]))
    pn = t["pines"]
    pines_bullets = "".join(f"<li>{e(b)}</li>" for b in pn["bullets"])

    ny_steps = "".join(f'<div class="ny-step" data-step="{i}"><p class="big-n">{e(a)}</p><h3>{e(b)}</h3><p>{e(c)}</p></div>'
                       for i, (a, b, c) in enumerate(t["ny"]))
    flyers = "".join(f'<div class="flyer f{i}"><span class="flyer-k">NYC · 2022</span><strong>{e(c)}</strong><span class="flyer-d">Sat · 11PM</span></div>'
                     for i, c in enumerate(["Le Noir", "PHD", "Nebula", "Marquis"]))

    a4 = t["all4"]
    a4_tags = "".join(f'<span class="tag">{e(x)}</span>' for x in a4["tags"])
    a4_steps = "".join(f'<li><span class="step-n">{i + 1}</span><strong>{e(a)}</strong><small>{e(b)}</small></li>'
                       for i, (a, b) in enumerate(a4["steps"]))

    edu = "".join(f"""
      <article class="card edu" data-reveal>
        <div class="edu-head">
          <div><h3>{e(x['school'])}</h3><p class="edu-prog">{e(x['prog'][lang])}</p></div>
          <span class="tag{' tag-live' if x.get('now') else ''}">{e(t['edu_now']) if x.get('now') else e(x['years'][lang])}</span>
        </div>
        <p>{e(x['desc'][lang])}</p>
        <div class="edu-foot"><span class="edu-years">{e(x['years'][lang])}</span><span class="tags">{''.join(f'<span class="tag">{e(g)}</span>' for g in x['tags'][lang])}</span></div>
      </article>""" for x in EDUCATION)

    off_stats = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in t["off_stats"])
    cv_langs = "".join(f'<a class="btn btn-quiet btn-sm" href="../cv/{pdf_name(l)}" download>{l.upper()}</a>' for l in LANGS)
    linkedin = f'<a class="btn btn-quiet" href="{e(LINKEDIN)}" target="_blank" rel="noopener noreferrer">LinkedIn</a>' if LINKEDIN else ""
    user, domain = EMAIL.split("@")
    alternates = "".join(f'<link rel="alternate" hreflang="{l}" href="../{l}/">' for l in LANGS)

    return f"""<!doctype html>
<html lang="{t['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['meta'])}">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['meta'])}">
{alternates}
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<script>try{{var s=localStorage.getItem('cm-theme');if(s)document.documentElement.dataset.theme=s;}}catch(_){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>

<header class="nav-wrap">
  <nav class="nav-pill" aria-label="Navigation">
    <a class="nav-name" href="#top">{e(NAME)}</a>
    <span class="nav-links">{nav}</span>
    <button class="btn-cv" type="button" data-open-cv>CV</button>
    <span class="seg">{langs}</span>
    <button class="theme" type="button" aria-label="{e(t['theme'])}">{MOON}</button>
  </nav>
</header>

<main id="main">
<section class="hero" id="top">
  <div class="hero-light" aria-hidden="true"></div>
  <div class="hero-top">
    <p class="hero-label">{e(t['hero_role'])}</p>
    <p class="hero-label">{e(t['hero_place'])}</p>
  </div>
  <div class="hero-mid">
    <h1 class="hero-name"><span class="n1">{letters("César", 0)}</span><span class="n2">{letters("Mateu", 5)}</span></h1>
    <button class="bell" type="button" aria-label="{e(t['bell'])}">
      <svg viewBox="0 0 200 150" fill="none" aria-hidden="true">
        <defs><linearGradient id="bg1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6e2b8"/><stop offset=".45" stop-color="#c99b55"/><stop offset="1" stop-color="#6b4a1e"/></linearGradient>
        <linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3530"/><stop offset="1" stop-color="#15130f"/></linearGradient></defs>
        <g class="bell-top"><rect x="95" y="16" width="10" height="16" rx="3" fill="url(#bg1)"/><rect x="88" y="10" width="24" height="8" rx="4" fill="url(#bg1)"/>
        <path d="M30 110 A70 70 0 0 1 170 110 Z" fill="url(#bg1)"/><path d="M48 92 A55 55 0 0 1 92 46" stroke="#fff6dd" stroke-opacity=".55" stroke-width="4" stroke-linecap="round"/></g>
        <rect x="18" y="108" width="164" height="14" rx="7" fill="url(#bg2)"/><rect x="26" y="122" width="148" height="12" rx="4" fill="#0e0c0a"/>
      </svg>
      <span class="bell-hint">{e(t['bell'])}</span>
      <span class="ding" aria-hidden="true">ding!</span>
    </button>
  </div>
  <div class="hero-bottom">
    <p class="hero-bio">{e(t['hero_bio'])}</p>
    <div class="hero-ctas">
      <a class="btn btn-light" href="#parcours">{e(t['cta1'])} {ARROW}</a>
      <a class="btn btn-outline" href="#contact">{e(t['cta2'])}</a>
    </div>
  </div>
  <a class="scroll-cue" href="#parcours">{e(t['scroll'])}<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 6l4 4 4-4"/></svg></a>
</section>

<section class="wall-sec" id="parcours" style="--total:{total}">
  <div class="wall-pin">
    <div class="wrap">
      <div class="sec-head">
        <div><p class="eyebrow">{e(t['wall_eyebrow'])}</p><h2>{e(t['wall_h'])}</h2></div>
        <p class="counter"><b data-wall-count>00</b> / {total:02d}</p>
      </div>
      <div class="wall-grid">
        <div class="wall-side">
          <div class="wall-cards card">{''.join(layer_cards)}</div>
          <div class="dots"><i class="on"></i><i></i><i></i><i></i></div>
        </div>
        <div class="wall">{''.join(reversed(rows))}<div class="wall-floor"></div></div>
      </div>
      <p class="caption">{e(t['wall_caption'])}</p>
    </div>
  </div>
</section>

<section class="sec" id="experiences">
  <div class="wrap">
    <p class="eyebrow" data-reveal>{e(t['exp_eyebrow'])}</p>
    <h2 class="h2-lg" data-reveal>{e(t['exp_h'])}</h2>

    <article class="dark-card zuma" data-reveal>
      <div class="zuma-copy">
        <p class="chip-live"><i></i>{e(z['chip'])}</p>
        <h3>{e(z['h'])}</h3>
        <p>{e(z['p'])}</p>
        <p class="zuma-name">Zuma Ibiza <span>· {e(z['tag'])}</span></p>
      </div>
      <ol class="roles">{zuma_roles}</ol>
    </article>

    <article class="card split pines" data-reveal>
      <div class="split-copy">
        <p class="eyebrow-sm">{e(pn['eyebrow'])}</p>
        <h3>{e(pn['h'])}</h3>
        <p>{e(pn['p'])}</p>
        <ul class="bullets">{pines_bullets}</ul>
      </div>
      <div class="pines-visual" data-tilt>
        <div class="keycard">
          <div class="keycard-top"><span class="keycard-logo">7PINES</span><span>RESORT · IBIZA</span></div>
          <div class="keycard-chip"></div>
          <div class="keycard-bottom"><span>{e(pn['card'])}</span><b>2025</b></div>
        </div>
        <div class="luggage"><span>IBZ</span><small>César M.</small></div>
      </div>
    </article>
  </div>

  <div class="ny" data-ny>
    <div class="ny-pin">
      <div class="wrap ny-grid">
        <div class="ny-copy"><p class="eyebrow">{e(t['ny_eyebrow'])}</p><div class="ny-steps">{ny_steps}</div></div>
        <div class="flyers" aria-hidden="true">{flyers}</div>
      </div>
    </div>
  </div>

  <div class="wrap">
    <article class="card proj" data-reveal>
      <div class="proj-head">
        <div><h3>{e(a4['h'])}</h3><p class="proj-sub">{e(a4['sub'])}</p></div>
        <span class="tags">{a4_tags}</span>
      </div>
      <p class="proj-p">{e(a4['p'])}</p>
      <div class="proj-steps"><p class="steps-h">{e(a4['steps_h'])}</p><ol>{a4_steps}</ol></div>
    </article>
  </div>
</section>

<section class="sec" id="formation">
  <div class="wrap">
    <p class="eyebrow" data-reveal>{e(t['edu_eyebrow'])}</p>
    <h2 class="h2-lg" data-reveal>{e(t['edu_h'])}</h2>
    <div class="edu-grid">{edu}</div>
  </div>
</section>

<section class="sec statement">
  <div class="wrap statement-grid">
    <div>
      <h2 class="h-xl" data-reveal>{e(t['off_h'])} <span class="u">{e(t['off_h2'])}<svg viewBox="0 0 300 20" preserveAspectRatio="none" aria-hidden="true"><path d="M4 14 C 80 4, 200 4, 296 10"/></svg></span></h2>
      <p class="statement-p" data-reveal>{e(t['off_p'])}</p>
    </div>
    <ul class="off-stats" data-reveal>{off_stats}</ul>
  </div>
</section>

<section class="sec" id="cv">
  <div class="wrap">
    <div class="card cv-card" data-reveal>
      <div class="cv-copy">
        <p class="eyebrow">{e(t['cv_eyebrow'])}</p>
        <h2>{e(t['cv_h'])}</h2>
        <p>{e(t['cv_p'])}</p>
        <div class="row">
          <a class="btn btn-primary" href="{cv_href}" download>{DOWN} {e(t['cv_dl'])}</a>
          <button class="btn btn-quiet" type="button" data-open-cv>{e(t['cv_view'])}</button>
        </div>
        <div class="row cv-langs">{cv_langs}</div>
      </div>
      <button class="sheet" type="button" data-open-cv aria-label="{e(t['cv_view'])}">
        <img src="../cv/preview-{lang}.png" alt="CV — {e(NAME)}" width="794" height="1123" loading="lazy">
      </button>
    </div>
  </div>
</section>

<footer class="site-footer" id="contact">
  <div class="wrap">
    <p class="eyebrow">{e(t['contact_eyebrow'])}</p>
    <h2>{e(t['contact_h'])}</h2>
    <p class="footer-p">{e(t['contact_p'])}</p>
    <div class="row">
      <a class="btn btn-primary" href="{cv_href}" download>{DOWN} {e(t['cv_dl']).upper()}</a>
      <a class="btn btn-quiet mail" data-u="{e(user)}" data-d="{e(domain)}" href="#">…</a>
      {linkedin}
    </div>
    <p class="copyright">© 2026 {e(NAME)}. {e(t['footer'])}</p>
  </div>
</footer>
</main>

<dialog class="cv-modal">
  <div class="cv-modal-bar">
    <strong>CV — {e(NAME)}</strong>
    <span class="row"><a class="btn btn-primary btn-sm" href="{cv_href}" download>{DOWN} PDF</a>
    <button class="btn btn-quiet btn-sm" type="button" data-close>{e(t['close'])}</button></span>
  </div>
  <img src="../cv/preview-{lang}.png" alt="CV — {e(NAME)}" width="794" height="1123">
</dialog>
<script src="../assets/main.js"></script>
</body>
</html>
"""


def root_index():
    return """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>César Mateu</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>var l=(navigator.language||'fr').slice(0,2);location.replace((['fr','en','es'].indexOf(l)>-1?l:'en')+'/');</script>
<meta http-equiv="refresh" content="1;url=fr/"></head>
<body style="background:#0b0a08"></body></html>
"""


# ---------------------------------------------------------------- CV

def cv(lang):
    t = T[lang]
    exps = "".join(f"""
      <div class="item">
        <div class="item-when">{e(x['year'])}<small>{e(x['city'])}</small></div>
        <div><h4>{e(x['role'][lang])}</h4><p class="where">{e(x['venue'])}{' — ' + e(x['group']) if x['group'] else ''}</p>
        <p>{e(x['desc'][lang])}</p></div>
      </div>""" for x in EXPERIENCES)
    edus = "".join(f"""
      <div class="item">
        <div class="item-when">{e(x['years'][lang])}</div>
        <div><h4>{e(x['school'])}</h4><p>{e(x['prog'][lang])}</p></div>
      </div>""" for x in EDUCATION)
    langs = "".join(f"<li><b>{e(a)}</b> — {e(b)}</li>" for a, b in t["langs"])
    ints = "".join(f"<li>{e(i)}</li>" for i in t["cv_int"])
    skills = "".join(f"<span>{e(s)}</span>" for s in t["cv_skills"])
    li = f"<li>{e(LINKEDIN.replace('https://', ''))}</li>" if LINKEDIN else ""
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>CV — {e(NAME)}</title>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="cv.css"></head>
<body><div class="page">
  <aside>
    <img class="photo" src="../assets/portrait.jpg" alt="">
    <h3>{e(t['cv_profile_h'])}</h3><p>{e(t['cv_profile'])}</p>
    <h3>{e(t['cv_contact_h'])}</h3>
    <ul><li>{e(EMAIL)}</li><li>{e(PHONE)}</li><li>{e(ADDRESS)}</li>{li}<li>{e(t['licence'])}</li></ul>
    <h3>{e(t['cv_langs_h'])}</h3><ul>{langs}</ul>
    <h3>{e(t['cv_int_h'])}</h3><ul>{ints}</ul>
  </aside>
  <section>
    <header><p class="kicker">{e(t['cv_title'])} · Vatel Madrid</p><h1>{e(NAME)}</h1></header>
    <h2>{e(t['cv_exp_h'])}</h2>{exps}
    <h2>{e(t['cv_edu_h'])}</h2>{edus}
    <h2>{e(t['cv_skills_h'])}</h2><div class="chips">{skills}</div>
  </section>
</div></body></html>
"""


def chrome(*args):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=4000", *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    for lang in LANGS:
        d = ROOT / lang
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(lang), encoding="utf-8")
    (ROOT / "index.html").write_text(root_index(), encoding="utf-8")
    print("site : fr/ en/ es/")

    if "--no-cv" in sys.argv:
        return
    cvdir = ROOT / "cv"
    for lang in LANGS:
        src = cvdir / f"cv-{lang}.html"
        src.write_text(cv(lang), encoding="utf-8")
        chrome("--no-pdf-header-footer", f"--print-to-pdf={cvdir / pdf_name(lang)}", src.as_uri())
        chrome("--window-size=794,1123", "--force-device-scale-factor=2",
               f"--screenshot={cvdir / f'preview-{lang}.png'}", src.as_uri())
        print(f"cv : {pdf_name(lang)} + preview-{lang}.png")


if __name__ == "__main__":
    main()
