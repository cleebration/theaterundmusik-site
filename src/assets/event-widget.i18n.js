/*
 * event-widget.i18n.js
 * Sprachfaehige Variante des Event-Moduls. Gegenueber der einsprachigen Version
 * sind GENAU vier Dinge anders (dieselben vier Schritte gelten 1:1 fuer das Blog-
 * und Galerie-Modul – siehe RETROFIT.md):
 *
 *   (1) STRINGS-Tabelle pro Sprache (Status-Labels, Datums-Locale, Buttontexte)
 *   (2) currentLang(): liest die aktive Sprache von window.SiteI18n
 *                      (Rueckfall: lang-Attribut, dann "de")
 *   (3) Feed-URL mit Platzhalter {lang}: feed=".../cleebration.{lang}.json"
 *   (4) auf "i18n:change" hoeren -> Sprache neu bestimmen, ggf. neu laden, neu rendern
 *
 * Einbetten:
 *   <script type="module" src="/event-widget.i18n.js"></script>
 *   <event-list  feed="https://HUB/feed/sites/cleebration.{lang}.json"
 *                detail-url="/events/event.html"></event-list>
 *   <event-detail feed="https://HUB/feed/sites/cleebration.{lang}.json"></event-detail>
 *
 * Themebar ueber --evt-* CSS-Variablen (identisch zur einsprachigen Version).
 */

/* (1) ---- Sprachabhaengige UI-Texte ------------------------------------- */
const STRINGS = {
  de: {
    locale: "de-AT",
    status: { scheduled: null, soldout: "Ausverkauft", cancelled: "Abgesagt", postponed: "Verschoben" },
    tickets: "Tickets",
    details: "Details",
    none: "Derzeit keine Veranstaltungen.",
    loadError: "Veranstaltungen konnten nicht geladen werden.",
    frueher: "Frühere Veranstaltung",
    spaeter: "Spätere Veranstaltung",
    alleTermine: "Alle Veranstaltungen",
    fallbackNote: "Übersetzung folgt",
    // PATCH Redaktion 2026-10-08: mehrere Termine, Programm, Hinweis, Nachbericht
    weitereTermine: "Alle Termine", programm: "Programm", mitwirkende: "Mitwirkende", nachbericht: "Nachbericht", fotos: "Fotos ansehen", einlass: "Einlass", verschobenAuf: "neuer Termin", dieserTermin: "dieser Termin", gross: "Doppelklick: Bild groß anzeigen", schliessen: "Schließen",
    // PATCH kalender (ersetzt AddEvent)
    kalender: "In den Kalender",
    abo: "Kalender abonnieren",
    aboHinweis: "Neue Termine erscheinen dann von selbst in deinem Kalender.",
    kal: { google: "Google Kalender", ics: "Apple Kalender / Outlook-Programm", outlook: "Outlook.com", m365: "Microsoft 365 (Arbeit/Schule)" }
  },
  en: {
    locale: "en-GB",
    status: { scheduled: null, soldout: "Sold out", cancelled: "Cancelled", postponed: "Postponed" },
    tickets: "Tickets",
    details: "Details",
    none: "No events at the moment.",
    loadError: "Events could not be loaded.",
    frueher: "Earlier event",
    spaeter: "Later event",
    alleTermine: "All events",
    fallbackNote: "Translation pending",
    weitereTermine: "All dates", programm: "Programme", mitwirkende: "Performers", nachbericht: "Review", fotos: "View photos", einlass: "Doors", verschobenAuf: "new date", dieserTermin: "this date", gross: "Double-click to enlarge", schliessen: "Close",
    // PATCH kalender (replaces AddEvent)
    kalender: "Add to calendar",
    abo: "Subscribe to calendar",
    aboHinweis: "New events will then appear in your calendar automatically.",
    kal: { google: "Google Calendar", ics: "Apple Calendar / Outlook app", outlook: "Outlook.com", m365: "Microsoft 365 (work/school)" }
  }
};
const DEFAULT_LANG = "de";

/* (2) ---- Aktive Sprache bestimmen -------------------------------------- */
function currentLang(el) {
  if (window.SiteI18n && window.SiteI18n.lang) return window.SiteI18n.lang;
  const attr = el && el.getAttribute("lang");
  if (attr) return attr;
  return DEFAULT_LANG;
}
/* Rückfall über die Basissprache: "pt-BR" nimmt "pt", bevor es auf die
   Standardsprache zurückfällt. Dieselbe Regel wie im Galerie-, Blog- und
   Newsletter-Modul, damit sich alle vier gleich verhalten. */
function strings(lang) {
  return (
    STRINGS[lang] ||
    STRINGS[String(lang).split("-")[0]] ||
    STRINGS[DEFAULT_LANG]
  );
}

const STYLES = `
  :host {
    --evt-font-display: var(--evt-font, Georgia, "Times New Roman", serif);
    --evt-font-body: var(--evt-font, system-ui, -apple-system, "Segoe UI", sans-serif);
    --evt-bg: transparent; --evt-surface: #fff; --evt-text: #1a1a1a;
    --evt-muted: #6b6b6b; --evt-accent: #1a1a1a; --evt-accent-contrast: #fff;
    --evt-border: #e4e1da; --evt-radius: 4px; --evt-gap: 1.75rem; --evt-maxwidth: 1120px;
    display: block; color: var(--evt-text); background: var(--evt-bg);
    font-family: var(--evt-font-body); line-height: 1.55; box-sizing: border-box;
  }
  *, *::before, *::after { box-sizing: inherit; }
  .wrap { max-width: var(--evt-maxwidth); margin: 0 auto; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--evt-gap); }
  .card { display: flex; flex-direction: column; background: var(--evt-surface);
    border: 1px solid var(--evt-border); border-radius: var(--evt-radius); overflow: hidden;
    text-decoration: none; color: inherit; transition: transform .18s ease, box-shadow .18s ease; }
  .card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,.10); }
  .card:focus-visible { outline: 3px solid var(--evt-accent); outline-offset: 2px; }
  .card__media { aspect-ratio: 3 / 2; background: var(--evt-border); overflow: hidden; }
  .card__media img { width: 100%; height: 100%; object-fit: cover; }
  .card__body { padding: 1.1rem 1.2rem 1.3rem; display: flex; flex-direction: column; gap: .5rem; flex: 1; }
  .date { font-size: .82rem; letter-spacing: .04em; text-transform: uppercase; color: var(--evt-muted); }
  .title { font-family: var(--evt-font-display); font-size: 1.3rem; margin: 0; line-height: 1.2; }
  .summary { color: var(--evt-muted); margin: 0; }
  .meta { margin-top: auto; display: flex; align-items: center; gap: .6rem; flex-wrap: wrap; padding-top: .4rem; }
  .pill { font-size: .72rem; font-weight: 600; padding: .15rem .55rem; border-radius: 999px;
    background: var(--evt-accent); color: var(--evt-accent-contrast); }
  .pill--muted { background: var(--evt-border); color: var(--evt-text); }
  .empty, .error { color: var(--evt-muted); padding: 2rem 0; }
  /* Detail */
  /* PATCH Redaktion 2026-10-08: Bild/Plakat ganz zeigen (nicht beschneiden), Doppelklick = gross */
  .detail__media { background: var(--evt-border); border-radius: var(--evt-radius); overflow: hidden; margin-bottom: 1.5rem; display: flex; justify-content: center; }
  .detail__media img { display: block; width: auto; max-width: 100%; height: auto; max-height: 80vh; object-fit: contain; cursor: zoom-in; }
  .lb { position: fixed; inset: 0; z-index: 2147483000; background: rgba(0,0,0,.92); display: flex; align-items: center; justify-content: center; padding: 2vmin; cursor: zoom-out; }
  .lb[hidden] { display: none; }
  .lb img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .lb button { position: absolute; top: .5rem; right: .9rem; font-size: 2.4rem; line-height: 1; background: none; border: 0; color: #fff; cursor: pointer; }
  .detail__title { font-family: var(--evt-font-display); font-size: clamp(1.8rem, 4vw, 2.6rem); margin: 0 0 .5rem; }
  .detail__facts { display: flex; gap: 1.4rem; flex-wrap: wrap; color: var(--evt-muted); margin-bottom: 1.4rem; }
  .detail__body { max-width: 70ch; }
  .detail__h { font-family: var(--evt-font-display); font-size: 1.3rem; margin: 1.6rem 0 .5rem; }
  .hinweis { max-width: 70ch; border-left: 4px solid var(--evt-accent); padding: .6rem 1rem; background: color-mix(in srgb, var(--evt-accent) 8%, transparent); }
  .termine-liste { padding-left: 1.1rem; } .termine-liste li { margin: .3rem 0; } .termine-liste li.weg { text-decoration: line-through; opacity: .6; }
  .detail__body a { color: var(--evt-accent); }
  /* Blaettern zwischen Terminen. Zwei Spalten, damit der spaetere Termin
     rechts bleibt, auch wenn es links keinen frueheren gibt. */
  .umblaettern { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
                 margin-top: 2.5rem; padding-top: 1.25rem;
                 border-top: 1px solid var(--evt-border); }
  .umblaettern a { text-decoration: none; color: inherit; }
  .umblaettern a:hover .blatt__titel { color: var(--evt-accent); }
  .blatt--rechts { text-align: right; }
  .blatt__richtung { display: block; font-size: .78rem; color: var(--evt-muted);
                     text-transform: uppercase; letter-spacing: .06em; margin-bottom: .2rem; }
  .blatt__titel { display: block; font-family: var(--evt-font-display);
                  font-size: 1.05rem; line-height: 1.25; }
  @media (max-width: 34rem) {
    .umblaettern { grid-template-columns: 1fr; }
    .blatt--rechts { text-align: left; }
  }
  .btn { display: inline-block; margin-top: 1.4rem; padding: .7rem 1.4rem; border-radius: var(--evt-radius);
    background: var(--evt-accent); color: var(--evt-accent-contrast); text-decoration: none; font-weight: 600; }
  /* PATCH kalender: "In den Kalender" / "Kalender abonnieren" (ersetzt AddEvent) */
  .aktionen { display: flex; flex-wrap: wrap; gap: .75rem; align-items: flex-start; margin-top: 1.4rem; }
  .aktionen .btn { margin-top: 0; }
  .kal { display: inline-block; }
  .kal > summary { list-style: none; cursor: pointer; display: inline-block; padding: .7rem 1.4rem;
    border: 1px solid var(--evt-accent); border-radius: var(--evt-radius); color: var(--evt-accent);
    background: transparent; font-weight: 600; }
  .kal > summary::-webkit-details-marker { display: none; }
  .kal > summary::after { content: " ▾"; }
  .kal[open] > summary::after { content: " ▴"; }
  .kal > summary:focus-visible { outline: 3px solid var(--evt-accent); outline-offset: 2px; }
  .kal__menu { margin: .4rem 0 0; padding: .3rem 0; list-style: none; background: var(--evt-surface);
    border: 1px solid var(--evt-border); border-radius: var(--evt-radius); min-width: 16rem; }
  .kal__menu a { display: block; padding: .5rem 1rem; color: var(--evt-text); text-decoration: none; }
  .kal__menu a:hover, .kal__menu a:focus-visible { background: var(--evt-border); }
  .kal__hinweis { margin: .4rem 0 0; font-size: .85rem; color: var(--evt-muted); }
  .kal--abo { margin-top: 1.5rem; }
`;

function fmtDate(iso, tz, locale) {
  try {
    return new Intl.DateTimeFormat(locale, {
      weekday: "short", day: "2-digit", month: "long", year: "numeric",
      hour: "2-digit", minute: "2-digit", timeZone: tz || "Europe/Vienna"
    }).format(new Date(iso));
  } catch { return iso; }
}

async function loadFeed(rawUrl, lang) {
  const url = rawUrl.replace(/\{lang\}/g, lang);
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}


/* Warten, bis die Sprache der Seite feststeht.

   Ohne das zeichnet das Modul in der Standardsprache, holt deren Feed, und
   zeichnet unmittelbar danach noch einmal in der wirklichen Sprache — zwei
   Abrufe und ein sichtbares Flackern.

   Auf einer fremden Seite ohne SiteI18n gibt es nichts zu warten; dort
   zeichnet das Modul sofort. */
function spracheBereit() {
  const i = window.SiteI18n;
  if (!i || !i.ready) return Promise.resolve();
  /* Notausgang: bindet eine Seite site-i18n.js ein, ruft aber nie init()
     auf, loest das Versprechen nie auf -- und das Modul bliebe fuer immer
     leer. Nach zwei Sekunden wird deshalb in der Standardsprache
     gezeichnet. */
  const notausgang = new Promise((r) => setTimeout(r, 2000));
  return Promise.race([i.ready, notausgang]).catch(() => {});
}

/* ---- PATCH kalender: Kalender-Links (ersetzt AddEvent.com) -------------
   Google, Outlook.com und Microsoft 365 bekommen einen Link mit den Daten
   im Aufruf. Apple und Outlook-Programm bekommen die .ics-Datei, die der
   Hub fuer jeden Termin baut (Feld `ics`). Fehlt sie (alter Hub), wird die
   Datei hier im Browser erzeugt. */
const KAL_STANDARD_DAUER_MIN = 120; // gleich wie im Hub (kalender.mjs)

function kalEnde(e) {
  return e.endDate ? new Date(e.endDate)
    : new Date(new Date(e.date).getTime() + KAL_STANDARD_DAUER_MIN * 60e3);
}
function kalZeit(d) { return new Date(d).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, ""); }
function kalOrt(e) { return [e.venue, e.address || e.city].filter(Boolean).join(", "); }
function absolut(pfad, basis) {
  try { return new URL(pfad, new URL(basis, location.href)).href; } catch { return pfad; }
}
/* Text des Kalendereintrags -- gleich wie im Hub (kalender.mjs):
   Kurztext, Beschreibung, Tickets (nur wenn gesetzt), Details-Link.
   Fuer die Links wird gekuerzt, weil Google/Outlook lange Adressen abschneiden. */
function kalOhneHtml(html) {
  return String(html ?? "")
    .replace(/<\/(p|li|h\d)>/gi, "\n").replace(/<br\s*\/?>/gi, "\n").replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\n{3,}/g, "\n\n").trim();
}
function kalText(e, seite, max = 1500) {
  const kurz = String(e.summary ?? "").trim();
  let lang = kalOhneHtml(e.body);
  if (kurz && lang.startsWith(kurz)) lang = lang.slice(kurz.length).trim();
  const ende = [e.ticketUrl ? `Tickets: ${e.ticketUrl}` : "", (seite || e.url) ? `Details: ${seite || e.url}` : ""].filter(Boolean);
  let kopf = [kurz, lang].filter(Boolean).join("\n\n");
  if (kopf.length > max) kopf = kopf.slice(0, max).replace(/\s+\S*$/, "") + " …";
  return [kopf, ...ende].filter(Boolean).join("\n\n");
}

function icsNotfall(e, seite) {
  const t = (s) => String(s ?? "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n");
  const z = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//cleebration//event-widget//DE", "BEGIN:VEVENT",
    `UID:${e.slug}@cleebration-events-hub`, `DTSTAMP:${kalZeit(new Date())}`,
    `DTSTART:${kalZeit(e.date)}`, `DTEND:${kalZeit(kalEnde(e))}`, `SUMMARY:${t(e.title)}`,
    kalOrt(e) ? `LOCATION:${t(kalOrt(e))}` : "", `DESCRIPTION:${t(kalText(e, seite, 100000))}`,
    "END:VEVENT", "END:VCALENDAR"].filter(Boolean);
  return "data:text/calendar;charset=utf-8," + encodeURIComponent(z.join("\r\n"));
}

function kalenderLinks(e, feedUrl, seite) {
  const q = encodeURIComponent;
  const start = new Date(e.date), ende = kalEnde(e);
  const text = kalText(e, seite);
  const ms = (basis) => `${basis}/calendar/0/action/compose?path=%2Fcalendar%2Faction%2Fcompose&rru=addevent` +
    `&subject=${q(e.title)}&startdt=${q(start.toISOString())}&enddt=${q(ende.toISOString())}` +
    `&body=${q(text)}&location=${q(kalOrt(e))}`;
  return {
    google: "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      `&text=${q(e.title)}&dates=${kalZeit(start)}/${kalZeit(ende)}` +
      `&details=${q(text)}&location=${q(kalOrt(e))}&ctz=${q(e.timeZone || "Europe/Vienna")}`,
    ics: e.ics ? absolut(e.ics, feedUrl) : icsNotfall(e, seite),
    outlook: ms("https://outlook.live.com"),
    m365: ms("https://outlook.office.com")
  };
}

/* Nur fuer kommende Termine, die stattfinden. */
function kalenderKnopf(e, t, feedUrl, seite) {
  if (!e.date || e.status === "cancelled") return "";
  if (new Date(e.date).getTime() < Date.now()) return "";
  const l = kalenderLinks(e, feedUrl, seite);
  const ziel = (k) => k === "ics" ? "" : ` target="_blank" rel="noopener"`;
  return `
    <details class="kal">
      <summary>${esc(t.kalender)}</summary>
      <ul class="kal__menu">
        ${["google", "ics", "outlook", "m365"].map((k) =>
          `<li><a href="${esc(l[k])}"${ziel(k)}>${esc(t.kal[k])}</a></li>`).join("")}
      </ul>
    </details>`;
}

/* Abo-Kalender einer Seite. <event-list abo> leitet die Adresse aus dem
   Feed ab (…/feed/sites/X.{lang}.json -> …/feed/ics/sites/X.<lang>.ics);
   abo="https://…" setzt sie ausdruecklich. */
function aboKnopf(el, t, lang) {
  if (!el.hasAttribute("abo")) return "";
  const wert = el.getAttribute("abo");
  let https = /^https?:/.test(wert || "") ? wert : null;
  if (!https) {
    const feed = absolut((el.getAttribute("feed") || "").replace(/\{lang\}/g, lang), location.href);
    const m = feed.match(/^(.*)\/feed\/sites\/([^/]+?)(?:\.[a-z]{2}(?:-[A-Za-z]+)?)?\.json(?:\?.*)?$/);
    if (!m) return "";
    https = `${m[1]}/feed/ics/sites/${m[2]}.${lang}.ics`;
  }
  const webcal = https.replace(/^https?:/, "webcal:");
  const q = encodeURIComponent;
  const links = {
    ics: webcal,
    google: `https://calendar.google.com/calendar/render?cid=${q(webcal)}`,
    outlook: `https://outlook.live.com/calendar/0/addfromweb?url=${q(https)}`
  };
  return `
    <details class="kal kal--abo">
      <summary>${esc(t.abo)}</summary>
      <ul class="kal__menu">
        ${["google", "ics", "outlook"].map((k) =>
          `<li><a href="${esc(links[k])}"${k === "ics" ? "" : ` target="_blank" rel="noopener"`}>${esc(t.kal[k])}</a></li>`).join("")}
      </ul>
      <p class="kal__hinweis">${esc(t.aboHinweis)}</p>
    </details>`;
}

/* ---- <event-list> ------------------------------------------------------- */
class EventList extends HTMLElement {
  static get observedAttributes() { return ["feed", "lang", "detail-url", "show", "abo", "from", "to", "limit"]; }
  connectedCallback() {
    this.attachShadow({ mode: "open" });
    // (4) auf Sprachwechsel reagieren
    this._unsub = window.SiteI18n
      ? window.SiteI18n.onChange(() => { if (this._gezeichnet) this.refresh(); })
      : () => {};
    spracheBereit().then(() => { this._gezeichnet = true; this.refresh(); });
  }
  disconnectedCallback() { this._unsub && this._unsub(); }
  attributeChangedCallback() { if (this.shadowRoot) this.refresh(); }

  async refresh() {
    const lang = currentLang(this);
    const t = strings(lang);
    const feed = this.getAttribute("feed");
    const detailUrl = this.getAttribute("detail-url") || "#";
    const show = this.getAttribute("show") || "upcoming";
    this.shadowRoot.innerHTML = `<style>${STYLES}</style><div class="wrap"><p class="empty">…</p></div>`;

    let items;
    try { items = await loadFeed(feed, lang); }
    catch { this.shadowRoot.querySelector(".wrap").innerHTML = `<p class="error">${t.loadError}</p>`; return; }

    const now = Date.now();
    if (show === "upcoming") items = items.filter((e) => new Date(e.date).getTime() >= now - 36e5);
    // PATCH cleebration (siehe site/README.md): Vergangenes liest man rückwärts —
    // das zuletzt Gespielte zuerst, wie schon auf der alten Wix-Seite.
    if (show === "past") {
      items = items
        .filter((e) => new Date(e.date).getTime() < now)
        .sort((a, b) => new Date(b.date) - new Date(a.date));
    }

    // PATCH theaterundmusik: from="JJJJ-MM-TT" / to="JJJJ-MM-TT" grenzen auf einen Zeitraum ein
    // (eine Produktion = ein Schuljahr). show="all" zeigt alles im Zeitraum, aufsteigend.
    const von = this.getAttribute("from"), bis = this.getAttribute("to");
    if (von) items = items.filter((e) => new Date(e.date).getTime() >= new Date(von + "T00:00:00").getTime());
    if (bis) items = items.filter((e) => new Date(e.date).getTime() <= new Date(bis + "T23:59:59").getTime());

    // PATCH lko-site: limit="N" zeigt nur die ersten N (Startseite: 3 zuletzt gespielte).
    const limit = parseInt(this.getAttribute("limit") || "", 10);
    if (limit > 0) items = items.slice(0, limit);

    const wrap = this.shadowRoot.querySelector(".wrap");
    if (!items.length) { wrap.innerHTML = `<p class="empty">${t.none}</p>${aboKnopf(this, t, lang)}`; return; }

    wrap.innerHTML = `<div class="grid">${items.map((e) => card(e, t, detailUrl)).join("")}</div>${aboKnopf(this, t, lang)}`;
  }
}

function card(e, t, detailUrl) {
  const statusLabel = t.status[e.status];
  const href = `${detailUrl}${detailUrl.includes("?") ? "&" : "?"}event=${encodeURIComponent(e.slug)}`;
  return `
    <a class="card" href="${href}">
      ${e.image ? `<div class="card__media"><img src="${e.image}" alt="" loading="lazy"></div>` : ""}
      <div class="card__body">
        <div class="date">${fmtDate(e.date, e.timeZone, t.locale)}</div>
        <h3 class="title">${esc(e.title)}</h3>
        ${e.summary ? `<p class="summary">${esc(e.summary)}</p>` : ""}
        <div class="meta">
          ${statusLabel ? `<span class="pill">${statusLabel}</span>` : ""}
          ${e.translated === false ? `<span class="pill pill--muted">${t.fallbackNote}</span>` : ""}
          ${e.venue ? `<span class="date">${esc(e.venue)}</span>` : ""}
        </div>
      </div>
    </a>`;
}

/* ---- <event-detail> ----------------------------------------------------- */
class EventDetail extends HTMLElement {
  static get observedAttributes() { return ["feed", "lang", "event"]; }
  connectedCallback() {
    this.attachShadow({ mode: "open" });
    this._unsub = window.SiteI18n
      ? window.SiteI18n.onChange(() => { if (this._gezeichnet) this.refresh(); })
      : () => {};
    spracheBereit().then(() => { this._gezeichnet = true; this.refresh(); });
  }
  disconnectedCallback() { this._unsub && this._unsub(); }
  attributeChangedCallback() { if (this.shadowRoot) this.refresh(); }

  async refresh() {
    const lang = currentLang(this);
    const t = strings(lang);
    const feed = this.getAttribute("feed");
    const slug = this.getAttribute("event") ||
      new URLSearchParams(location.search).get("event");
    this.shadowRoot.innerHTML = `<style>${STYLES}</style><div class="wrap"><p class="empty">…</p></div>`;

    let items;
    try { items = await loadFeed(feed, lang); }
    catch { this.shadowRoot.querySelector(".wrap").innerHTML = `<p class="error">${t.loadError}</p>`; return; }

    const i = items.findIndex((x) => x.slug === slug);
    const wrap = this.shadowRoot.querySelector(".wrap");
    if (i < 0) { wrap.innerHTML = `<p class="error">${t.none}</p>`; return; }
    const e = items[i];

    /* Der Feed kommt chronologisch aufsteigend: davor liegt der fruehere
       Termin, danach der spaetere. Bewusst ohne Ringschluss -- vom letzten
       auf den ersten Termin zu springen waere keine Navigation, sondern
       eine Ueberraschung. */
    const frueher = items[i - 1] || null;
    const spaeter = items[i + 1] || null;

    const detailUrl = this.getAttribute("detail-url") || location.pathname;
    const nachbarUrl = (s) => `${detailUrl}${detailUrl.includes("?") ? "&" : "?"}event=${encodeURIComponent(s)}`;
    const blatt = (eintrag, richtung, seite) => eintrag
      ? `<a class="blatt blatt--${seite}" href="${esc(nachbarUrl(eintrag.slug))}" rel="${seite === "links" ? "prev" : "next"}">
           <span class="blatt__richtung">${esc(richtung)}</span>
           <span class="blatt__titel">${seite === "links" ? "\u2039 " : ""}${esc(eintrag.title)}${seite === "rechts" ? " \u203a" : ""}</span>
         </a>`
      : `<span class="blatt blatt--${seite}"></span>`;
    const umblaettern = (frueher || spaeter)
      ? `<nav class="umblaettern" aria-label="${esc(t.alleTermine)}">
           ${blatt(frueher, t.frueher, "links")}
           ${blatt(spaeter, t.spaeter, "rechts")}
         </nav>`
      : "";

    const statusLabel = t.status[e.status];
    // PATCH Redaktion 2026-10-08: weitere Termine, Hinweis, Programm, Mitwirkende, Nachbericht, Fotos
    const L = (k) => t[k] || STRINGS[DEFAULT_LANG][k] || k;
    const tag = (iso) => { try { return new Intl.DateTimeFormat(t.locale, { timeZone: e.timeZone || "Europe/Vienna", weekday: "short", day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(iso)); } catch { return iso; } };
    const termine = Array.isArray(e.termine) && e.termine.length > 1
      ? `<h2 class="detail__h">${esc(L("weitereTermine"))}</h2><ul class="termine-liste">${e.termine.map((x) => {
          const st = t.status[x.status];
          const text = `${esc(tag(x.date))} · ${esc([x.venue, x.city].filter(Boolean).join(", "))}${st ? ` · <b>${esc(st)}</b>` : ""}`;
          return `<li class="${x.status === "cancelled" ? "weg" : ""}">${x.slug === e.slug ? `<b>${text}</b> <small>(${esc(L("dieserTermin"))})</small>` : `<a href="${esc(nachbarUrl(x.slug))}">${text}</a>`}</li>`;
        }).join("")}</ul>` : "";
    wrap.innerHTML = `
      ${e.image ? `<div class="detail__media"><img src="${e.image}" alt="" title="${esc(L("gross"))}"></div>
      <div class="lb" hidden role="dialog" aria-modal="true"><button type="button" aria-label="${esc(L("schliessen"))}">×</button><img src="${e.image}" alt=""></div>` : ""}
      <h1 class="detail__title">${esc(e.title)}</h1>
      <div class="detail__facts">
        <span>${fmtDate(e.date, e.timeZone, t.locale)}</span>
        ${e.doorsOpen ? `<span>${esc(L("einlass"))} ${esc(e.doorsOpen)}</span>` : ""}
        ${e.venue ? `<span>${esc(e.venue)}${e.city ? ", " + esc(e.city) : ""}</span>` : ""}
        ${e.price ? `<span>${esc(e.price)}</span>` : ""}
        ${statusLabel ? `<span class="pill">${statusLabel}${e.status === "postponed" && e.verschobenAuf ? ` – ${esc(L("verschobenAuf"))}: ${esc(tag(e.verschobenAuf))}` : ""}</span>` : ""}
        ${e.translated === false ? `<span class="pill pill--muted">${t.fallbackNote}</span>` : ""}
      </div>
      ${e.statusNote ? `<p class="hinweis">${esc(e.statusNote)}</p>` : ""}
      <div class="detail__body">${e.body || ""}</div>
      ${e.programm ? `<h2 class="detail__h">${esc(L("programm"))}</h2><div class="detail__body">${e.programm}</div>` : ""}
      ${Array.isArray(e.performers) && e.performers.length ? `<h2 class="detail__h">${esc(L("mitwirkende"))}</h2><p class="detail__body">${e.performers.map(esc).join(" · ")}</p>` : ""}
      ${termine}
      ${e.nachbericht ? `<h2 class="detail__h">${esc(L("nachbericht"))}</h2><div class="detail__body">${e.nachbericht}</div>` : ""}
      ${e.fotosUrl ? `<p><a class="btn" href="${esc(e.fotosUrl)}" target="_blank" rel="noopener">${esc(L("fotos"))}</a></p>` : ""}
      <div class="aktionen">
        ${e.ticketUrl ? `<a class="btn" href="${e.ticketUrl}" target="_blank" rel="noopener">${t.tickets}</a>` : ""}
        ${kalenderKnopf(e, t, feed, absolut(nachbarUrl(e.slug), location.href))}
      </div>
      ${umblaettern}
    `;
    // Grossansicht: Doppelklick (am Handy: Antippen); schliessen mit Klick, × oder Esc
    const bild = wrap.querySelector(".detail__media img"), lb = wrap.querySelector(".lb");
    if (bild && lb) {
      const auf = () => { lb.hidden = false; document.documentElement.style.overflow = "hidden"; lb.querySelector("button").focus(); };
      const zu = () => { lb.hidden = true; document.documentElement.style.overflow = ""; };
      bild.addEventListener("dblclick", auf);
      if (window.matchMedia && matchMedia("(pointer: coarse)").matches) bild.addEventListener("click", auf);
      lb.addEventListener("click", zu);
      lb.addEventListener("keydown", (ev) => { if (ev.key === "Escape") zu(); });
    }
  }
}

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

customElements.define("event-list", EventList);
customElements.define("event-detail", EventDetail);
