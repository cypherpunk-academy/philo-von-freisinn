# Leonardo.ai — Soziale Gesundheit, Dreiecke (Hilma af Klint)

Init-Bild: `halbkreise-dreiecke.png` (nur die beiden Dreiecke, transparent).
Stilreferenz: Hilma af Klints *Altarpiece, No. 1* (Group X) — aufsteigendes Dreieck, warme linke Hälfte, kühle rechte Hälfte, goldene Mittelachse, horizontale Bänder, strahlende Kalotte an der Spitze.

Geometrie **nicht verändern**: zwei gleichseitige, nach oben zeigende Dreiecke untereinander, DIN-A2-Hochformat. Keine Schrift, keine Buchstaben, keine Zahlen, keine Diagramm-Pfeile.

---

## Einstellungen

| | |
|---|---|
| Modell | Phoenix 1.0 oder Flux Dev |
| Init / Image Guidance | `halbkreise-dreiecke.png` |
| Guidance Strength | Schritt 1: **0.55–0.65** (Form halten). Schritt 2: **0.70–0.80** (Dreiecke nicht verwischen) |
| Style Reference | Altarpiece-Bild, Strength **0.45–0.60** |
| Format | Portrait, möglichst nah an **2:3** bzw. Custom **4200×5940**, danach Upscale |
| Negative | text, letters, words, typography, watermark, photorealistic, photography, 3D render, busy pattern, high contrast noise, muddy dark background, faces, hands, crowds, gothic, horror, blood, neon, cyberpunk, sharp photographic detail |

---

## Schritt 1 — nur die Dreiecksecken füllen

Init-Bild hochladen. Umgebung **leer lassen** (transparent oder sehr helles Pergament, fast weiß).

```
Hilma af Klint Altarpiece style, tempera on paper, 1907, sacred geometry, flat painted color fields with visible brush texture, two large upward-pointing equilateral triangles stacked vertically on an empty pale field.

Keep the exact triangle outlines. Paint only the interiors, each triangle divided into three corner realms that meet softly toward the center, horizontal bands and a faint golden oval-column along the median, like Altarpiece No. 1.

UPPER triangle — social illness, a corrupted altarpiece:
apex corner (top): Vorrechte — privilege, hierarchy, closed ranks; small black inner triangle at the tip; dark gold, charcoal, hardened vertical steps, a crown that does not open
lower-left corner: Wettbewerb — competition; saturated peach to deep red, fractured circles that refuse to join, sharp competing rays
lower-right corner: Leere Worte — empty words; icy pale blue fading into hollow indigo, vacant rings, gold that has gone dull, speech without substance

LOWER triangle — social health, a living altarpiece:
apex corner (top): Gleichheit — equality; rose and soft green, mirrored symmetry, a calm balanced scale of two identical forms
lower-left corner: Brüderlichkeit — brotherhood; ochre, earth red, networked circles, circulating chains, warmth that shares
lower-right corner: Freiheit — freedom; luminous blue-violet with living gold, an ascending spiral, a pale swan or dove suggested only as geometry

No background painting yet. Empty space around the triangles remains blank. No text.
```

---

## Schritt 2 — Umgebung nur als Hauch

Ergebnis von Schritt 1 als neues Init-Bild. Strength höher, damit die gefüllten Dreiecke stehen bleiben. Umgebung **sehr hell**, fast pergamentweiß (`#f4f1ea`), damit später dunkle Schrift darauf lesbar bleibt.

```
Same two Hilma af Klint triangles unchanged. Now breathe a very faint atmosphere into the empty space around them, watercolor wash at 10 percent strength, parchment ground remaining light enough for dark serif text to stay perfectly readable, no dark masses, no busy ornament, no vignette.

Around the UPPER triangle only: Die Lüge — the Lie. A hint of double contours, a pale veil, false gold mist, slightly misaligned echoes of the triangle, smoke-thin, almost not there. Cool gray-lilac haze, never opaque.

Around the LOWER triangle only: Die Wahrhaftigkeit — Truthfulness. A hint of clear morning light, open air, a barely-there gold breath, quiet clarity, the opposite of the veil above. Warm cream and the faintest rose-gold, never opaque.

The two atmospheres meet softly in the middle band without a hard border. Keep all surrounding tones high-key, desaturated, low contrast. The triangles stay the only strong forms. No text, no symbols that could be read as letters.
```

---

## Ein Durchgang (falls nur eine Generation)

Wenn Leonardo nur einmal laufen soll — Image Guidance **0.50–0.58**:

```
Hilma af Klint Altarpiece No. 1 style, tempera, 1907, two stacked upward equilateral triangles, exact outlines preserved.

Upper triangle interior: corrupted altarpiece of privilege, competition, empty words — apex dark gold and black hierarchy, left warm fractured red of rivalry, right hollow pale blue of vacant speech, horizontal bands, dull gold median.

Lower triangle interior: living altarpiece of equality, brotherhood, freedom — apex rose-green mirrored balance, left ochre networked circles of sharing, right blue-violet and living gold ascending spiral, horizontal bands, luminous gold median.

Surroundings only a breath on pale parchment: a faint veil of the Lie around the upper triangle (double contour, gray-lilac mist); a faint clear light of Truthfulness around the lower triangle (open cream, rose-gold air). High-key, low contrast, dark text must remain readable on the ground. No letters, no words, no photorealism.
```

---

## Schritt 3 — A0-Hintergrund, 150 dpi, volle Fläche

Zielgröße nach Upscale: **4967 × 7022 px** (A0 = 841 × 1189 mm bei 150 dpi).
Leonardo kann das nicht nativ: **2:3 / Tall** erzeugen, dann Universal Upscaler auf **4967 × 7022** (2:3 ist etwas länger als DIN-A — auf A0-Höhe beschneiden, nicht stauchen).

Kein Init mit Dreiecken. Style Reference: die fertigen Dreiecke, Strength **0.25–0.40** (Farbklima + Ausstrahlung, nicht die Formen kopieren). Private Mode egal.

**Wichtig:** Im Prompt keine Wörter wie *text, heading, title, letters, type, print* — Leonardo malt sonst Schrift. Lesbarkeit nur über *high-key / pale / light ground* steuern. Ergebnis: reine Lasur, **absolut ohne Schrift**.

Helligkeit nirgends unter etwa **78–80 %**; Sättigung niedrig bis mittel, nie grell.

```
Abstract color field only, Hilma af Klint tempera wash, 1907, no objects, completely blank of writing, no typography, no glyphs, no calligraphy, full-bleed parchment sheet.

A tall empty ground the color of warm parchment #f4f1ea. No triangles, no circles, no lines, no symbols, no figures, no frame, no border, no ornament, no horizon, no focal object. Absolutely no writing of any kind.

Color plays outward from two invisible centers — one in the upper third, one in the lower third — as if two altarpieces were breathing pigment into the paper around them. Soft radial blooms, not rays: diluted tempera that thins as it travels toward the edges and toward the middle band where both climates meet.

Upper field: from the upper center, a quiet outward wash of cool gray-lilac, faded false gold, a touch of peach-ash and hollow indigo — veiled, slightly unsettled, never opaque. Strongest near the unseen center, almost parchment again at the margins.

Lower field: from the lower center, a quiet outward wash of cream, rose-gold, soft ochre and the faintest blue-violet air — clear, open, never opaque. Strongest near the unseen center, fading gently outward.

Middle band: both atmospheres dissolve into each other without a hard seam. Paper grain and gouache stain visible, painterly but restrained.

Atmosphere only. Medium presence of color — richer than a blank page, calmer than a finished painting. Low contrast, no dark masses, no vignette, no busy pattern. High-key pale ground throughout. Pure background wash — nothing to read.
```

**Negative:** text, letters, words, typography, writing, calligraphy, alphabet, numbers, glyphs, watermark, caption, label, title, heading, signage, triangle, circle, spiral, mandala, frame, border, ornament, figure, face, swan, crown, stairs, scales, geometry, diagram, vignette, dark corners, high saturation, neon, busy pattern, landscape, clouds, floral, photorealistic, 3D, focal object, loud color blocks, high contrast

---

## Schritt 3b — etwas kräftiger (wenn Schritt 3 zu blass wirkt)

Gleiche Einstellungen; Style Reference Strength eher **0.35–0.45**. Immer noch Lasur, aber spürbare Ausstrahlung von den (unsichtbaren) Dreieckszonen nach außen. Wieder: **keine Schrift im Prompt-Inhalt andeuten**.

```
Abstract Hilma af Klint tempera atmosphere on pale parchment #f4f1ea, tall full-bleed sheet, no objects whatsoever, completely blank of writing, no typography, no glyphs.

Two soft color hearts — upper third and lower third — radiate diluted pigment gently outward into the empty paper, like heat from altarpieces that are not drawn. No shapes: only climate. Absolutely no writing.

Upper breath: cool gray-lilac veil, dull gold mist, ash-peach and hollow blue, strongest near the upper heart, thinning toward edges. A little more body than a whisper, still translucent.

Lower breath: warm cream, living rose-gold, soft ochre and a hint of blue-violet clarity, strongest near the lower heart, thinning toward edges. Quiet glow, not spotlight.

They meet in the middle as a soft crossfade. Visible brush and paper tooth. High-key pale ground. Pure atmospheric wash only — nothing to read, no letters, no triangles, no ornaments.
```

**Negative:** same as Schritt 3

---

## Schritt 3 (alt — sehr blass, nur Referenz)

Frühere Minimal-Version, falls man wieder ganz zurück will:

```
Abstract color field only, Hilma af Klint tempera wash, 1907, no objects, completely blank of writing.

A tall sheet of pale parchment #f4f1ea, full bleed, empty of every shape. No triangles, no circles, no lines, no symbols, no figures, no frame, no border, no ornament, no horizon. Absolutely no writing.

Only the faintest large-scale climate: upper half a cooler gray-lilac breath, lower half a warmer cream and rose-gold breath, meeting as a soft gradient across the middle. Paper grain and gouache stain, almost not there.

High-key, low contrast, desaturated, even light. Quiet, empty, atmospheric — a background wash, never a picture. Nothing to read.
```

**Negative:** text, letters, words, typography, writing, calligraphy, alphabet, numbers, glyphs, watermark, caption, label, title, heading, signage, triangle, circle, spiral, mandala, frame, border, ornament, figure, face, swan, crown, stairs, scales, geometry, diagram, vignette, dark corners, high saturation, busy pattern, landscape, clouds, floral, photorealistic, 3D, focal object
