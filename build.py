"""
Builds the website into docs/ (the folder GitHub Pages publishes).

    python build.py              content/ + static/  ->  docs/
    python build.py --figures    first refresh static/figdata.js from the paper CSVs, then build

Run it from anywhere; paths are relative to this file. See README.md.
"""
import csv, json, re, shutil, sys
from datetime import date
from pathlib import Path

# ── Settings you may change ─────────────────────────────────────────────
SITE_URL = "https://seongkwon-ham.github.io"
UPDATED = "November 2026"           # shown in the footer of every page
EMAIL = "skham.econ@yonsei.ac.kr"
GOOGLE_VERIFICATION = "K9H4NTLD0AC9T67dCbMoKKtk3IVvNjVkBCpD4-4_uDE"   # Google Search Console > HTML tag (keep it)
NAVER_VERIFICATION = ""             # Naver Search Advisor > HTML tag > content="..." value
# ────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
CONTENT, STATIC, DOCS = ROOT / "content", ROOT / "static", ROOT / "docs"

# page key, URL path, <title>, description, extra scripts
PAGES = [
    ("home", "/", "Seongkwon Ham | Economics, Yonsei University",
     "Seongkwon Ham (함성권), M.A. student in Economics at Yonsei University. Research on carbon pricing, energy, trade, and climate finance.", []),
    ("research", "/research/", "Research | Seongkwon Ham",
     "Working papers by Seongkwon Ham on carbon pricing, trade, and climate finance.", ["/assets/figdata.js"]),
    ("cv", "/cv/", "CV | Seongkwon Ham",
     "Curriculum vitae of Seongkwon Ham, School of Economics, Yonsei University.", []),
    ("contact", "/contact/", "Contact | Seongkwon Ham",
     "How to reach Seongkwon Ham, School of Economics, Yonsei University.", []),
]
NAV = [("home", "Home"), ("research", "Research"), ("cv", "CV"), ("contact", "Contact")]

# Structured data on the home page: tells search engines who the site is about.
PERSON = {
    "@context": "https://schema.org", "@type": "Person",
    "name": "Seongkwon Ham", "alternateName": "함성권", "url": SITE_URL + "/",
    "email": "mailto:" + EMAIL, "jobTitle": "M.A. student in Economics",
    "affiliation": {"@type": "CollegeOrUniversity", "name": "Yonsei University"},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Yonsei University"},
    "knowsAbout": ["Macroeconomics", "Energy economics", "Environmental economics", "Finance", "Carbon pricing"],
    "sameAs": ["https://github.com/seongkwon-Ham"],
}

FRAME = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Seongkwon Ham">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Seongkwon Ham">
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
    <span>&copy; <span id="yr">{year}</span> Seongkwon Ham &middot; 함성권</span>
    <span>Last updated {updated}</span>
  </div>
</footer>
{scripts}<script src="/assets/site.js"></script>
</body>
</html>
"""


# ── Figure data (only with --figures) ───────────────────────────────────
def refresh_figures():
    """Reads the numbers behind the three paper figures from the project folders
    next to this one and writes static/figdata.js.
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


# ── Pages ───────────────────────────────────────────────────────────────
def photo_html():
    """static/photo.jpg (or .jpeg/.png/.webp) if present, otherwise an initials tile."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        if (STATIC / f"photo.{ext}").exists():
            return f'<img src="/assets/photo.{ext}" alt="Seongkwon Ham" width="600" height="750">', f"/assets/photo.{ext}"
    return '<span class="monogram" aria-hidden="true">SH</span>', None


def build():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "assets").mkdir(parents=True)
    for f in STATIC.iterdir():
        if f.is_file():
            shutil.copy2(f, DOCS / "assets" / f.name)

    photo, photo_url = photo_html()
    for key, path, title, desc, scripts in PAGES:
        content = (CONTENT / f"{key}.html").read_text(encoding="utf-8").rstrip()
        content = content.replace("<!-- PHOTO -->", photo)
        content = re.sub(r"[ \t]*<!--.*?-->[ \t]*\n?", "", content, flags=re.S)   # guide notes stay out of the site
        url = SITE_URL + path
        extra = ""
        if photo_url:
            extra += f'<meta property="og:image" content="{SITE_URL}{photo_url}">\n'
        if key == "home":
            if GOOGLE_VERIFICATION:
                extra += f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">\n'
            if NAVER_VERIFICATION:
                extra += f'<meta name="naver-site-verification" content="{NAVER_VERIFICATION}">\n'
            extra += '<script type="application/ld+json">' + json.dumps(PERSON, ensure_ascii=False) + "</script>\n"
        paths = {k: p for k, p, *_ in PAGES}
        current = ' aria-current="page"'
        nav = "\n".join(f'      <a href="{paths[k]}"{current if k == key else ""}>{label}</a>' for k, label in NAV)
        html = FRAME.format(title=title, desc=desc, url=url, extra_head=extra, nav=nav, content=content,
                            year=date.today().year, updated=UPDATED,
                            scripts="".join(f'<script src="{s}"></script>\n' for s in scripts))
        out = DOCS / path.strip("/") / "index.html" if path != "/" else DOCS / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8", newline="\n")
        print(f"page:    docs/{out.relative_to(DOCS).as_posix()}")

    # Search engines: sitemap + robots. GitHub Pages: .nojekyll serves files as they are.
    today = date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n" for _, p, *_ in PAGES)
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "</urlset>\n", encoding="utf-8", newline="\n")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8", newline="\n")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print("search:  docs/sitemap.xml, docs/robots.txt")
    print("photo:  ", "static/" + photo_url.split("/")[-1] if photo_url else "none (initials tile shown)")


if __name__ == "__main__":
    if "--figures" in sys.argv:
        refresh_figures()
    build()
