#!/usr/bin/env python3
"""Génère le portfolio de Cèsar Mateu : /fr /en /es + CV (HTML → PDF + aperçu PNG via Chrome headless).

Usage : python3 build.py          (site + CV)
        python3 build.py --no-cv  (site seul, plus rapide)
"""
import html
import subprocess
import sys
from pathlib import Path

from content import ADDRESS, EDUCATION, EMAIL, EXPERIENCES, LANGS, LINKEDIN, PHONE, T

ROOT = Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600"
         "&family=Manrope:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap")
LANG_NAMES = {"fr": "Français", "en": "English", "es": "Español"}

e = html.escape


def pdf_name(lang):
    return f"Cesar-Mateu-CV-{lang.upper()}.pdf"


def split_letters(word, start):
    return "".join(f'<span class="l" style="--i:{start + i}">{e(c)}</span>' for i, c in enumerate(word))


# ---------------------------------------------------------------- site

def page(lang):
    t = T[lang]
    nav_ids = ["parcours", "formation", "carte", "cv", "contact"]
    nav = "".join(f'<a href="#{i}">{e(l)}</a>' for i, l in zip(nav_ids, t["nav"]))
    cur = ' aria-current="true"'
    langs = "".join(
        f'<a href="../{l}/" hreflang="{l}"{cur if l == lang else ""}>{l.upper()}</a>' for l in LANGS)

    stats = "".join(
        f'<div class="stat" data-reveal><span class="stat-n" data-count="{n}">0</span><span class="stat-l">{e(l)}</span></div>'
        for n, l in t["stats"])

    cards = []
    for i, x in enumerate(EXPERIENCES):
        cards.append(f"""
      <article class="ticket" style="--k:{i}">
        <div class="ticket-stub">
          <span class="ticket-code">{x['code']}</span>
          <span class="ticket-year">{e(x['year'])}</span>
        </div>
        <div class="ticket-body">
          <div class="ticket-top"><span>{e(x['city'])}</span><span class="ticket-tag">{e(x['tag'][lang])}</span></div>
          <h3 class="ticket-venue">{e(x['venue'])}</h3>
          <p class="ticket-role">{e(x['role'][lang])}</p>
          <p class="ticket-desc">{e(x['desc'][lang])}</p>
          <div class="ticket-foot"><span>{e(x['group'])}</span><span class="ticket-no">N° {i + 1:02d}/{len(EXPERIENCES):02d}</span></div>
        </div>
      </article>""")
    cities = " · ".join(["Toulouse", "New York", "Toulouse", "Ibiza", "Ibiza"])

    rows = []
    for x in EDUCATION:
        years = x.get("flap", x["years"])
        status = f'<span class="status now">{e(t["now"])}</span>' if x.get("now") else f'<span class="status">{e(t["done"])}</span>'
        rows.append(f"""
        <div class="board-row" data-reveal>
          <span class="flap" data-text="{e(years)}"></span>
          <span class="flap" data-text="{e(x['dest'])}"></span>
          <span class="board-prog"><strong>{e(x['school'])}</strong>{e(x['prog'][lang])}</span>
          {status}
        </div>""")

    carte_cols = "".join(
        f'<div class="carte-col" data-reveal><h3>{e(h)}</h3><ul>'
        + "".join(f'<li><span>{e(a)}</span><i></i><em>{e(b)}</em></li>' for a, b in items)
        + "</ul></div>" for h, items in t["carte"])
    langs_list = "".join(f'<li><span>{e(a)}</span><i></i><em>{e(b)}</em></li>' for a, b in t["langs"])
    soft = " · ".join(e(s) for s in t["soft"])

    def count(n):
        return f'<span data-count="{n}">0</span>' if n.isdigit() else f"<span>{n}</span>"

    hobbies = "".join(f"""
      <div class="hobby" data-reveal style="--k:{i}">
        <div class="hobby-n">{count(n)}<small>{e(u)}</small></div>
        <h3>{e(h)}</h3><p>{e(d)}</p>
      </div>""" for i, (n, u, h, d) in enumerate(t["hobbies"]))

    other_pdfs = " ".join(f'<a href="../cv/{pdf_name(l)}" download>{l.upper()}</a>' for l in LANGS if l != lang)
    linkedin = (f'<a class="btn btn-ghost" href="{e(LINKEDIN)}" target="_blank" rel="noopener">LinkedIn ↗</a>'
                if LINKEDIN else "")
    user, domain = EMAIL.split("@")
    loader = "".join(f"<span>{e(w)}</span>" for w in t["loader"])
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
<meta name="theme-color" content="#10201b">
{alternates}
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<div class="loader" aria-hidden="true"><div class="loader-words">{loader}</div><div class="loader-line"></div></div>
<div class="cursor" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>

<header class="topbar">
  <a class="mono" href="#top" aria-label="Cèsar Mateu">C<span>M</span></a>
  <nav class="nav">{nav}</nav>
  <div class="topbar-right">
    <a class="cv-pill" href="../cv/{pdf_name(lang)}" download>CV ↓</a>
    <div class="langs">{langs}</div>
  </div>
</header>

<main id="main">
<section class="hero" id="top">
  <div class="hero-meta">
    <span>{e(t['hero_role'])}</span>
    <span class="clock"><b data-clock>--:--</b> {e(t['clock'])}</span>
    <span>{e(t['hero_place'])}</span>
  </div>
  <h1 class="hero-name">
    <span class="row r1">{split_letters("Cèsar", 0)}</span>
    <span class="row r2">{split_letters("Mateu", 5)}</span>
  </h1>
  <div class="badge" aria-hidden="true">
    <svg viewBox="0 0 200 200"><defs><path id="c" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0"/></defs>
      <text><textPath href="#c">{e(t['badge'] * 2)}</textPath></text></svg>
    <span class="badge-key">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="8" cy="8" r="4.5"/><path d="M11.2 11.2 20 20M16 16l2.2-2.2M18.2 18.2l2-2"/></svg>
    </span>
  </div>
  <div class="hero-foot">
    <p class="hero-bio">{e(t['hero_bio'])}</p>
    <div class="hero-ctas">
      <a class="btn" href="#parcours">{e(t['cta1'])} →</a>
      <a class="btn btn-ghost" href="../cv/{pdf_name(lang)}" download>{e(t['cta2'])} ↓</a>
    </div>
  </div>
  <div class="scroll-cue"><span>{e(t['scroll'])}</span><i></i></div>
</section>

<section class="manifesto">
  <p class="eyebrow">{e(t['s1'])}</p>
  <p class="manifesto-text" data-words>{e(t['manifesto'])}</p>
  <div class="stats">{stats}</div>
</section>

<section class="hscroll" id="parcours">
  <div class="hscroll-pin">
    <div class="hscroll-head">
      <p class="eyebrow">{e(t['s2'])}</p>
      <h2>{e(t['h2'])}</h2>
      <p class="hscroll-sub">{e(t['h2_sub'])} <span class="arrow">→</span></p>
    </div>
    <div class="hscroll-ghost" aria-hidden="true">{cities} · {cities}</div>
    <div class="track">{''.join(cards)}
    </div>
    <div class="hscroll-progress"><i></i></div>
  </div>
</section>

<section class="formation" id="formation">
  <p class="eyebrow">{e(t['s3'])}</p>
  <h2>{e(t['h3'])}</h2>
  <div class="board">
    <div class="board-head">
      <span class="board-title">✈ {e(t['board_title'])}</span>
      <span class="board-clock">{e(t['board_live'])} <b data-clock>--:--</b></span>
    </div>
    <div class="board-row board-cols">{''.join(f'<span>{e(c)}</span>' for c in t['board_cols'])}</div>
    {''.join(rows)}
  </div>
</section>

<section class="carte-wrap" id="carte">
  <p class="eyebrow">{e(t['s4'])}</p>
  <div class="carte" data-tilt>
    <div class="carte-inner">
      <p class="carte-house">Maison Mateu · Est. 2019</p>
      <h2>{e(t['h4'])}</h2>
      <p class="carte-sub">{e(t['carte_sub'])}</p>
      <div class="carte-grid">{carte_cols}</div>
      <div class="carte-bottom">
        <div class="carte-col" data-reveal><h3>{e(t['langs_title'])}</h3><ul>{langs_list}</ul></div>
        <div class="carte-chef" data-reveal>
          <p class="chef-label">{e(t['chef'])}</p>
          <p class="chef-list">{soft}</p>
          <p class="chef-licence">{e(t['licence'])}</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="hobbies-wrap">
  <p class="eyebrow">{e(t['s5'])}</p>
  <h2>{e(t['h5'])}</h2>
  <div class="hobbies">{hobbies}</div>
</section>

<section class="cvsec" id="cv">
  <div class="cv-copy">
    <p class="eyebrow">{e(t['s6'])}</p>
    <h2>{e(t['h6'])}</h2>
    <p>{e(t['cv_text'])}</p>
    <div class="cv-actions">
      <a class="btn" href="../cv/{pdf_name(lang)}" download>{e(t['cv_dl'])} ↓</a>
      <span class="cv-other">{e(t['cv_other'])} : {other_pdfs}</span>
    </div>
    <p class="cv-updated">{e(t['cv_updated'])}</p>
  </div>
  <a class="sheet" href="../cv/{pdf_name(lang)}" target="_blank" rel="noopener" data-tilt>
    <img src="../cv/preview-{lang}.png" alt="CV — Cèsar Mateu" width="794" height="1123" loading="lazy">
    <span class="sheet-shine"></span>
  </a>
</section>

<section class="contact" id="contact">
  <p class="eyebrow">{e(t['s7'])}</p>
  <h2 class="contact-title">{e(t['h7'])}</h2>
  <p class="contact-text">{e(t['contact_text'])}</p>
  <div class="contact-mail">
    <a class="mail" data-u="{e(user)}" data-d="{e(domain)}" href="#">…</a>
    <button class="copy" type="button" data-copied="{e(t['copied'])}">{e(t['copy'])}</button>
  </div>
  <div class="contact-links">{linkedin}<a class="btn btn-ghost" href="../cv/{pdf_name(lang)}" download>CV ↓</a></div>
</section>
</main>

<footer class="footer">
  <span>© 2026 Cèsar Mateu. {e(t['footer'])}</span>
  <span>Madrid · Ibiza · Toulouse · New York</span>
</footer>
<div class="toast" role="status" aria-live="polite"></div>
<script src="../assets/main.js"></script>
</body>
</html>
"""


def root_index():
    return """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Cèsar Mateu</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
var l=(navigator.language||'fr').slice(0,2);location.replace((['fr','en','es'].indexOf(l)>-1?l:'en')+'/');
</script>
<meta http-equiv="refresh" content="1;url=fr/"></head>
<body style="background:#10201b"></body></html>
"""


# ---------------------------------------------------------------- CV

def cv(lang):
    t = T[lang]
    exps = "".join(f"""
      <div class="item">
        <div class="item-when">{e(x['year'])}<small>{e(x['city'])}</small></div>
        <div><h4>{e(x['role'][lang])}</h4><p class="where">{e(x['venue'])}{' — ' + e(x['group']) if x['group'].startswith('Groupe') else ''}</p>
        <p>{e(x['desc'][lang])}</p></div>
      </div>""" for x in reversed(EXPERIENCES))
    edus = "".join(f"""
      <div class="item">
        <div class="item-when">{e(x['years'])}{e(t['cv_now']) if x.get('now') else ''}</div>
        <div><h4>{e(x['school'])}</h4><p>{e(x['prog'][lang])}</p></div>
      </div>""" for x in EDUCATION)
    langs = "".join(f"<li><b>{e(a)}</b> — {e(b)}</li>" for a, b in t["langs"])
    ints = "".join(f"<li>{e(i)}</li>" for i in t["cv_int"])
    skills = "".join(f"<span>{e(s)}</span>" for s in t["cv_skills"])
    li = f"<li>{e(LINKEDIN.replace('https://', ''))}</li>" if LINKEDIN else ""
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>CV — Cèsar Mateu</title>
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
    <header><p class="kicker">{e(t['cv_title'])} · Vatel Madrid</p><h1>Cèsar <em>Mateu</em></h1></header>
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
