# theaterundmusik-site

Website des Talentevereins Theater und Musik des BG/BRG Stockerau – **www.theaterundmusik.at**.
Seit Oktober 2026 eigene statische Seite statt Wix (Projekt „Music Theater und Music“, Umzug-Doku in
`1! claude/05 Projekte/Music Theater und Music/Output/Theater-Umzug.md`).

- `public/` – fertige Seite. Einziger Build-Schritt auf Vercel: `node scripts/besetzung.mjs` (setzt die Besetzung in `/orchester` ein).
- `vercel.json` – saubere Adressen, Weiterleitungen aller alten Wix-Adressen (`/blank…`, `/post/…`), Cache.
- `src/site.json` – **die Produktionen** (eine je Schuljahr), aktuelle Produktion, Archivliste, alte Wix-Blogadressen.
- `src/` – Erzeuger `build_site.py`, Texte (`quotes.json`, `impressum.html`, `datenschutz.html`), `assets/` (CSS, JS, Schriften lokal, Hub-Module, cleebration-Credit).

## Termine, Blog, Fotos = cleebration-Hubs

Die Seite hat keine eigenen Inhalte dafür. Alles mit `sites: [theaterundmusik]`:

| Was | Hub | Zuordnung zur Produktion |
|---|---|---|
| Termine | cleebration-events-hub | Datum im Schuljahr (`from`/`to` in site.json) |
| Blog | cleebration-blog-hub | Schlagwort = Produktions-key, z. B. `graefin-mariza-2027` |
| Fotos | cleebration-gallery-hub | Galerie, z. B. `tum-2027-mariza` |

Eingeben über die Hub-Masken (`/admin/`) oder Claude im Projekt „Music Theater und Music“.

## Besetzung (`/orchester`)

Personen stehen in `src/data/besetzung.json` und werden in der **Redaktion** gepflegt
(Werkzeug „Besetzung“, wie das Ensemble beim LKO). Je Person: **Name** (Pflicht) · Instrument · Foto · Link · Text –
was leer ist, erscheint nicht. Gezeigt werden nur `aktiv: true`, nie löschen, nur ausschalten. Fotos: `public/img/personen/`.
Jeder Push (auch von der Redaktion) → Vercel baut `scripts/besetzung.mjs` → Seite in ca. 1 Minute aktuell.

## Neue Produktion (jedes Schuljahr)

1. `src/site.json`: neuen Eintrag **oben** in `productions`, `current` auf den neuen key.
2. Gallery-Hub: Galerie `tum-<Jahr>-<kurz>` in `galleries.config.js` + Auswahlliste in `public/admin/config.yml`.
3. Blog-Hub: Schlagwort in `tags.config.json`.
4. Seite neu erzeugen (unten), commit, push.
- Bild-/Video-Originale: `theaterundmusik-medien.zip` im Drive-Projektordner (Output/2026 10 14 Wix-Export …).

## Neu erzeugen
```bash
unzip ".../theaterundmusik-medien.zip" -d /tmp/tum-medien     # Drive: Output/2026 10 14 Wix-Export …
python3 -m pip install pillow
python3 src/build_site.py /tmp/tum-medien /tmp/tum-build      # Zielordner wird neu angelegt
rm -rf public && cp -r /tmp/tum-build/public public && cp /tmp/tum-build/vercel.json .
git add -A && git commit -m "Seite neu erzeugt" && git push   # Vercel veröffentlicht automatisch
```

Hosting: Vercel (Team „cleebration's projects“, Hobby – nicht-kommerziell). DNS bei Vercel, Mail der Domain bei Google.
