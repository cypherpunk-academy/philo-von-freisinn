# Einkaufsliste Commons — direkte Downloads

*Alle Links geprüft am 20. August 2026. Herunterladen kann ich sie hier nicht: die Sandbox darf nur GitHub, PyPI und npm erreichen. Das Skript unten läuft bei dir.*

## Direkt ladbar (PDF-Link geprüft)

| # | Titel | Lizenz | Direkter Link |
|---|-------|--------|---------------|
| 1 | Cox/Arnold/Villamayor-Tomás: A Review of Design Principles (2010) | CC BY-NC | https://www.ecologyandsociety.org/vol15/iss4/art38/ES-2010-3704.pdf |
| 2 | Anderies/Janssen: Sustaining the Commons v2.0 | CC BY-NC-ND 3.0 | https://sustainingthecommons.org/wp-content/uploads/2019/06/Sustaining-the-Commons-v2.0.pdf |
| 3 | Helfrich/Bollier: Frei, fair und lebendig (2019) | **CC BY-SA 4.0** | https://www.transcript-verlag.de/shopMedia/openaccess/pdf/oa9783839445303.pdf |
| 4 | Helfrich/Bollier/Böll: Die Welt der Commons (2015) | **CC BY-SA 3.0** | https://www.boell.de/sites/default/files/welt_der_commons.pdf |
| 5 | Ostrom: Nobelvortrag „Beyond Markets and States" (2009) | © Nobel Foundation | https://www.nobelprize.org/uploads/2018/06/ostrom_lecture.pdf |
| 6 | Ostrom: Folien zum Nobelvortrag | © Nobel Foundation | https://www.nobelprize.org/uploads/2018/06/ostrom-lecture-slides.pdf |

## Ein Klick nötig (Landing Page mit Download-Button)

| # | Titel | Lizenz | Seite |
|---|-------|--------|-------|
| 7 | Helfrich/Böll (Hg.): Commons — Für eine neue Politik jenseits von Markt und Staat (2012) | CC BY-SA 3.0 | https://www.transcript-open.de/isbn/2835 |
| 8 | Baggio et al.: Explaining success and failure in the commons (IJC 2016) | CC BY 4.0 | https://thecommonsjournal.org/articles/10.18352/ijc.634 |
| 9 | Stern: Design principles for global commons (IJC 2011) | CC BY 4.0 | https://thecommonsjournal.org/articles/10.18352/ijc.305 |

Bei transcript-open folgt der Direktlink immer dem Muster `shopMedia/openaccess/pdf/oa<eISBN ohne Bindestriche>.pdf` — falls du weitere Bände von dort holst, sparst du dir damit den Umweg.

## Kapitelweise statt am Stück

Für den RAG oft besser, weil die Chunk-Grenzen dann an Kapitelgrenzen liegen:

- **Frei, fair und lebendig**, Einzelkapitel als PDF: https://www.transcript-open.de/isbn/4530 — jedes Kapitel hat ein eigenes DOI (`10.14361/9783839445303-003` bis `-014`). Für dich am interessantesten: Kapitel 5 „Selbstorganisation durch Gleichrangige" (S. 113–154), Kapitel 6 „Sorgendes & selbstbestimmtes Wirtschaften" (S. 155–188) und Kapitel 9 „Commons im Staat" (S. 263–292) — das ist inhaltlich die Dreigliederungsfrage in Commons-Sprache.
- **Die Welt der Commons**, Essays einzeln als HTML: http://band2.dieweltdercommons.de/
- **Commons Band 1**, Essays einzeln als HTML: http://band1.dieweltdercommons.de/

## Skript

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR="${1:-bibliothek/commons}"
mkdir -p "$DIR"
cd "$DIR"

fetch () {  # fetch <url> <zieldatei>
  if [ -f "$2" ]; then echo "übersprungen: $2"; return; fi
  echo "lade: $2"
  curl -fL --retry 3 --retry-delay 2 -A "Mozilla/5.0" -o "$2" "$1" \
    || echo "FEHLGESCHLAGEN: $1"
}

fetch "https://www.ecologyandsociety.org/vol15/iss4/art38/ES-2010-3704.pdf" \
      "cox-2010-review-design-principles.pdf"

fetch "https://sustainingthecommons.org/wp-content/uploads/2019/06/Sustaining-the-Commons-v2.0.pdf" \
      "anderies-janssen-sustaining-the-commons-v2.pdf"

fetch "https://www.transcript-verlag.de/shopMedia/openaccess/pdf/oa9783839445303.pdf" \
      "helfrich-bollier-2019-frei-fair-lebendig.pdf"

fetch "https://www.boell.de/sites/default/files/welt_der_commons.pdf" \
      "helfrich-bollier-2015-welt-der-commons.pdf"

fetch "https://www.nobelprize.org/uploads/2018/06/ostrom_lecture.pdf" \
      "ostrom-2009-nobelvortrag.pdf"

fetch "https://www.nobelprize.org/uploads/2018/06/ostrom-lecture-slides.pdf" \
      "ostrom-2009-nobelvortrag-folien.pdf"

echo
echo "Fertig. Prüfen:"
ls -lh
```

Speichern als `commons-holen.sh`, dann `chmod +x commons-holen.sh && ./commons-holen.sh`.

Falls einer der Server einen leeren oder winzigen Treffer liefert (HTML-Fehlerseite statt PDF), zeigt `ls -lh` das sofort — alles unter 100 KB ist verdächtig.

## Text extrahieren

Für die Weiterverarbeitung in deiner Pipeline:

```bash
for f in *.pdf; do
  pdftotext -layout "$f" "${f%.pdf}.txt"
done
```

Bei den transcript-Bänden lohnt danach der Blick auf weiche Trennstriche — die kommen bei den PDFs aus dem Satzsystem gelegentlich als U+00AD durch, wie bei den GA-Bänden.

## Lizenzhinweis fürs Repository

Wenn du daraus etwas veröffentlichst: Die beiden Helfrich/Bollier-Bände stehen unter **CC BY-SA**. Ein daraus abgeleiteter eigenständiger Text müsste ebenfalls unter CC BY-SA stehen. Bei Cox (NC) und Anderies/Janssen (NC-ND) ist die kommerzielle Nutzung ausgeschlossen und bei ND zusätzlich die Bearbeitung — indexieren und zitieren ist in Ordnung, ein abgeleitetes Werk nicht. Der Nobelvortrag ist gar nicht offen lizenziert: lesen ja, weiterverbreiten nein.

Ich würde in `bibliothek/commons/` eine `LIZENZEN.md` mit genau dieser Tabelle ablegen, damit später klar bleibt, was woher stammt.
