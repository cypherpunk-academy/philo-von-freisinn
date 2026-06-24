# Plandokument — Der soziale Dreiklang

**Produkt:** Der soziale Dreiklang  
**Untertitel:** Geist, Recht und Wirtschaft — Harmonie und Ungleichgewicht  
**Marke:** Philo von Freisinn  
**Slug:** `der-soziale-dreiklang`  
**Stand:** Arbeitsspezifikation  
**Stichworte:** Dreiklang, Dreigliederungs-Matrix, zwölf Felder, sozialer Organismus

---

## 1. Produktübersicht

*Der soziale Dreiklang* ordnet das Zusammenleben von Geist, Recht und Wirtschaft in **zwölf Felder**. Drei davon zeigen den harmonischen Zustand — nur als Grafik. Neun beschreiben Krankheitssymptome und Beispiele für Ungleichgewicht.

Das Werk erscheint in mehreren Ausdrucksformen aus **einer gemeinsamen Inhaltsquelle** (`content/fields.yaml`):

| Format | Verwendung |
|---|---|
| **A4** | Heft, Handreichung, Einzelblatt |
| **A2** | Wandkarte, Seminarraum |
| **A0** | Übersichtsplakat, Ausstellung |
| **Web** | Interaktive Karte, Vertiefung pro Feld |

---

## 2. Die zwölf Felder

### 2.1 Hauptmatrix (3×3)

Steiners sozialer Organismus hat drei Glieder mit je eigenem Prinzip. Krank wird er, sobald eine Sphäre nach den Mitteln einer anderen greift.

- **Zeilen** = von wo der Impuls ausgeht (die übergreifende Sphäre)
- **Spalten** = wohin der Übergriff landet (die befallene Sphäre)

| von ↓ \ auf → | Geistesleben | Rechtsleben (Politik) | Wirtschaftsleben |
|---|---|---|---|
| **Geistesleben** | *Freiheit* (Harmonie) | Übergriff 1 | Übergriff 2 |
| **Rechtsleben** | Übergriff 3 | *Gleichheit* (Harmonie) | Übergriff 4 |
| **Wirtschaftsleben** | Übergriff 6 | Übergriff 5 | *Brüderlichkeit* (Harmonie) |

**Diagonale (Felder 1–3):** Sphäre wirkt in sich selbst — der gesunde Zustand. Nur Klint-Motiv + Prinzipwort, keine Textschichten.

**Off-Diagonale (Felder 4–9):** die sechs Übergriffe — voller Inhalt (Titel, Korruption, Grundgedanke, Beispiele).

### 2.2 Drei Kombinationsfelder (Felder 10–12)

Ergänzend zur Matrix: Fälle, in denen **zwei Sphären gemeinsam** in die dritte greifen — verschärfte oder zusammengesetzte Pathologien.

| Kombination | Ziel-Sphäre | Feld-ID |
|---|---|---|
| Geist + Recht | → Wirtschaft | `kombination-geist-recht-wirtschaft` |
| Geist + Wirtschaft | → Recht | `kombination-geist-wirtschaft-recht` |
| Recht + Wirtschaft | → Geist | `kombination-recht-wirtschaft-geist` |

> Inhalt der Kombinationsfelder: noch auszuarbeiten (siehe `content/fields.yaml`, Status `draft`).

### 2.3 Übersicht aller zwölf Felder

| # | ID | Typ | Inhalt |
|---|---|---|---|
| 1 | `harmonie-geist` | Harmonie | Freiheit — nur Grafik |
| 2 | `harmonie-recht` | Harmonie | Gleichheit — nur Grafik |
| 3 | `harmonie-wirtschaft` | Harmonie | Brüderlichkeit — nur Grafik |
| 4 | `uebergriff-geist-recht` | Ungleichgewicht | Geist → Recht |
| 5 | `uebergriff-geist-wirtschaft` | Ungleichgewicht | Geist → Wirtschaft |
| 6 | `uebergriff-recht-geist` | Ungleichgewicht | Recht → Geist |
| 7 | `uebergriff-recht-wirtschaft` | Ungleichgewicht | Recht → Wirtschaft |
| 8 | `uebergriff-wirtschaft-recht` | Ungleichgewicht | Wirtschaft → Recht |
| 9 | `uebergriff-wirtschaft-geist` | Ungleichgewicht | Wirtschaft → Geist |
| 10 | `kombination-geist-recht-wirtschaft` | Ungleichgewicht | Geist + Recht → Wirtschaft |
| 11 | `kombination-geist-wirtschaft-recht` | Ungleichgewicht | Geist + Wirtschaft → Recht |
| 12 | `kombination-recht-wirtschaft-geist` | Ungleichgewicht | Recht + Wirtschaft → Geist |

**Optional — Schatten der Diagonale:** Jede Sphäre kann ihr eigenes Prinzip verraten, ohne schon in eine andere überzugreifen: Geist → Dogma, Recht → Willkür/Privileg, Wirtschaft → Gier/Ausbeutung. Das ist der *Impuls*, der zum Übergriff werden kann. Kann als zweite Zeile in den Harmonie-Feldern oder als eigene Annotation erscheinen — noch offen.

Die Matrix ist **inhaltsneutral**: sie diagnostiziert die strukturelle Bewegung, nicht die Weltanschauung.

---

## 3. Lesedistanz-Staffelung (Gestaltungsprinzip)

Jedes Ungleichgewichts-Feld trägt **vier Schichten**, gestaffelt nach Lesedistanz (skaliert je nach Format):

| Schicht | Lesedistanz (A0) | Inhalt | Länge | Schriftgröße A0 (ca.) |
|---|---|---|---|---|
| **1 Titel** | 3–5 m | Schlagzeile | 3–5 Wörter | 40–54 pt |
| **2 Korruption** | 2–3 m | verletztes Prinzip + Richtung | 3–5 Wörter | 28–34 pt |
| **3 Grundgedanke** | 1,5–2,5 m | Wesen des Übergriffs | ~30 Wörter / 2 Sätze | 22–28 pt |
| **4 Beispiele (2×)** | <1 m | Stichwort + ein Satz | je ~15–20 Wörter | 14–18 pt |

Haupttitel *Der soziale Dreiklang*: 120–160 pt (A0). Achsenbeschriftung: 48–60 pt.

So entsteht das „Hineinziehen": von weitem die Gestalt, dann der Gedanke, beim Herantreten die Konkretion. A4 und Web komprimieren die Schichten; A2 und A0 behalten die Staffelung.

---

## 4. Inhalt der sechs Übergriffe (Matrix, final)

### Übergriff 1 — Geist → Recht/Politik (`uebergriff-geist-recht`)
- **Titel:** Der Geist greift nach dem Staat
- **Korruption:** Glaube wird zu Gesetz · Theokratie
- **Grundgedanke:** Eine geistige Idee — ein Glaube, eine Weltanschauung — verlässt ihre freie Sphäre und macht sich zur Grundlage staatlicher Gewalt. Aus Überzeugung wird Zwang, aus Bekenntnis wird Recht.
- **Beispiel A — Religiöse Landnahme:** „Eretz Israel" als religiöse Begründung staatlicher Territorialansprüche; ebenso die Islamische Republik Iran.
- **Beispiel B — Herrschende Lüge:** Golf von Tonkin, irakische „Massenvernichtungswaffen" — die Presse wird zur Kriegslegitimation eingespannt.

### Übergriff 2 — Geist → Wirtschaft (`uebergriff-geist-wirtschaft`)
- **Titel:** Das Dogma diktiert den Markt
- **Korruption:** Lehre bestimmt Produktion
- **Grundgedanke:** Eine geistige Doktrin schreibt vor, was produziert, gehandelt und konsumiert werden darf — statt dass realer Bedarf und assoziative Vernunft den Ausschlag geben.
- **Beispiel A — Religiöse Wirtschaftsgebote:** Zinsverbot (Islamic Finance), Halal-/Koscher-Zertifizierung als Marktregime.
- **Beispiel B — Ideologische Planwirtschaft:** eine Weltanschauung bestimmt die Produktion statt des Bedarfs.

### Übergriff 3 — Recht/Politik → Geist (`uebergriff-recht-geist`)
- **Titel:** Der Staat beherrscht den Geist
- **Korruption:** Macht bestimmt Wahrheit
- **Grundgedanke:** Der Staat greift nach Religion, Bildung, Presse und Wissenschaft und schreibt vor, was geglaubt, gelehrt und gewusst werden darf. Die Freiheit des Geistes wird dem Zwang geopfert.
- **Beispiel A — Staatsreligion / Staatsatheismus:** verordneter Lehrplan, Pressezensur.
- **Beispiel B — Lyssenkoismus:** der Staat diktiert, was als wahr zu gelten hat.

### Übergriff 4 — Recht/Politik → Wirtschaft (`uebergriff-recht-wirtschaft`)
- **Titel:** Der Staat lenkt die Wirtschaft
- **Korruption:** Gewalt setzt Preise
- **Grundgedanke:** Staatliche Gewalt greift unmittelbar in Produktion, Preise und Handel ein, statt nur den Rechtsrahmen zu sichern, in dem die Wirtschaft sich selbst assoziativ ordnet.
- **Beispiel A — Planwirtschaft:** Verstaatlichung, staatliche Preisfestsetzung.
- **Beispiel B — Sanktionen & Zölle:** Handel als politische Waffe statt wirtschaftlicher Vernunft.

### Übergriff 5 — Wirtschaft → Recht/Politik (`uebergriff-wirtschaft-recht`)
- **Titel:** Das Geld kauft das Recht
- **Korruption:** Vorrecht wird Ware
- **Grundgedanke:** Wirtschaftliche Macht kauft sich Gesetze und Vorrechte. Was für alle gleich gelten sollte, wird käuflich — das Recht hört auf, Recht zu sein, und wird zur Ware.
- **Beispiel A — Lobbyismus & Parteienfinanzierung:** faktisch käufliche Gesetze.
- **Beispiel B — Vorrechte als Ware:** Golden Visa, Bodenrente/Miete, Patente.

### Übergriff 6 — Wirtschaft → Geist (`uebergriff-wirtschaft-geist`)
- **Titel:** Der Profit kauft die Wahrheit
- **Korruption:** Geld bestimmt Wissen
- **Grundgedanke:** Das Wirtschaftsleben kolonisiert Forschung, Bildung, Presse und Kultur. Erkenntnis und Aufmerksamkeit folgen nicht mehr der Wahrheit, sondern dem Profit.
- **Beispiel A — Gekaufte Forschung:** Tabak-, Zucker-, Pharma-Studien im Dienst des Auftraggebers.
- **Beispiel B — Aufmerksamkeitsökonomie:** werbefinanzierte Presse; Medien folgen dem Profit, nicht der Wahrheit.

### Diagonale — drei Harmonie-Felder
- **Geist in sich:** FREIHEIT
- **Recht in sich:** GLEICHHEIT
- **Wirtschaft in sich:** BRÜDERLICHKEIT

Nur Klint-Motiv + Prinzipwort (empfohlen — Ruhepunkte, zeigt das Ideal).

---

## 5. Visuelles System (Hilma af Klint)

Klints Formenvokabular: aufsteigende Spiralen, konzentrische Kreise, Mandalas, gespiegelte Symmetrien, botanisch-esoterische Diagramme, Buchstaben/Signets, Pastell + Gold.

**Eine Leitfarbe + ein Leitmotiv pro Sphäre:**

| Sphäre | Prinzip | Farbe (Vorschlag) | Klint-Motiv |
|---|---|---|---|
| Geistesleben | Freiheit | Blau/Violett + Gold | aufsteigende Spirale, Taube/Schwan |
| Rechtsleben | Gleichheit | Rosé/Grün | gespiegelte Symmetrie, Doppelform/Waage |
| Wirtschaftsleben | Brüderlichkeit | Ocker/Rot-Erdton | vernetzte Kreise, kreisende Ströme/Ketten |

**Übergriffs-Felder:** Hintergrund = die *zwei* beteiligten Sphären-Motive, die ineinandergreifen / kollidieren. Ein **Richtungspfeil** in der Leitfarbe der übergreifenden Sphäre macht die Richtung lesbar.

**Kombinationsfelder:** alle drei beteiligten Sphären-Motive; zwei Quellfarben greifen in die Ziel-Sphäre.

**Harmonie-Felder:** reines Einzel-Motiv der Sphäre, ruhig, ohne Pfeil.

---

## 6. Produktionsspezifikation

### Druck (A4 / A2 / A0)

| Format | Maße (mm) | Orientierung | Besonderheit |
|---|---|---|---|
| A4 | 210 × 297 | Hoch | Heft, komprimierte Schichten |
| A2 | 420 × 594 | Hoch | Mittlere Lesedistanz |
| A0 | 841 × 1189 | Hoch | Volle Lesedistanz-Staffelung |

- Auflösung Druck: 300 dpi, CMYK, Beschnitt 3–5 mm
- A0 Pixel: ~9933 × 14043 px
- Aufbau: Raster + Typografie als Vektor; Klint-Hintergründe als hochaufgelöste Raster
- Schrift: serifenbetont für Titel; Grotesk für Beispieltexte. Max. 2 Schriftfamilien
- Sprache: durchgehend Deutsch

### Web

- Interaktive 3×3-Matrix + drei Kombinationsfelder
- Klick auf Feld → alle vier Schichten + erweiterte Beispiele
- Responsive; Harmonie-Felder als reine Grafik mit Prinzipwort

---

## 7. Projektstruktur

```
products/der-soziale-dreiklang/
├── dreigliederungs-matrix-plan.md   ← dieses Dokument
├── README.md
├── content/
│   └── fields.yaml                  ← alle 12 Felder (Single Source of Truth)
├── print/
│   ├── a4/
│   ├── a2/
│   └── a0/
└── web/
```

---

## 8. Offene Entscheidungen

1. Kombinationsfelder 10–12: Inhalte und Beispiele ausarbeiten
2. Schatten-Zeile in Harmonie-Feldern: einbauen oder weglassen?
3. Layout Kombinationsfelder: unter der Matrix, seitlich, oder auf Web als eigene Ebene?
4. A0: Raster zentriert (mit Titel-/Fußzone) oder flächenfüllend?
5. Pfeil-Konvention: im Feld oder als Achsenbänder?
6. Quellenfußzeile / GA-Bezug (z. B. „Kernpunkte der sozialen Frage") ja/nein?
7. Leonardo-Prompts pro Sphäre ausarbeiten (Klint-Stil, Farbvorgabe)
8. Übergriff 1 — drittes Beispiel „erzwungene gesellschaftliche Ächtung ohne Verfahren" aufnehmen?
