#!/usr/bin/env python3
"""Erzeugt theaterundmusik-site/ (statisch, für Vercel) aus dem Wix-Export.
Aufruf: python3 build_site.py <media-ordner> <ziel-ordner>
"""
import sys, os, shutil, json, html, unicodedata, re
from PIL import Image, ImageOps

MEDIA, OUT = sys.argv[1], sys.argv[2]
PUB = os.path.join(OUT, "public")
SITE = "https://www.theaterundmusik.at"
MAIL = "ernst.rehberger@bildung.gv.at"
E = html.escape

# ---------------------------------------------------------------- Bilder
def img_id(name):
    return name.replace("~mv2", "").rsplit(".", 1)[0]

SIZES = {}
def build_images():
    os.makedirs(os.path.join(PUB, "img", "t"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(MEDIA, "img"))):
        src = os.path.join(MEDIA, "img", f)
        base, ext = f.rsplit(".", 1)
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        if ext == "png" and im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            for w, sub in ((1600, ""), (640, "t/")):
                c = im.copy(); c.thumbnail((w, w * 2))
                c.save(os.path.join(PUB, "img", sub + base + ".png"), optimize=True)
            SIZES[base] = (im.width, im.height, "png")
            continue
        im = im.convert("RGB")
        for w, q, sub in ((1600, 80, ""), (640, 74, "t/")):
            c = im.copy(); c.thumbnail((w, w * 2))
            c.save(os.path.join(PUB, "img", sub + base + ".jpg"), quality=q, optimize=True, progressive=True)
        SIZES[base] = (im.width, im.height, "jpg")

def src(base, thumb=False):
    w, h, ext = SIZES[base]
    return f"/img/{'t/' if thumb else ''}{base}.{ext}"

def wh(base, maxw):
    w, h, _ = SIZES[base]
    s = min(1, maxw / w)
    return int(w * s), int(h * s)

def figure(base, alt="", caption=None, cls="fig"):
    w, h = wh(base, 1600)
    cap = f"<figcaption>{E(caption)}</figcaption>" if caption else ""
    return (f'<figure class="{cls}"><a href="{src(base)}" data-lightbox>'
            f'<img src="{src(base)}" alt="{E(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></a>{cap}</figure>')

def gallery(bases, alt):
    items = []
    for b in bases:
        w, h = wh(b, 640)
        items.append(f'<a href="{src(b)}" data-lightbox="g"><img src="{src(b, True)}" alt="{E(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></a>')
    return '<div class="gallery">' + "".join(items) + "</div>"

# ---------------------------------------------------------------- Rahmen
NAV = [("/", "Home"), ("/ueber-uns", "Über uns"), ("/bildergalerie", "Bildergalerie"),
       ("/orchester", "Orchester"), ("/blog", "Blog"), ("/archiv", "Archiv")]
SUB = [("/das-doppelte-lottchen", "2026 Das doppelte Lottchen"), ("/wiener-blut", "2025 Wiener Blut")]
LOGO = "1ad5fa_a2e0afd8fe1f49c795180a599518f11d"

def page(path, title, body, desc, og=None, active=None):
    full = f"{title} | Theater & Musik" if title != "Home" else "Theater & Musik – Talenteverein des BG/BRG Stockerau"
    og_img = SITE + (src(og) if og else "/img/og.jpg")
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if active == href else ""
        if href == "/archiv":
            subs = "".join(f'<li><a href="{h}"{" aria-current=page" if active == h else ""}>{E(l)}</a></li>' for h, l in SUB)
            links.append(f'<li class="has-sub"><a href="{href}"{cur}>{E(label)}</a><ul class="sub">{subs}</ul></li>')
        else:
            links.append(f'<li><a href="{href}"{cur}>{E(label)}</a></li>')
    canonical = SITE + (path if path != "/" else "/")
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_AT">
<meta property="og:site_name" content="Theater &amp; Musik">
<meta property="og:title" content="{E(full)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/barlow-condensed-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script src="/assets/site.js" defer></script>
<script type="module" src="/assets/brand/cleebration-credit.js"></script>
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="head">
  <div class="wrap head__bar">
    <a class="brand" href="/"><img src="/img/t/{LOGO}.png" alt="Musical Oper" width="52" height="55"><span>Talenteverein<br><strong>Theater und Musik</strong></span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menü</button>
    <nav id="nav" aria-label="Hauptnavigation"><ul>{''.join(links)}</ul></nav>
  </div>
</header>
<main id="inhalt">
{body}
</main>
<footer class="foot">
  <div class="wrap foot__grid">
    <div><img src="/img/t/{LOGO}.png" alt="" width="64" height="68" class="foot__logo"></div>
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
    p = os.path.join(PUB, fn)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def ids(s):
    return [x.strip() for x in s.replace("\n", ",").split(",") if x.strip()]

# ---------------------------------------------------------------- Blog
POSTS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts.json"), encoding="utf-8"))

def ascii_slug(s):
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

MONATE = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
def datum(iso):
    from datetime import datetime, timedelta
    t = datetime.fromisoformat(iso.replace("Z", "+00:00")) + timedelta(hours=2)  # MESZ (alle Beiträge Mai/Juni)
    y, m, d = t.strftime("%Y-%m-%d").split("-")
    return f"{int(d)}. {MONATE[int(m)-1]} {y}"

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(PUB)
    build_images()
    here = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(os.path.join(here, "assets"), os.path.join(PUB, "assets"))
    os.makedirs(os.path.join(PUB, "media"))
    shutil.copy(os.path.join(MEDIA, "video", "lottchen-trailer-480p.mp4"), os.path.join(PUB, "media", "das-doppelte-lottchen.mp4"))
    shutil.copy(os.path.join(MEDIA, "docs", "plakat-das-doppelte-lottchen.pdf"), os.path.join(PUB, "media", "plakat-das-doppelte-lottchen.pdf"))
    # Favicons / OG
    logo = Image.open(os.path.join(MEDIA, "img", LOGO + ".png")).convert("RGBA")
    box = logo.getbbox(); sq = logo.crop(box)
    for n, s in (("favicon.png", 64), ("apple-touch-icon.png", 180)):
        bg = Image.new("RGBA", sq.size, (0, 0, 0, 255)); bg.alpha_composite(sq)
        bg.convert("RGB").resize((s, s), Image.LANCZOS).save(os.path.join(PUB, n))
    og = Image.new("RGB", (1200, 630), (17, 17, 17))
    l = sq.copy(); l.thumbnail((440, 440)); og.paste(l, (380, 95), l)
    og.save(os.path.join(PUB, "img", "og.jpg"), quality=85)

    POSTER = "c8d331_a026076bc5c44bdb963a1ff273d426d5"
    VIDEO_POSTER = "1ad5fa_562b28ae08e841e894ea1b4d1664d6b1f001"
    video = (f'<video class="video" controls preload="none" playsinline poster="{src(VIDEO_POSTER)}">'
             f'<source src="/media/das-doppelte-lottchen.mp4" type="video/mp4">'
             f'Ihr Browser kann dieses Video nicht abspielen.</video>')

    # ---- Home
    body = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="kicker">Aufführung 2026</p>
      <p class="lead">Wir freuen uns auf unsere neueste Produktion!<br>Im Juni 2026 präsentieren wir</p>
      <h1>Das doppelte Lottchen</h1>
      <p>Der bekannte Kinderroman von Erich Kästner, der 1949 veröffentlicht wurde, wird auf die Bühne gebracht mit eigenen Texten und Liedern.</p>
      <p><a class="btn" href="/das-doppelte-lottchen">Schau dir Impressionen der Probenarbeiten an</a></p>
    </div>
    <div>{video}</div>
  </div>
</section>
<section class="wrap cards">
  <article class="card"><h2>Standort</h2><p>Pfarrzentrum Stockerau<br>Kirchenplatz 3, 2000 Stockerau</p>
    <p><a href="https://www.google.com/maps/place//data=!4m2!3m1!1s0x476d12a53e84d119:0x89aaf1cd8763583d" rel="noopener" target="_blank">Auf der Karte ansehen</a></p></article>
  <article class="card"><h2>Kartenverkauf</h2><p><a class="btn btn--small" href="https://www.oeticket.com/eventseries/das-doppelte-lottchen-theater-mit-musik-1579039/" rel="noopener" target="_blank">Kaufen Sie hier Karten</a></p>
    <img src="{src('c8d331_ef2ef658ad2f4ecd89c5478fd97500e7', True)}" alt="QR-Code zum Kartenverkauf" width="140" height="140" class="qr" loading="lazy"></article>
  <article class="card"><h2>Kontaktdaten</h2><p>kontaktieren Sie uns:</p><p><a class="btn btn--small" href="mailto:{MAIL}?subject=Kontakt">Unsere E-Mail</a></p></article>
  <article class="card card--poster"><h2>Termine</h2>
    <a href="/media/plakat-das-doppelte-lottchen.pdf"><img src="{src(POSTER, True)}" alt="Plakat Das doppelte Lottchen" width="{wh(POSTER,640)[0]}" height="{wh(POSTER,640)[1]}" loading="lazy"></a>
    <p><a href="/media/plakat-das-doppelte-lottchen.pdf">Plakat in Vollbild</a></p></article>
</section>
<section class="wrap duo">
  {figure('c8d331_2fa8e82807284ecd955a70da343434f8', 'Gruppenfoto Gruppe A', 'Gruppe A')}
  {figure('c8d331_c95e49d3f1c248cfb6d4c16373f2376f', 'Gruppenfoto Gruppe B', 'Gruppe B')}
</section>
<section class="wrap imprint-note">
  <p><strong>Eigentümer und Herausgeber:</strong><br>Talenteverein Theater und Musik des BG/BRG Stockerau<br>Unter den Linden 16, 2000 Stockerau</p>
</section>
"""
    write("/", page("/", "Home", body, "Talenteverein Theater und Musik des BG/BRG Stockerau – Musical Oper: Das doppelte Lottchen 2026, Archiv aller Produktionen seit 2001, Orchester und Blog.", og=POSTER, active="/"))

    # ---- Über uns
    body = """
<h1 class="page-title">Über uns</h1>
<div class="wrap prose">
  <h2>Unsere Ziele</h2>
  <p>Unser Verein wurde 2016 gegründet und ist nicht auf Gewinn ausgerichtet.<br>
  Darsteller und Techniker sind alle Schülerinnen und Schüler des <a href="https://www.bgstockerau.ac.at/" rel="noopener" target="_blank">BG/BRG Stockerau</a>.</p>
  <ul class="goals">
    <li>Kulturelle Bildung der mitwirkenden Kinder und Jugendlichen des Bundesgymnasiums und Bundesrealgymnasiums Stockerau sowohl als aktive Mitwirkende bei Theateraufführungen und Konzerten als auch als Teilnehmer von Kulturreisen.</li>
    <li>Unterstützung bedürftiger Schülerinnen und Schüler des Bundesgymnasiums und Bundesrealgymnasiums Stockerau unter dem Motto „SchülerInnen helfen SchülerInnen“ und anderer Menschen mit besonderen Bedürfnissen sowie karitativer und kirchlicher Organisationen.</li>
    <li>Näherbringen von Kultur in Land und Stadt aller österreichischen Bundesländer und angrenzenden Nachbarstaaten.</li>
  </ul>
</div>
"""
    write("/ueber-uns", page("/ueber-uns", "Über uns", body, "Der Talenteverein Theater und Musik des BG/BRG Stockerau: gegründet 2016, gemeinnützig, getragen von Schülerinnen und Schülern.", active="/ueber-uns"))

    # ---- Bildergalerie
    GAL = ids("""c8d331_8381b07bf41449ba9709d4a6944de111, c8d331_401df15294bf4e078833923a7fa2dd00, c8d331_716c944b4c0c40d98e63281a0b318c37, c8d331_ef38fcdb73ef4fc28f4a14f51b44bb36, c8d331_7870aff452b34288a253977e1c06f008, c8d331_97bdc0243c2e491a92d12a3883a2d321, c8d331_182dc96b990d404f9a420237b65ef8c6, c8d331_a5c0657958cf41d0aa8bca61c0ccd7d4, c8d331_6dda2accade24b68b08e2dd0f89a343c, c8d331_98895c41ddb540dcb1fd50fdb84b8f41, c8d331_1a97d2a9a2fe4ecbb1928b960608cffa, c8d331_aa26300581344fc79cb01f71b98b8dff, c8d331_751e25254fc640899d00bba439eb0138, c8d331_d07891887b3945c5860143251f33c64f, c8d331_b8311ef2a6224a6390f26a57697d45c4, c8d331_2e6bfcb949eb42ec9b647dfc8618be0a, c8d331_2a000d777b20477982571b95b160325b, c8d331_7812a113216b450cba0c6fe4cbf2f3df, c8d331_55907741f19f4de9bdcf7aecb34acf90, c8d331_dbc810c8bffe46ccb77b45c4bd2a733b, c8d331_4947a71b453044bd94b0774f835972dc, c8d331_78e50549a1f448c6910b2a693eb59a2b, c8d331_114000c95daa45fba3c6e1311ec8deb9, c8d331_2f04b92654cd4514961c98b6fa8cdd7f, c8d331_84e65f9a42fa4e499b6d78e99e185bef""")
    body = f'<h1 class="page-title">Bildergalerie</h1><div class="wrap"><h2 class="sec">Bildergalerie von Das doppelte Lottchen</h2>{gallery(GAL, "Das doppelte Lottchen")}</div>'
    write("/bildergalerie", page("/bildergalerie", "Bildergalerie", body, "Fotos von „Das doppelte Lottchen“ (2026) – Talenteverein Theater und Musik, BG/BRG Stockerau.", og=GAL[0], active="/bildergalerie"))

    # ---- Orchester
    ORCH = [("Manuela-Josefine Fichtinger", "Klarinette", "1ad5fa_c34944356c3e4ec3817da2a1014760e1", None),
            ("Anna Puskas", "Violoncello", "1ad5fa_61b1e9d82ee14b05bf8fa6fba152d3f8", None),
            ("Chris H. Leeb", "Kontrabass", "1ad5fa_bc1b2d27c7564ee4b7c5b4855a472461", "https://www.cleebration.com"),
            ("Ernst Rehberger", "Gesamtleitung", "1ad5fa_6a81f19867254908b4ff888c118345f3", None),
            ("Josip Matičić", "Violine, Notenarrangement", "1ad5fa_1bd9d65df47c4466906cfe442059bcf9", "https://www.youtube.com/watch?v=Ne_JXvRKgJU"),
            ("Eva Breinschmid", "Violine", "1ad5fa_2014c8cf299e4a6a8db1776b95cde119", "https://www.breinschmid.at/"),
            ("Cornelia Schmidt", "Klavier", "1ad5fa_25fbedca2ef94747a6754caf261b552a", None),
            ("Karin Huf", "Klarinette", "1ad5fa_3bde226b75ac49f7b6263a538118d7f1", None)]
    cards = []
    for n, i, b, link in ORCH:
        w, h = wh(b, 640)
        img = f'<img src="{src(b, True)}" alt="{E(n)}" width="{w}" height="{h}" loading="lazy">'
        if link:
            img = f'<a href="{link}" rel="noopener" target="_blank">{img}</a>'
        cards.append(f'<figure class="person">{img}<figcaption><strong>{E(n)}</strong><span>{E(i)}</span></figcaption></figure>')
    body = f"""<h1 class="page-title">Orchester</h1>
<div class="wrap">{figure('1ad5fa_5a9a3458da824997b96f21fc11e09913', 'Ensemble Unter den Linden', 'Ensemble „Unter den Linden“', cls='fig fig--wide')}
<div class="people">{''.join(cards)}</div></div>"""
    write("/orchester", page("/orchester", "Orchester", body, "Das Orchester „Unter den Linden“ begleitet die Produktionen des Talentevereins Theater und Musik.", og="1ad5fa_5a9a3458da824997b96f21fc11e09913", active="/orchester"))

    # ---- Blog
    cards = []
    for p in POSTS:
        slug = ascii_slug(p["slug"])
        p["new"] = slug
        cover = img_id(p["cover"].rsplit("/", 1)[1])
        w, h = wh(cover, 640)
        cards.append(f'<article class="post-card"><a href="/blog/{slug}"><img src="{src(cover, True)}" alt="" width="{w}" height="{h}" loading="lazy">'
                     f'<time datetime="{p["date"][:10]}">{datum(p["date"])}</time><h2>{E(p["title"].strip())}</h2>'
                     f'{"<p>"+E(p["excerpt"])+"</p>" if p["excerpt"] else ""}</a></article>')
        body_html = re.sub(r"\{\{IMG:([^|}]+)(?:\|([^}]*))?\}\}", lambda m: figure(m.group(1), m.group(2) or p["title"].strip(), m.group(2)), p["html"])
        body_html = re.sub(r"\{\{GAL:([^}]+)\}\}", lambda m: gallery(ids(m.group(1)), p["title"].strip()), body_html)
        write(f"/blog/{slug}", page(f"/blog/{slug}", p["title"].strip(),
              f'<article class="wrap prose post"><p class="back"><a href="/blog">← Alle Beiträge</a></p><time datetime="{p["date"][:10]}">{datum(p["date"])}</time><h1>{E(p["title"].strip())}</h1>{body_html}</article>',
              p["excerpt"] or p["title"].strip() + " – Blog des Talentevereins Theater und Musik, BG/BRG Stockerau.", og=cover, active="/blog"))
    body = f'<h1 class="page-title">Blog</h1><div class="wrap posts">{"".join(cards)}</div>'
    write("/blog", page("/blog", "Blog", body, "Neuigkeiten von den Proben und Aufführungen des Talentevereins Theater und Musik.", active="/blog"))

    # ---- Archiv
    SHOWS = """2001/2002 Hänsel und Gretel|2002/2003 Der verlorene Sohn|2003/2004 Die sonderbare Nacht|2004/2005 Max und Moritz|2005/2006 Suleilas erste Weihnacht|2006/2007 Die Zauberflöte|2007/2008 Lumpazivagabundus|2008/2009 Der Bauer als Millionär|2009/2010 Im weißen Rössl|2010/2011 Die Fledermaus|2011/2012 Gräfin Mariza|2012/2013 Der Vogelhändler|2013/2014 My Fair Lady|2014/2015 Wiener Blut|2015/2016 Im weißen Rössl|2016/2017 Hallo Dienstmann|2017/2018 My Fair Lady|2018/2019 Emil und die Detektive|2019/2020 Der Vogelhändler|2020/2021 Pension Schöller|2021/2022 Der Bauer als Millionär|2022/2023 Pünktchen und Anton|2023/2024 Im weißen Rössl|2024/2025 Wiener Blut|2025/2026 Das doppelte Lottchen""".split("|")
    rows = []
    for s in reversed(SHOWS):
        yr, name = s.split(" ", 1)
        link = {"2025/2026": "/das-doppelte-lottchen", "2024/2025": "/wiener-blut"}.get(yr)
        nm = f'<a href="{link}">{E(name)}</a>' if link else E(name)
        rows.append(f"<li><span>{yr}</span>{nm}</li>")
    body = f"""<h1 class="page-title">Archiv</h1>
<div class="wrap archive">
  <div class="archive__now"><p class="kicker">20. – 25. Juni 2026</p><h2><a href="/das-doppelte-lottchen">Das doppelte Lottchen</a></h2>
    <a href="/media/plakat-das-doppelte-lottchen.pdf"><img src="{src(POSTER, True)}" alt="Plakat Das doppelte Lottchen" width="{wh(POSTER,640)[0]}" height="{wh(POSTER,640)[1]}" loading="lazy"></a></div>
  <div><h2 class="sec">Bisherige Aufführungen</h2><ol class="shows" reversed>{''.join(rows)}</ol></div>
</div>"""
    write("/archiv", page("/archiv", "Archiv", body, "Alle Produktionen der Musical Oper am BG/BRG Stockerau seit 2001/2002 – von Hänsel und Gretel bis Das doppelte Lottchen.", og=POSTER, active="/archiv"))

    # ---- Das doppelte Lottchen
    LOT = ids("""c8d331_a026076bc5c44bdb963a1ff273d426d5, c8d331_8381b07bf41449ba9709d4a6944de111, c8d331_401df15294bf4e078833923a7fa2dd00, c8d331_716c944b4c0c40d98e63281a0b318c37, c8d331_ef38fcdb73ef4fc28f4a14f51b44bb36, c8d331_80ebe0a78fe243e1b67a8df000af2526, c8d331_7bd08a19e06840a2b0a21dc079e54c6d, c8d331_2fa8e82807284ecd955a70da343434f8, c8d331_b2316e68e1ae49819a208a5ed68d5306, c8d331_f328fc28950a4b55802c0bccd1f21d41, c8d331_c95e49d3f1c248cfb6d4c16373f2376f, c8d331_7870aff452b34288a253977e1c06f008, c8d331_4947a71b453044bd94b0774f835972dc, c8d331_1a97d2a9a2fe4ecbb1928b960608cffa, c8d331_182dc96b990d404f9a420237b65ef8c6""")
    body = f"""<h1 class="page-title">Das doppelte Lottchen <span>2025/26</span></h1>
<div class="wrap split">
  <div class="prose"><p>In diesem Schuljahr 2025/2026 führen wir das Stück „Das doppelte Lottchen“ von Erich Kästner auf. Das erstmals 1950 erschienene Buch wird von uns, dank des Theaterstücks des Bühnenverlags Weitendorf, vorgetragen und mit selbst komponierter Musik von Josip Matičić und Ernst Rehberger begleitet. Wir sind schon sehr gespannt, arbeiten und proben fleißig und hoffen, dass unser Projekt ein großer Erfolg wird. Wir freuen uns, Sie auch dieses Mal bei unseren Vorstellungen begrüßen zu dürfen.</p>
  <p class="sig">Nicolas Bolvari / Michael Fitz</p></div>
  <div>{video}</div>
</div>
<div class="wrap"><h2 class="sec">Ein paar Impressionen</h2>{gallery(LOT, "Das doppelte Lottchen")}</div>"""
    write("/das-doppelte-lottchen", page("/das-doppelte-lottchen", "2026 Das doppelte Lottchen", body, "Das doppelte Lottchen nach Erich Kästner – Produktion 2025/26 der Musical Oper am BG/BRG Stockerau, Musik von Josip Matičić und Ernst Rehberger.", og=POSTER, active="/das-doppelte-lottchen"))

    # ---- Wiener Blut
    IMP = ids("1ad5fa_bf2027b37b0f45f5a861bbe01e4b0d45, 1ad5fa_ef4f606964984c6c9af0596fbac41887, 1ad5fa_14594e6d069a4539b998664e5aefba18, 1ad5fa_fc7591c3b0574053b843d0965e783eea, 1ad5fa_a519c735a7ac438daaa2f49cdb51f22c, 1ad5fa_6f36ad35ca504d09a8dede81dd833e97, 1ad5fa_516d4c6f4e1645c0b1d12f3bec5f2092, 1ad5fa_ae018137518245388a7bc350b8404e47, 1ad5fa_eb21398278b547f5b7c80b4090f39c09, 1ad5fa_b3dc824f49454cc78004e7c35dca463b, 1ad5fa_1eb7a5e8a2c74727af6a23c9ed4e025c, 1ad5fa_5c34185e37b14e20b096a002148a953c")
    IBK = ids("8bb438_dbc34d8b0df546e3b720b14ff670ba83, 8bb438_f2d393d3ad61468890a2616c56fff0f5, 8bb438_e83d8cc28a044555b7672018983789a7, 8bb438_22ae62c08916403d955425d5e8c70a11, 8bb438_189ac9d807b640ffbeca24c41d965bae, 8bb438_02133a81229f49e09dc4c20f107f1eb6, 8bb438_f7a5e921e855433896901546de91b43e, 8bb438_927f3e749a784536afbcdd81890e8064f003, 8bb438_31254b5ad37446c8949144e34adc2113, 8bb438_c9e1a83e7f7b43799dbe5a8d3fd81f0b, 8bb438_324d1f8b463e45d891b5de00c83989ad, 8bb438_f6bbdd3a41df4bcab09c7333855ba583f003, 1ad5fa_f06907c0ec814ee3ae23f1e4fb3dcad5, 1ad5fa_083936134b864c8e93518e2f2e5c608f, 1ad5fa_91239454a7ef476eb46eecf5417dc8f5, 1ad5fa_93ba1c0405d64b23bd8b764e69ab39d1, 1ad5fa_071dc16ec76d47ce8f1c43dd3c2d2d9b, 1ad5fa_a86a0810e644446db729f6025158b1e7, 1ad5fa_01ce53c8e0fc49c0bbfefd53bf9a71b1, 1ad5fa_9aa430a09fb545308a38739d6d0688db, 1ad5fa_cbbd294b3efd4fd69d579e61918070a7")
    Q = json.load(open(os.path.join(here, "quotes.json"), encoding="utf-8"))
    quotes = "".join(f'<blockquote>{"".join("<p>"+E(x)+"</p>" for x in q["text"])}<footer>{E(q["by"])}</footer></blockquote>' for q in Q)
    body = f"""<h1 class="page-title">Wiener Blut <span>19. – 22. Juni 2025</span></h1>
<div class="wrap prose"><p>Das Schuljahr 2024/2025 war ein wunderschönes Jahr für die Unverbindliche Übung Musical Oper. Im Johann Strauß Jahr stand heuer die Operette „Wiener Blut“ am Programm. Nach acht sehr erfolgreichen Aufführungen folgte von 19. bis 22. Juni 2025 die traditionelle Musical Oper Reise nach Innsbruck. Wir durften Tirol bei herrlichstem Wetter genießen.</p>
<p class="sig">MMag. Ernst Rehberger</p></div>
<div class="wrap"><h2 class="sec">Ein paar Impressionen</h2>{gallery(IMP, "Wiener Blut")}
<h2 class="sec">Reise nach Innsbruck</h2>{gallery(IBK, "Reise nach Innsbruck")}</div>
<div class="wrap quotes">{quotes}</div>"""
    write("/wiener-blut", page("/wiener-blut", "2025 Wiener Blut", body, "Wiener Blut 2025: acht Aufführungen der Musical Oper am BG/BRG Stockerau und die Reise nach Innsbruck.", og="1ad5fa_b3dc824f49454cc78004e7c35dca463b", active="/wiener-blut"))

    # ---- Rechtliches
    for name in ("impressum", "datenschutz"):
        txt = open(os.path.join(here, name + ".html"), encoding="utf-8").read().replace("{{MAIL}}", MAIL)
        title = "Impressum" if name == "impressum" else "Datenschutz"
        write("/" + name, page("/" + name, title, txt, f"{title} – Talenteverein Theater und Musik des BG/BRG Stockerau."))

    # ---- 404
    write("/404", page("/404", "Seite nicht gefunden", '<h1 class="page-title">Seite nicht gefunden</h1><div class="wrap prose"><p>Diese Seite gibt es nicht (mehr). <a href="/">Zur Startseite</a></p></div>', "Seite nicht gefunden."))

    # ---- vercel.json: alte Wix-Adressen
    redirects = [{"source": a, "destination": b, "permanent": True} for a, b in [
        ("/blank-1", "/ueber-uns"), ("/blank-2", "/bildergalerie"), ("/blank", "/orchester"),
        ("/blank-4", "/blog"), ("/blank-3", "/archiv"), ("/dasdoppeltelottchen", "/das-doppelte-lottchen"),
        ("/blank-5", "/wiener-blut")]]
    from urllib.parse import quote
    for p in POSTS:
        for s in {p["slug"], quote(p["slug"])}:
            redirects.append({"source": "/post/" + s, "destination": "/blog/" + p["new"], "permanent": True})
    redirects.append({"source": "/post/:slug*", "destination": "/blog", "permanent": True})
    redirects.append({"source": "/blog/categories/:c*", "destination": "/blog", "permanent": True})
    cfg = {"$schema": "https://openapi.vercel.sh/vercel.json", "cleanUrls": True, "trailingSlash": False,
           "redirects": redirects,
           "headers": [{"source": "/(img|assets|media)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                       {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                                       {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]}]}
    json.dump(cfg, open(os.path.join(OUT, "vercel.json"), "w"), ensure_ascii=False, indent=2)

    # ---- sitemap/robots
    urls = ["/", "/ueber-uns", "/bildergalerie", "/orchester", "/blog", "/archiv", "/das-doppelte-lottchen", "/wiener-blut", "/impressum", "/datenschutz"] + [f"/blog/{p['new']}" for p in POSTS]
    with open(os.path.join(PUB, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u if u != '/' else '/'}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(PUB, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print("ok", len(POSTS), "Beiträge,", len(SIZES), "Bilder")

build()
