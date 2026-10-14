# theaterundmusik-site

Website des Talentevereins Theater und Musik des BG/BRG Stockerau – **www.theaterundmusik.at**.
Seit Oktober 2026 eigene statische Seite statt Wix (Projekt „Music Theater und Music“, Umzug-Doku in
`1! claude/05 Projekte/Music Theater und Music/Output/Theater-Umzug.md`).

- `public/` – fertige Seite, so wie sie Vercel ausliefert (kein Build-Schritt auf Vercel).
- `vercel.json` – saubere Adressen, Weiterleitungen aller alten Wix-Adressen (`/blank…`, `/post/…`), Cache.
- `src/` – Erzeuger: `build_site.py` + Texte (`posts.json`, `quotes.json`, `impressum.html`, `datenschutz.html`) + `assets/` (CSS, JS, Schriften lokal, cleebration-Credit).
- Bild-/Video-Originale: `theaterundmusik-medien.zip` im Drive-Projektordner (Output/2026 10 14 Wix-Export …).

## Neu erzeugen
```bash
unzip ".../theaterundmusik-medien.zip" -d /tmp/tum-medien
python3 -m pip install pillow
python3 src/build_site.py /tmp/tum-medien /tmp/tum-build   # Zielordner wird neu angelegt
rm -rf public && cp -r /tmp/tum-build/public public && cp /tmp/tum-build/vercel.json .
git add -A && git commit -m "Seite neu erzeugt" && git push   # Vercel veröffentlicht automatisch
```

Hosting: Vercel (Team „cleebration's projects“, Hobby – nicht-kommerziell). Mail der Domain bleibt bei Google.
