"""
Builds the website into docs/ from the data files in content/.

    python build.py              content/*.yml + static/ + admin/  ->  docs/
    python build.py --figures    first refresh static/figdata.js from the paper CSVs, then build

On GitHub, every push (including every save in /admin) runs this script
automatically (.github/workflows/site.yml) and publishes docs/.
"""
import csv, html, json, re, shutil, sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

# ── Settings ────────────────────────────────────────────────────────────
SITE_URL = "https://seongkwon-ham.github.io"
GOOGLE_VERIFICATION = "K9H4NTLD0AC9T67dCbMoKKtk3IVvNjVkBCpD4-4_uDE"   # Google Search Console (keep it)
NAVER_VERIFICATION = "034875e87df9ba7c2c1ced58bf6424174cdc39b8"       # Naver Search Advisor (keep it)
GITHUB_PROFILE = "https://github.com/seongkwon-Ham"
# ────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
CONTENT, STATIC, ADMIN, DOCS = ROOT / "content", ROOT / "static", ROOT / "admin", ROOT / "docs"


def load(name):
    with open(CONTENT / f"{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ── Text helpers: *italic*, **bold**, [text](url), blank line = new paragraph ──
def inline(s):
    s = html.escape(str(s or "").strip(), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a class="lnk" href="{html.escape(m[2])}">{m[1]}</a>', s)
    return s


def lines(s):
    """Keeps line breaks (addresses, short lists)."""
    return "<br>".join(inline(x) for x in str(s or "").strip().splitlines() if x.strip())


def paragraphs(s, cls=""):
    attr = f' class="{cls}"' if cls else ""
    parts = [p for p in re.split(r"\n\s*\n", str(s or "").strip()) if p.strip()]
    return "\n".join(f"<p{attr}>{inline(' '.join(p.split()))}</p>" for p in parts)


def full_title(p):
    t, sub = p.get("title", ""), p.get("subtitle", "")
    if not sub:
        return t
    return f"{t} {sub}" if t.rstrip().endswith(("?", "!")) else f"{t}: {sub}"


# ── Figures: the drawing code is in static/site.js; this is the frame around it ──
FIGURES = {
    "carbon-costs": dict(
        canvas="f1",
        aria="Line chart. Cumulative response of all-industry production to a 10 percent higher cost of carbon-emitting generation, by nuclear utilization. With high utilization, production is about 0.36 percentage points lower after 7 months. With low utilization, the response is insignificant.",
        legend='<span style="color:var(--accent)"><i class="sw"></i>High utilization</span>\n'
               '<span style="color:var(--ink-2)"><i class="sw"></i>Median</span>\n'
               '<span style="color:var(--ink-3)"><i class="sw dash"></i>Low utilization</span>'),
    "being-green": dict(
        canvas="f2",
        aria="Line chart. Cumulative return of the portfolio that is long carbon-efficient and short carbon-inefficient firms within each sector, July 2009 to December 2024. It reaches about 91 percent for all firms and about 104 percent for large firms.",
        legend='<span style="color:var(--accent)"><i class="sw"></i>EMI1 &middot; all firms</span>\n'
               '<span style="color:var(--ink-2)"><i class="sw dash"></i>EMI3 &middot; large firms</span>'),
    "environmental-bias": dict(
        canvas="f3",
        aria="Event-study chart. Monthly estimates of carbon embodied in Korea's imports of liberalized steel products relative to control products, 2013 to 2024. Estimates are near zero before the agreement entered into force in December 2015 and rise afterwards.",
        legend='<span style="color:var(--accent)"><i class="sw"></i>Estimate</span>\n'
               '<span><i class="sw box"></i>95% CI</span>\n'
               '<span style="color:var(--ink-3)"><i class="sw dash"></i>FTA in force</span>'),
}


# ── Page bodies ─────────────────────────────────────────────────────────
def photo_html(home):
    src = (home.get("photo") or "").strip()
    rel = re.sub(r"^/?(assets|static)/", "", src)          # editor saves /assets/<path under static/>
    if rel and (STATIC / rel).is_file():
        url = "/assets/" + quote(rel)
        return f'<img src="{url}" alt="{html.escape(SITE["name"])}" width="600" height="750">', url
    if src:
        print(f"warning: photo '{src}' not found under static/, showing initials instead")
    for ext in ("jpg", "jpeg", "png", "webp"):
        if (STATIC / f"photo.{ext}").exists():
            return f'<img src="/assets/photo.{ext}" alt="{html.escape(SITE["name"])}" width="600" height="750">', f"/assets/photo.{ext}"
    return '<span class="monogram" aria-hidden="true">SH</span>', None


def page_home(home, research):
    first, *rest = SITE["name"].split(" ", 1) + [""]
    eyebrow = '<span class="dot">/</span>\n        '.join(f"<span>{inline(x)}</span>" for x in home.get("eyebrow", []))
    email = SITE["email"]
    facts = "\n".join(
        f'      <div class="fact"><dt class="m">{inline(f.get("label"))}</dt><dd>{inline(f.get("title"))}'
        + (f'<span>{lines(f.get("detail"))}</span>' if f.get("detail") else "") + "</dd></div>"
        for f in home.get("facts", []))
    idx = "\n".join(
        f'      <a href="/research/#{p["id"]}">\n'
        f'        <span class="idx-t">{inline(full_title(p))}</span>\n'
        f'        <span class="idx-w">{inline(p.get("coauthors"))}</span>\n'
        f'        <span class="idx-arw m" aria-hidden="true">&rarr;</span>\n      </a>'
        for p in research.get("papers", []))
    return f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="m eyebrow ld">
        {eyebrow}
      </p>
      <h1 class="ld d1"><span>{inline(first)}</span><span>{inline(rest[0])}</span></h1>
      <p class="hero-sub ld d2">{inline(home.get("tagline"))}</p>
      <div class="hero-meta m ld d3">
        <a class="lnk" href="mailto:{email}">{email}</a>
        <a class="lnk" href="/research/">Research &rarr;</a>
        <a class="lnk" href="/cv/">CV &rarr;</a>
      </div>
    </div>
    <figure class="portrait ld d4">
      {PHOTO}
    </figure>
  </div>
</section>

<section class="about">
  <div class="wrap about-grid">
    <div class="greeting rv">
{paragraphs(home.get("greeting"))}
    </div>
    <dl class="facts rv">
{facts}
    </dl>
  </div>
</section>

<section class="index">
  <div class="wrap">
    <p class="index-head m rv"><span>Working papers</span><a class="lnk" href="/research/" style="color:var(--ink-2)">All research &rarr;</a></p>
    <div class="idx rv">
{idx}
    </div>
  </div>
</section>"""


def page_research(research):
    papers = research.get("papers", [])
    out = []
    for p in papers:
        tags = f'<span class="tag hi">{inline(p.get("status") or "Working paper")}</span>'
        if p.get("date"):
            tags += f'<span class="tag">{inline(p["date"])}</span>'
        sub = f'<span class="subtitle">{inline(p["subtitle"])}</span>' if p.get("subtitle") else ""
        abstract = ""
        if p.get("abstract"):
            jel = f'\n          <p class="note">JEL {inline(p["jel"])}</p>' if p.get("jel") else ""
            abstract = f"""
        <details>
          <summary>Abstract</summary>
          {paragraphs(p["abstract"], "abs")}{jel}
        </details>"""
        subject = re.sub(r"[^A-Za-z0-9 ?:'-]", "", p.get("title", "")).strip()
        mail = f'mailto:{SITE["email"]}?subject=' + quote("Draft request: " + subject)
        fig = ""
        spec = FIGURES.get(p.get("figure") or "")
        if spec:
            head = "".join(f"<span>{inline(p[k])}</span>" for k in ("figure_title", "figure_range") if p.get(k))
            fig = f"""
      <figure class="pfig">
        <p class="pfig-head m"><b>Fig. {len([q for q in papers[:papers.index(p) + 1] if FIGURES.get(q.get("figure") or "")])}</b>{head}</p>
        <canvas id="{spec['canvas']}" role="img" aria-label="{html.escape(spec['aria'])}"></canvas>
        <p class="legend m">
{spec['legend']}
        </p>
        <p class="note">{inline(' '.join(str(p.get('figure_note', '')).split()))}</p>
      </figure>"""
        out.append(f"""    <article class="paper rv" id="{p['id']}">
      <div>
        <div class="tags m">{tags}</div>
        <h3>{inline(p.get('title'))}{sub}</h3>
        <p class="byline">{inline(p.get('coauthors'))}</p>{abstract}
        <p class="filerow m">
          <span>Draft on request</span>
          <a class="lnk" href="{mail}">Request &#8599;</a>
        </p>
      </div>{fig}
    </article>""")
    return f"""<section class="page-head">
  <div class="wrap">
    <p class="m eyebrow ld"><span>Research</span><span class="dot">/</span><span>{len(papers)} working paper{'s' if len(papers) != 1 else ''}</span></p>
    <h1 class="ld d1">{inline(research.get('title'))}</h1>
    <p class="lede ld d2">{inline(research.get('lede'))}</p>
  </div>
</section>

<section class="page-body">
  <div class="wrap">
{chr(10).join(out)}
  </div>
</section>"""


def tl_row(years, title, detail="", bullets=(), link=""):
    t = inline(title)
    if link:
        t = f'<a class="lnk" href="{link}">{t}</a>'
    d = f'<p class="tl-where">{inline(detail)}</p>' if detail else ""
    b = ("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in bullets) + "</ul>") if bullets else ""
    return f'        <div class="tl-row"><p class="tl-yr m">{inline(years)}</p><div><p class="tl-what">{t}</p>{d}{b}</div></div>'


def page_cv(cv, research):
    groups = []
    for s in cv.get("sections", []):
        if s.get("papers"):
            rows = [tl_row(re.sub(r".*?(\d{4}).*", r"\1", str(p.get("date", ""))) or "", full_title(p),
                           p.get("coauthors", ""), link=f"/research/#{p['id']}") for p in research.get("papers", [])]
        else:
            rows = [tl_row(i.get("years", ""), i.get("title", ""), i.get("detail", ""), i.get("bullets") or [])
                    for i in s.get("items") or []]
        groups.append(f"""    <div class="tl-group rv">
      <span class="m">{inline(s.get('heading'))}</span>
      <div class="tl">
{chr(10).join(rows)}
      </div>
    </div>""")
    chips = "".join(f'<span class="tag">{inline(x)}</span>' for x in cv.get("tools", [])) + \
            "".join(f'<span class="tag hi">{inline(x)}</span>' for x in cv.get("methods", []))
    if chips:
        groups.append(f"""    <div class="tl-group rv">
      <span class="m">Tools and methods</span>
      <div class="chips m">{chips}</div>
    </div>""")
    return f"""<section class="page-head">
  <div class="wrap narrow">
    <p class="m eyebrow ld"><span>CV</span><span class="dot">/</span><span>Updated {inline(SITE.get('updated'))}</span></p>
    <h1 class="ld d1">{inline(cv.get('title'))}</h1>
  </div>
</section>

<section class="page-body">
  <div class="wrap narrow">
{chr(10).join(groups)}
  </div>
</section>"""


def page_contact(contact):
    email = SITE["email"]
    boxes = "\n".join(f'      <div><span class="m">{inline(b.get("label"))}</span><p>{lines(b.get("text"))}</p></div>'
                      for b in contact.get("boxes", []))
    return f"""<section class="page-head">
  <div class="wrap narrow">
    <p class="m eyebrow ld"><span>Contact</span></p>
    <h1 class="ld d1">{inline(contact.get('title'))}</h1>
    <p class="lede ld d2">{inline(contact.get('lede'))}</p>
  </div>
</section>

<section class="page-body">
  <div class="wrap narrow">
    <a class="mailto ld d3" href="mailto:{email}">{email}</a>
    <div class="contact-grid rv">
{boxes}
    </div>
  </div>
</section>"""


# ── Shared frame ────────────────────────────────────────────────────────
FRAME = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{name}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
{extra_head}<meta name="color-scheme" content="light dark">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%231E31A8'/%3E%3Ctext x='16' y='21.5' font-family='Arial,sans-serif' font-size='14' font-weight='700' fill='white' text-anchor='middle'%3ESH%3C/text%3E%3C/svg%3E">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..400&display=swap">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip m" href="#main">Skip to content</a>

<header class="nav" id="nav">
  <div class="nav-in">
    <a class="mark" href="/" aria-label="Home">SH</a>
    <nav class="nav-links m" aria-label="Pages">
{nav}
    </nav>
    <button class="theme-btn" id="themeBtn" type="button" aria-label="Switch color theme">
      <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M8 1.8a6.2 6.2 0 0 1 0 12.4z" fill="currentColor"/></svg>
    </button>
  </div>
</header>

<main id="main">
{content}
</main>

<footer>
  <div class="wrap foot-in m">
    <span>&copy; <span id="yr">{year}</span> {name} &middot; {korean_name}</span>
    <span>Last updated {updated}</span>
  </div>
</footer>
{scripts}<script src="/assets/site.js"></script>
</body>
</html>
"""
NAV = [("home", "/", "Home"), ("research", "/research/", "Research"), ("cv", "/cv/", "CV"), ("contact", "/contact/", "Contact")]


# ── Figure data (only with --figures) ───────────────────────────────────
def refresh_figures():
    """Reads the numbers behind the three paper figures from the project folders next to
    this one and writes static/figdata.js. Runs only on the computer that has those folders.
      Fig. 1  Pf.Jo tracing carbon costs/output/paper_figures/figure_data.csv  (cond_nuc_IP)
      Fig. 2  Pf.In_and_Park/output/20261119/data/f1_cum_emi.csv
      Fig. 3  Pf.Choi/output/261120_figures/data/figure41.csv"""
    res = ROOT.parent

    def rows(p):
        with open(res / p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    w1 = {}
    for r in rows("Pf.Jo tracing carbon costs/output/paper_figures/figure_data.csv"):
        if r["figure"] == "cond_nuc_IP":
            s = w1.setdefault(r["series"], {"h": [], "b": [], "sig": []})
            s["h"].append(int(r["horizon"])); s["b"].append(round(float(r["estimate"]), 4)); s["sig"].append(r["significant"] == "True")
    w2 = {"t": [], "EMI1": [], "EMI3": []}
    for r in rows("Pf.In_and_Park/output/20261119/data/f1_cum_emi.csv"):
        w2["t"].append(r[""]); w2["EMI1"].append(round(float(r["EMI1"]), 4)); w2["EMI3"].append(round(float(r["EMI3"]), 4))
    w3 = {"k": [], "b": [], "lo": [], "hi": []}
    for r in rows("Pf.Choi/output/261120_figures/data/figure41.csv"):
        b, se = float(r["b_M"]), float(r["se_M"])
        w3["k"].append(int(r["k"])); w3["b"].append(round(b, 4))
        w3["lo"].append(round(b - 1.96 * se, 4)); w3["hi"].append(round(b + 1.96 * se, 4))
    (STATIC / "figdata.js").write_text(
        "/* generated by build.py --figures: numbers behind the paper figures */\nwindow.FIGDATA="
        + json.dumps({"w1": w1, "w2": w2, "w3": w3}, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("figures: refreshed static/figdata.js")


# ── Build ───────────────────────────────────────────────────────────────
SITE = {}


def build():
    global SITE, PHOTO
    SITE = load("site")
    home, research, cv, contact = load("home"), load("research"), load("cv"), load("contact")
    PHOTO, photo_url = None, None

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    shutil.copytree(STATIC, DOCS / "assets")          # includes sub-folders made in the editor
    shutil.copytree(ADMIN, DOCS / "admin")

    PHOTO, photo_url = photo_html(home)
    name = SITE["name"]
    pages = [
        ("home", f"{name} | Economics, Yonsei University",
         f"{name} ({SITE.get('korean_name', '')}), M.A. student in Economics at Yonsei University. Research on carbon pricing, energy, trade, and climate finance.",
         page_home(home, research), []),
        ("research", f"Research | {name}", f"Working papers by {name} on carbon pricing, trade, and climate finance.",
         page_research(research), ["/assets/figdata.js"]),
        ("cv", f"CV | {name}", f"Curriculum vitae of {name}, School of Economics, Yonsei University.", page_cv(cv, research), []),
        ("contact", f"Contact | {name}", f"How to reach {name}, School of Economics, Yonsei University.", page_contact(contact), []),
    ]
    person = {
        "@context": "https://schema.org", "@type": "Person", "name": name, "alternateName": SITE.get("korean_name", ""),
        "url": SITE_URL + "/", "email": "mailto:" + SITE["email"], "jobTitle": "M.A. student in Economics",
        "affiliation": {"@type": "CollegeOrUniversity", "name": "Yonsei University"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Yonsei University"},
        "knowsAbout": ["Macroeconomics", "Energy economics", "Environmental economics", "Finance", "Carbon pricing"],
        "sameAs": [GITHUB_PROFILE],
    }
    paths = dict((k, p) for k, p, _ in NAV)
    for key, title, desc, content, scripts in pages:
        url = SITE_URL + paths[key]
        extra = f'<meta property="og:image" content="{SITE_URL}{photo_url}">\n' if photo_url else ""
        if key == "home":
            extra += f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">\n' if GOOGLE_VERIFICATION else ""
            extra += f'<meta name="naver-site-verification" content="{NAVER_VERIFICATION}">\n' if NAVER_VERIFICATION else ""
            extra += '<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False) + "</script>\n"
        current = ' aria-current="page"'
        nav = "\n".join(f'      <a href="{p}"{current if k == key else ""}>{label}</a>' for k, p, label in NAV)
        page = FRAME.format(title=html.escape(title), desc=html.escape(desc), name=html.escape(name), url=url,
                            extra_head=extra, nav=nav, content=content.replace("{PHOTO}", PHOTO),
                            year=date.today().year, korean_name=html.escape(SITE.get("korean_name", "")),
                            updated=inline(SITE.get("updated", "")),
                            scripts="".join(f'<script src="{s}"></script>\n' for s in scripts))
        out = DOCS / "index.html" if key == "home" else DOCS / key / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8", newline="\n")
        print(f"page:    docs/{out.relative_to(DOCS).as_posix()}")

    today = date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n" for _, p, _ in NAV)
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + urls + "</urlset>\n", encoding="utf-8", newline="\n")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE_URL}/sitemap.xml\n",
                                     encoding="utf-8", newline="\n")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("search:  docs/sitemap.xml, docs/robots.txt")
    print("admin:   docs/admin/")
    print("photo:  ", photo_url or "none (initials tile shown)")


if __name__ == "__main__":
    if "--figures" in sys.argv:
        refresh_figures()
    build()
