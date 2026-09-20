# Everbloom: Teams und Bewerbungen pflegen

Alle Spieler, Rollen, Profil-Links, Riot-IDs und offenen Stellen werden in `data/site.json` gepflegt. Keine HTML-Karten mehr kopieren.

## Spieler ändern

1. In GitHub `data/site.json` öffnen und den Stift wählen.
2. Unter `teams` das Team und den Spieler suchen.
3. `name` ist der sichtbare Name; `role` die Rolle; `image` der Dateiname des Bildes. `links` enthält beschriftete HTTPS-Links.
4. `riotName` und `riotTag` werden für die automatischen Rang-Abfragen verwendet. `id` muss eindeutig sein und sollte bei bestehenden Spielern unverändert bleiben.
5. Für neue Spieler einen vollständigen Eintrag kopieren, eine neue ID vergeben und die Daten ändern. Neue Bilder ebenfalls hochladen.
6. Änderung speichern. Die Aktion „Build team and recruitment pages“ erzeugt die Seiten neu. Das vorhandene Publishing muss die generierten HTML-Dateien veröffentlichen.

## Offene Rollen

Unter `openings` Titel, Beschreibung und `requirements` ändern. Mit `open: false` wird eine Anzeige ausgeblendet. `applicationUrl` steuert das vorhandene Google-Formular.

Aktueller Stand laut Lena: FLINTA-Coaches sind besetzt; Male Roster 2 hat drei freie Spielerplätze. Mindestalter, Mindestrang und Trainingszeiten sind nicht bestätigt und werden deshalb nicht erfunden.

## Lokal bauen

```sh
python scripts/build_content.py
python -m http.server 8080
```

Der Generator benötigt nur Python, keine zusätzlichen Pakete. `roster.html`, `join.html` und der Bewerbungs-Teaser in `index.html` werden daraus erstellt und funktionieren auch ohne JavaScript. `ranks.json` ergänzt die Rangdaten; das Rang-Update nutzt dieselben Spieler-IDs aus `site.json`.

## Veröffentlichung

Die Änderungen sind zunächst auf einem separaten Branch vorbereitet. Die bestehenden GitHub-Pages-Einstellungen müssen bei der Veröffentlichung geprüft werden: von `GITHUB_TOKEN` erzeugte Commits lösen nicht jeden Pages-Build automatisch aus. Bei einem manuellen Upload die generierten HTML-Dateien hochladen. CSS und JavaScript werden direkt eingebettet, weil der aktuelle Live-Host die neuen Asset-Pfade nicht zuverlässig ausliefert. Änderungen weiterhin zentral in `enhancements.css` und `enhancements.js` pflegen; der Generator übernimmt sie in alle fünf Seiten.

## Performance

Keine blockierende Splash-Seite oder permanenten Canvas-Animationen mehr auf Start- und Teamseite. Der X-Feed lädt erst nach Klick. Bilder unterhalb des Seitenanfangs werden verzögert geladen. Die mobile Navigation bietet direkten Zugang zu Bewerbungen.

Die nicht aktivierte KI-/Cloudflare-Konfiguration gehört nicht zu diesem Website-Update. Der vorhandene öffentliche Scrim-Webhook wurde nicht verändert; dessen separate Absicherung und Austausch stehen noch aus.

## Einheitliche Seiten

Die vom Nutzer eingefügten Versionen von Startseite, Roster, Bootcamp und Legal wurden als Grundlage übernommen. Alle fünf Seiten einschließlich Join verwenden dieselbe Navigation und einen persistenten Hell-/Dunkelmodus. Die Rechtstexte wurden inhaltlich nicht überarbeitet. Bootcamp verweist auf die drei bestätigten offenen Plätze in Male Roster 2.
