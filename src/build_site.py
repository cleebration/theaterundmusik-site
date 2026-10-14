#!/usr/bin/env python3
"""theaterundmusik.at – statische Seite für Vercel.

Termine, Blog und Fotos kommen zur Laufzeit aus den cleebration-Hubs
(Events-, Blog-, Galerie-Hub, je `sites: theaterundmusik`). Diese Datei baut
nur den Rahmen: Seiten, Produktionsseiten aus src/site.json, Weiterleitungen.

Aufruf:  python3 src/build_site.py <Medienordner> <Zielordner>
         Medienordner = entpacktes theaterundmusik-medien.zip (img/, video/, docs/)
         Zielordner wird neu angelegt; danach public/ und vercel.json ins Repo kopieren.
"""
import sys, os, shutil, json, html
from urllib.parse import quote
from PIL import Image, ImageOps

MEDIA, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(OUT, "public")
S = json.load(open(os.path.join(HERE, "site.json"), encoding="utf-8"))
SITE, MAIL, F = S["siteUrl"], S["mail"], S["feeds"]
PROD = {p["key"]: p for p in S["productions"]}
CUR = PROD[S["current"]]
PAST = [p for p in S["productions"] if p["key"] != S["current"]]
E = html.escape
LOGO = "1ad5fa_a2e0afd8fe1f49c795180a599518f11d"

# ---------------------------------------------------------------- Bilder (nur die der Seite selbst)
# Personenfotos der Besetzung liegen im Repo (public/img/personen, gepflegt in der Redaktion).
SITE_IMAGES = [LOGO, "1ad5fa_5a9a3458da824997b96f21fc11e09913"]
for p in S["productions"]:
    SITE_IMAGES += [p[k] for k in ("poster", "videoPoster", "cover") if p.get(k)]
SIZES = {}

def build_images():
    os.makedirs(os.path.join(PUB, "img", "t"), exist_ok=True)
    for base in dict.fromkeys(SITE_IMAGES):
        srcp = next(os.path.join(MEDIA, "img", base + e) for e in (".png", ".jpg") if os.path.exists(os.path.join(MEDIA, "img", base + e)))
        im = ImageOps.exif_transpose(Image.open(srcp))
        if srcp.endswith(".png"):
            im = im.convert("RGBA")
            for w, sub in ((1600, ""), (640, "t/")):
                c = im.copy(); c.thumbnail((w, w * 2)); c.save(os.path.join(PUB, "img", sub + base + ".png"), optimize=True)
            SIZES[base] = (im.width, im.height, "png"); continue
        im = im.convert("RGB")
        for w, q, sub in ((1600, 80, ""), (640, 74, "t/")):
            c = im.copy(); c.thumbnail((w, w * 2)); c.save(os.path.join(PUB, "img", sub + base + ".jpg"), quality=q, optimize=True, progressive=True)
        SIZES[base] = (im.width, im.height, "jpg")

def src(b, thumb=False):
    return f"/img/{'t/' if thumb else ''}{b}.{SIZES[b][2]}"

def wh(b, maxw):
    w, h, _ = SIZES[b]; s = min(1, maxw / w); return int(w * s), int(h * s)

def img(b, alt, thumb=False, cls="", lazy=True):
    w, h = wh(b, 640 if thumb else 1600)
    return f'<img src="{src(b, thumb)}" alt="{E(alt)}" width="{w}" height="{h}"{" loading=lazy" if lazy else ""}{f" class={cls}" if cls else ""}>'

# ---------------------------------------------------------------- Rahmen
def nav_items():
    return [("/", "Home"), (f"/produktion/{CUR['key']}", f"{CUR['title']} {CUR['key'][-4:]}"), ("/termine", "Termine"),
            ("/blog", "Blog"), ("/bildergalerie", "Bildergalerie"), ("/archiv", "Archiv"), ("/orchester", "Orchester"), ("/ueber-uns", "Über uns")]

def page(path, title, body, desc, og=None, active=None, scripts=(), noindex=False):
    full = "Theater & Musik – Talenteverein des BG/BRG Stockerau" if path == "/" else f"{title} | Theater & Musik"
    og_img = SITE + (src(og) if og else "/img/og.jpg")
    lis = []
    for href, label in nav_items():
        cur = ' aria-current="page"' if active == href else ""
        if href == "/archiv":
            subs = "".join(f'<li><a href="/produktion/{p["key"]}"{" aria-current=page" if active == "/produktion/" + p["key"] else ""}>{p["key"][-4:]} {E(p["title"])}</a></li>' for p in PAST)
            subs += '<li><a href="/archiv">Alle Produktionen seit 2001</a></li>'
            lis.append(f'<li class="has-sub"><a href="{href}"{cur}>{label}</a><ul class="sub">{subs}</ul></li>')
        else:
            lis.append(f'<li><a href="{href}"{cur}>{E(label)}</a></li>')
    mods = {"evt": "/assets/event-widget.i18n.js", "blog": "/assets/blog-widget.js", "gal": "/assets/gallery-widget.js"}
    script_tags = "".join(f'<script type="module" src="{mods[s]}"></script>\n' for s in scripts)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full)}</title>
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{SITE}{path}">'}
<meta property="og:type" content="website">
<meta property="og:locale" content="de_AT">
<meta property="og:site_name" content="Theater &amp; Musik">
<meta property="og:title" content="{E(full)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{og_img}">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/barlow-condensed-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js" defer></script>
<script type="module" src="/assets/brand/cleebration-credit.js"></script>
{script_tags}</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="head">
  <div class="wrap head__bar">
    <a class="brand" href="/"><img src="/img/logo.png" alt="Musical Oper" width="96" height="96"><span>Talenteverein<br><strong>Theater und Musik</strong></span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menü</button>
    <nav id="nav" aria-label="Hauptnavigation"><ul>{''.join(lis)}</ul></nav>
  </div>
</header>
<main id="inhalt">
{body}
</main>
<footer class="foot">
  <div class="wrap foot__grid">
    <div><img src="/img/logo.png" alt="" width="120" height="120" class="foot__logo"></div>
    <div>Talenteverein Theater und Musik<br>des BG/BRG Stockerau<br>Unter den Linden 16, 2000 Stockerau<br>
      <a href="mailto:{MAIL}">{MAIL}</a></div>
    <div class="foot__links">
      <a href="/impressum">Impressum</a> · <a href="/datenschutz">Datenschutz</a>
      <p class="social"><a href="https://www.instagram.com/musicaloper/" rel="noopener" target="_blank">Instagram</a> · <a href="https://www.facebook.com/people/Musical-Oper-Gymnasium-Stockerau/61576564972435/" rel="noopener" target="_blank">Facebook</a> · <a href="https://www.youtube.com/@MusicalOperBGStockerau/videos" rel="noopener" target="_blank">YouTube</a></p>
      <p class="credit"><cleebration-credit logo="/assets/brand/cleebration-wortmarke.svg" label="Website von"></cleebration-credit></p>
      <p>© 2026 Talenteverein Theater und Musik des BG/BRG Stockerau</p>
    </div>
  </div>
</footer>
</body>
</html>
"""

def write(path, content):
    fn = "index.html" if path == "/" else path.strip("/") + ".html"
    p = os.path.join(PUB, fn); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)

# ---------------------------------------------------------------- Bausteine (Hub-Module)
def events(p=None, show="upcoming", limit=None, abo=False):
    attrs = f'feed="{F["events"]}" detail-url="/termin" show="{show}"'
    if p: attrs += f' from="{p["from"]}" to="{p["to"]}"'
    if limit: attrs += f' limit="{limit}"'
    if abo: attrs += " abo"
    return f"<event-list {attrs}></event-list>"

def blog(tag=None, size=9):
    t = f' tags="{tag}"' if tag else ""
    return f'<blog-list feed="{F["blog"]}" post-url="/post" page-size="{size}" credit="off"{t}></blog-list>'

def gallery(key=None, filt=False, limit=None):
    a = f'feed="{F["gallery"]}"'
    if key: a += f' gallery="{key}"'
    if filt: a += ' filter="on"'
    if limit: a += f' limit="{limit}"'
    return f"<gallery-grid {a}></gallery-grid>"

def prod_header(p):
    dates = f'<span>{E(p["dates"])}</span>' if p.get("dates") else f'<span>Schuljahr {p["season"]}</span>'
    return f'<h1 class="page-title"><small>Produktion {p["key"][-4:]}</small>{E(p["title"])}{dates}</h1>'

def prod_page(p):
    here = p["key"] == S["current"]
    text = "".join(f"<p>{E(x)}</p>" for x in p["text"])
    sig = f'<p class="sig">{E(p["signature"])}</p>' if p.get("signature") else ""
    side = ""
    if p.get("video"):
        side = (f'<video class="video" controls preload="none" playsinline poster="{src(p["videoPoster"])}">'
                f'<source src="{p["video"]}" type="video/mp4">Ihr Browser kann dieses Video nicht abspielen.</video>')
    elif p.get("cover"):
        side = f'<figure class="fig"><a href="{src(p["cover"])}" data-lightbox>{img(p["cover"], p["title"])}</a></figure>'
    poster = ""
    if p.get("poster"):
        poster = (f'<aside class="poster"><a href="{p.get("posterPdf") or src(p["poster"])}">{img(p["poster"], "Plakat " + p["title"], thumb=True)}</a>'
                  f'<p><a href="{p.get("posterPdf") or src(p["poster"])}">Plakat in Vollbild</a></p></aside>')
    venue = f'<p class="venue"><strong>Ort:</strong> {E(p["venue"])}</p>' if p.get("venue") else ""
    quotes = ""
    if p.get("quotes"):
        Q = json.load(open(os.path.join(HERE, p["quotes"]), encoding="utf-8"))
        quotes = '<h2 class="sec">Stimmen</h2><div class="quotes">' + "".join(
            f'<blockquote>{"".join("<p>" + E(x) + "</p>" for x in q["text"])}<footer>{E(q["by"])}</footer></blockquote>' for q in Q) + "</div>"
    body = f"""{prod_header(p)}
<div class="wrap split">
  <div class="prose"><p class="kicker">{E(p.get("subtitle", ""))} · Schuljahr {p["season"]}</p>{text}{sig}{venue}</div>
  <div>{side}{poster}</div>
</div>
<div class="wrap">
  <h2 class="sec" id="termine">Termine</h2>{events(p, show="upcoming" if here else "all", abo=here)}
  <h2 class="sec" id="fotos">Fotos</h2>{gallery(p["gallery"], filt=True)}
  <h2 class="sec" id="blog">Aus dem Blog</h2>{blog(p["key"], 6)}
  {quotes}
  {'' if here else '<p class="back"><a href="/archiv">← Alle Produktionen</a></p>'}
</div>"""
    desc = f'{p["title"]} ({p["season"]}) – {p.get("subtitle", "")}. Produktion des Talentevereins Theater und Musik am BG/BRG Stockerau.'
    og = p.get("poster") or p.get("cover")
    write(f"/produktion/{p['key']}", page(f"/produktion/{p['key']}", f'{p["title"]} {p["key"][-4:]}', body, desc, og=og,
                                          active=f"/produktion/{p['key']}", scripts=("evt", "blog", "gal")))

# ---------------------------------------------------------------- Seiten
def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(PUB)
    build_images()
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(PUB, "assets"))
    os.makedirs(os.path.join(PUB, "media"))
    shutil.copy(os.path.join(MEDIA, "video", "lottchen-trailer-480p.mp4"), os.path.join(PUB, "media", "das-doppelte-lottchen.mp4"))
    shutil.copy(os.path.join(MEDIA, "docs", "plakat-das-doppelte-lottchen.pdf"), os.path.join(PUB, "media", "plakat-das-doppelte-lottchen.pdf"))
    logo = Image.open(os.path.join(MEDIA, "img", LOGO + ".png")).convert("RGBA"); sq = logo.crop(logo.getbbox())
    for n, s in (("favicon.png", 64), ("apple-touch-icon.png", 180)):
        bg = Image.new("RGBA", sq.size, (0, 0, 0, 255)); bg.alpha_composite(sq); bg.convert("RGB").resize((s, s), Image.LANCZOS).save(os.path.join(PUB, n))
    lg = sq.copy(); lg.thumbnail((400, 400)); lg.save(os.path.join(PUB, "img", "logo.png"), optimize=True)  # Logo ohne Rand
    og = Image.new("RGB", (1200, 630), (17, 17, 17)); l = sq.copy(); l.thumbnail((440, 440)); og.paste(l, (380, 95), l)
    og.save(os.path.join(PUB, "img", "og.jpg"), quality=85)

    last = PAST[0]
    # ---- Startseite
    body = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="kicker">Unsere Produktion {CUR["key"][-4:]} · Schuljahr {CUR["season"]}</p>
      <h1>{E(CUR["title"])}</h1>
      <p class="lead">{E(CUR.get("subtitle", ""))}</p>
      {''.join(f"<p>{E(x)}</p>" for x in CUR["text"])}
      <p><a class="btn" href="/produktion/{CUR["key"]}">Zur Produktion</a></p>
    </div>
    <div class="hero__events"><h2>Nächste Termine</h2>{events(limit=3)}</div>
  </div>
</section>
<section class="wrap">
  <h2 class="sec">Neues aus dem Blog</h2>{blog(size=3)}
  <p class="more"><a href="/blog">Alle Beiträge →</a></p>
</section>
<section class="wrap last">
  <div class="last__img"><a href="/produktion/{last["key"]}">{img(last.get("poster") or last.get("cover"), last["title"], thumb=True)}</a></div>
  <div><p class="kicker">Zuletzt auf der Bühne · {last["season"]}</p><h2>{E(last["title"])}</h2>
    <p>{E(last.get("subtitle", ""))}{" · " + E(last["dates"]) if last.get("dates") else ""}</p>
    <p><a class="btn btn--small" href="/produktion/{last["key"]}">Fotos, Video und Berichte</a> <a class="btn btn--ghost" href="/archiv">Alle Produktionen seit 2001</a></p></div>
</section>
<section class="wrap imprint-note">
  <p><strong>Eigentümer und Herausgeber:</strong><br>Talenteverein Theater und Musik des BG/BRG Stockerau<br>Unter den Linden 16, 2000 Stockerau</p>
</section>"""
    write("/", page("/", "Home", body, f"Talenteverein Theater und Musik des BG/BRG Stockerau – Musical Oper: {CUR['title']} {CUR['key'][-4:]}, Archiv aller Produktionen seit 2001, Termine, Blog und Fotos.", active="/", scripts=("evt", "blog")))

    for p in S["productions"]:
        prod_page(p)

    # ---- Termine
    body = f"""<h1 class="page-title">Termine</h1><div class="wrap">
<h2 class="sec">Kommende Termine</h2>{events(show="upcoming", abo=True)}
<h2 class="sec">Vergangene Termine</h2>{events(show="past")}</div>"""
    write("/termine", page("/termine", "Termine", body, "Aufführungstermine des Talentevereins Theater und Musik, BG/BRG Stockerau.", active="/termine", scripts=("evt",)))
    write("/termin", page("/termin", "Termin", f'<div class="wrap detail"><p class="back"><a href="/termine">← Alle Termine</a></p><event-detail feed="{F["events"]}" detail-url="/termin"></event-detail></div>',
                          "Termin des Talentevereins Theater und Musik.", active="/termine", scripts=("evt",), noindex=True))

    # ---- Blog
    body = f'<h1 class="page-title">Blog</h1><div class="wrap">{blog(size=12)}</div>'
    write("/blog", page("/blog", "Blog", body, "Neuigkeiten von Proben und Aufführungen des Talentevereins Theater und Musik.", active="/blog", scripts=("blog",)))
    write("/post", page("/post", "Beitrag", f'<div class="wrap detail"><blog-post feed="{F["blog"]}" back-url="/blog" credit="off"></blog-post></div>',
                        "Beitrag aus dem Blog des Talentevereins Theater und Musik.", active="/blog", scripts=("blog",), noindex=True))

    # ---- Bildergalerie
    secs = "".join(f'<h2 class="sec"><a href="/produktion/{p["key"]}">{E(p["title"])} <span>{p["key"][-4:]}</span></a></h2>{gallery(p["gallery"], filt=True)}' for p in S["productions"])
    write("/bildergalerie", page("/bildergalerie", "Bildergalerie", f'<h1 class="page-title">Bildergalerie</h1><div class="wrap">{secs}</div>',
                                 "Fotos aller Produktionen des Talentevereins Theater und Musik.", active="/bildergalerie", scripts=("gal",)))

    # ---- Archiv
    cards = "".join(f'''<a class="prod-card" href="/produktion/{p["key"]}">{img(p.get("poster") or p.get("cover") or LOGO, p["title"], thumb=True)}
      <span class="prod-card__year">{p["season"]}</span><strong>{E(p["title"])}</strong><span>{E(p.get("subtitle", ""))}</span></a>''' for p in S["productions"])
    rows = "".join(f'<li><span>{e.split(" ", 1)[0]}</span>{E(e.split(" ", 1)[1])}</li>' for e in reversed(S["earlier"]))
    body = f"""<h1 class="page-title">Archiv</h1><div class="wrap">
<p class="lead-dark">Seit 2001 bringt die Musical Oper des BG/BRG Stockerau jedes Schuljahr eine Produktion auf die Bühne.</p>
<div class="prod-cards">{cards}</div>
<h2 class="sec">Frühere Produktionen</h2><ol class="shows" reversed>{rows}</ol></div>"""
    write("/archiv", page("/archiv", "Archiv", body, "Alle Produktionen der Musical Oper am BG/BRG Stockerau seit 2001/2002.", active="/archiv"))

    # ---- Orchester: Personen kommen aus src/data/besetzung.json (Redaktion → Werkzeug „Besetzung“),
    #      eingesetzt von scripts/besetzung.mjs zwischen den Markierungen (bei jedem Vercel-Deploy).
    pers = os.path.join(HERE, "..", "public", "img", "personen")
    if os.path.isdir(pers): shutil.copytree(pers, os.path.join(PUB, "img", "personen"))
    ens = "1ad5fa_5a9a3458da824997b96f21fc11e09913"
    body = f'''<h1 class="page-title">Orchester</h1><div class="wrap">
<figure class="fig fig--wide"><a href="{src(ens)}" data-lightbox>{img(ens, "Ensemble Unter den Linden")}</a><figcaption>Ensemble „Unter den Linden“</figcaption></figure>
<!-- besetzung:start --><!-- besetzung:end --></div>'''
    write("/orchester", page("/orchester", "Orchester", body, "Das Orchester „Unter den Linden“ begleitet die Produktionen des Talentevereins Theater und Musik.", og=ens, active="/orchester"))

    # ---- Über uns
    body = """<h1 class="page-title">Über uns</h1><div class="wrap prose">
  <h2>Unsere Ziele</h2>
  <p>Unser Verein wurde 2016 gegründet und ist nicht auf Gewinn ausgerichtet.<br>
  Darsteller und Techniker sind alle Schülerinnen und Schüler des <a href="https://www.bgstockerau.ac.at/" rel="noopener" target="_blank">BG/BRG Stockerau</a>.</p>
  <ul class="goals">
    <li>Kulturelle Bildung der mitwirkenden Kinder und Jugendlichen des Bundesgymnasiums und Bundesrealgymnasiums Stockerau sowohl als aktive Mitwirkende bei Theateraufführungen und Konzerten als auch als Teilnehmer von Kulturreisen.</li>
    <li>Unterstützung bedürftiger Schülerinnen und Schüler des Bundesgymnasiums und Bundesrealgymnasiums Stockerau unter dem Motto „SchülerInnen helfen SchülerInnen“ und anderer Menschen mit besonderen Bedürfnissen sowie karitativer und kirchlicher Organisationen.</li>
    <li>Näherbringen von Kultur in Land und Stadt aller österreichischen Bundesländer und angrenzenden Nachbarstaaten.</li>
  </ul></div>"""
    write("/ueber-uns", page("/ueber-uns", "Über uns", body, "Der Talenteverein Theater und Musik des BG/BRG Stockerau: gegründet 2016, gemeinnützig, getragen von Schülerinnen und Schülern.", active="/ueber-uns"))

    for name, title in (("impressum", "Impressum"), ("datenschutz", "Datenschutz")):
        txt = open(os.path.join(HERE, name + ".html"), encoding="utf-8").read().replace("{{MAIL}}", MAIL)
        write("/" + name, page("/" + name, title, txt, f"{title} – Talenteverein Theater und Musik des BG/BRG Stockerau."))
    write("/404", page("/404", "Seite nicht gefunden", '<h1 class="page-title">Seite nicht gefunden</h1><div class="wrap prose"><p>Diese Seite gibt es nicht (mehr). <a href="/">Zur Startseite</a></p></div>', "Seite nicht gefunden.", noindex=True))

    # ---- Weiterleitungen (alte Wix-Adressen + Adressen der ersten Fassung vom 14.10.2026)
    R = [("/blank-1", "/ueber-uns"), ("/blank-2", "/bildergalerie"), ("/blank", "/orchester"), ("/blank-4", "/blog"),
         ("/blank-3", "/archiv"), ("/dasdoppeltelottchen", "/produktion/das-doppelte-lottchen-2026"),
         ("/blank-5", "/produktion/wiener-blut-2025"), ("/das-doppelte-lottchen", "/produktion/das-doppelte-lottchen-2026"),
         ("/wiener-blut", "/produktion/wiener-blut-2025")]
    redirects = [{"source": a, "destination": b, "permanent": True} for a, b in R]
    for wix, new in S["wixPosts"].items():
        for s in dict.fromkeys([wix, quote(wix)]):
            redirects.append({"source": f"/post/{s}", "destination": f"/post?post={new}", "permanent": True})
    redirects += [{"source": "/blog/:slug", "destination": "/post?post=:slug", "permanent": True},
                  {"source": "/post/:slug*", "destination": "/blog", "permanent": True},
                  {"source": "/blog/categories/:c*", "destination": "/blog", "permanent": True}]
    cfg = {"$schema": "https://openapi.vercel.sh/vercel.json", "buildCommand": "node scripts/besetzung.mjs", "outputDirectory": "public", "cleanUrls": True, "trailingSlash": False, "redirects": redirects,
           "headers": [{"source": "/(img|assets|media)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                       {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]}
    json.dump(cfg, open(os.path.join(OUT, "vercel.json"), "w"), ensure_ascii=False, indent=2)

    urls = ["/", "/termine", "/blog", "/bildergalerie", "/archiv", "/orchester", "/ueber-uns", "/impressum", "/datenschutz"] + [f"/produktion/{p['key']}" for p in S["productions"]]
    open(os.path.join(PUB, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(PUB, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    import subprocess
    subprocess.run(["node", os.path.join(HERE, "..", "scripts", "besetzung.mjs"), PUB], check=True)
    print("ok –", len(S["productions"]), "Produktionen,", len(SIZES), "Bilder der Seite")

build()
