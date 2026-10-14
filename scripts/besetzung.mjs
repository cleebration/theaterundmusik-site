/**
 * besetzung.mjs – füllt den Personen-Baustein der Seite /orchester aus src/data/besetzung.json.
 *
 * Gepflegt wird die Datei in der Redaktion (Werkzeug „Besetzung“), wie das Ensemble beim LKO.
 * Läuft bei jedem Vercel-Deploy (vercel.json → buildCommand) und lokal nach build_site.py.
 *
 * Je Person: name (Pflicht) · instrument · foto · link · text – alles andere optional.
 * Was leer ist, erscheint nicht. Gezeigt werden nur aktiv=true, sortiert nach reihenfolge, dann Name.
 * Mehrsprachige Felder dürfen { de: "…" } oder ein einfacher Text sein.
 *
 * Aufruf: node scripts/besetzung.mjs [public-Ordner]   (Standard: ./public)
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PUB = process.argv[2] || join(ROOT, "public");
const DATEN = join(ROOT, "src", "data", "besetzung.json");
const SEITE = join(PUB, "orchester.html");
const START = "<!-- besetzung:start -->", ENDE = "<!-- besetzung:end -->";

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ESC[c]);
export const text = (w) => (w == null ? "" : typeof w === "string" ? w : w.de ?? Object.values(w)[0] ?? "").trim();

/** Nur http(s)-Adressen und eigene Pfade (/img/…) sind erlaubt. */
export function sichereUrl(u) {
  const s = String(u ?? "").trim();
  if (!s) return "";
  if (/^\/(?!\/)[^\s"'<>]*$/.test(s)) return s;
  try { const x = new URL(s); return x.protocol === "https:" || x.protocol === "http:" ? x.href : ""; } catch { return ""; }
}

export function renderBesetzung(daten) {
  const leute = (daten?.personen || [])
    .filter((p) => p && p.aktiv !== false && text(p.name))
    .sort((a, b) => (Number(a.reihenfolge) || 0) - (Number(b.reihenfolge) || 0) || text(a.name).localeCompare(text(b.name), "de"));
  if (!leute.length) return "";
  const karten = leute.map((p) => {
    const name = esc(text(p.name));
    const link = sichereUrl(p.link);
    const foto = sichereUrl(p.foto);
    const inst = text(p.instrument);
    const absaetze = text(p.text).split(/\n\s*\n/).map((x) => x.trim()).filter(Boolean);
    const a = (inhalt) => (link ? `<a href="${esc(link)}" rel="noopener" target="_blank">${inhalt}</a>` : inhalt);
    return `<figure class="person${foto ? "" : " person--ohne-foto"}">` +
      (foto ? a(`<img src="${esc(foto)}" alt="${name}" loading="lazy" width="480" height="640">`) : "") +
      `<figcaption><strong>${a(name)}</strong>` +
      (inst ? `<span>${esc(inst)}</span>` : "") +
      absaetze.map((x) => `<p class="person__text">${esc(x).replace(/\n/g, "<br>")}</p>`).join("") +
      `</figcaption></figure>`;
  });
  return `<div class="people">${karten.join("")}</div>`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  if (!existsSync(SEITE)) { console.log("besetzung: keine orchester.html – nichts zu tun"); process.exit(0); }
  const html = readFileSync(SEITE, "utf8");
  const i = html.indexOf(START), j = html.indexOf(ENDE);
  if (i < 0 || j < i) { console.error("besetzung: Markierungen fehlen in orchester.html"); process.exit(1); }
  const daten = existsSync(DATEN) ? JSON.parse(readFileSync(DATEN, "utf8")) : { personen: [] };
  const neu = html.slice(0, i + START.length) + renderBesetzung(daten) + html.slice(j);
  writeFileSync(SEITE, neu);
  console.log(`besetzung: ${(daten.personen || []).filter((p) => p.aktiv !== false).length} Personen in orchester.html`);
}
