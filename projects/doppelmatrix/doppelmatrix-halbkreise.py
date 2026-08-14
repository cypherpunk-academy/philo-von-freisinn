#!/usr/bin/env python3
"""
Doppelmatrix — DIN-A2-Hochformat mit zwei Dreiecken untereinander.

  Obere Haelfte:  Krankheit
  Untere Haelfte: Gesundheit

Zusammenhang mit doppelmatrix-gesund-und-krank.yaml
-----------------------------------------
Die YAML ist die inhaltliche Quelle (9 Richtungsfelder x gesund/krank,
je 7 Aspekte mit schlagwort + schlagsatz bei den 6 Kantenfeldern;
Medianfelder 07–09 nur Titel/Label).

Halbkreis-Index (LABELS/RADIAL/BLOCKS)  <->  YAML
  Gesund / Krank:
    7  Geist -> Recht                dm-01g / dm-01k
    4  Geist -> Wirtschaft           dm-02g / dm-02k
    6  Recht -> Geist                dm-03g / dm-03k
    0  Recht -> Wirtschaft           dm-04g / dm-04k
    1  Wirtschaft -> Recht           dm-05g / dm-05k
    3  Wirtschaft -> Geist           dm-06g / dm-06k
    8  Geist + Recht -> Wirtschaft   dm-07g / dm-07k  (nur Label)
    5  Geist + Wirtschaft -> Recht   dm-08g / dm-08k  (nur Label)
    2  Recht + Wirtschaft -> Geist   dm-09g / dm-09k  (nur Label)

RADIAL und BLOCKS hier manuell spiegeln — kein YAML-Import.
Bei inhaltlichen Aenderungen zuerst die YAML, dann hier nachziehen,
danach dieses Script ausfuehren (schreibt doppelmatrix-halbkreise.svg).
A0 ruft build_a2() auf — beim Import wird nichts geschrieben.

Klint-Fuellungen (optional): doppelmatrix-dreieck-krankheit.png /
doppelmatrix-dreieck-gesundheit.png im selben Ordner werden in die
Dreiecksflaechen gelegt; fehlen sie, bleibt die graue Flaeche.
Hintergrund (optional): doppelmatrix-hintergrund.jpg fuellt die Seite
statt der Beige-Flaeche (DIN-A, z. B. A0-Zuschnitt).
"""
import math
import os

# ---------------------------------------------------------------- Seite (DIN A2 Hochformat)
# 1 SVG-Einheit = 0.1 mm  →  A2 = 420×594 mm = 4200×5940 Einheiten
PAGE_W = 4200.0
PAGE_H = 5940.0
PAGE_MARGIN = 80.0
HALF_GAP = 60.0              # Abstand zwischen Krankheits- und Gesundheits-Haelfte

MAIN_TITLE_LINES = [
    "Gesundheit und Krankheit",
    "des sozialen Zusammenlebens",
]
MAIN_TITLE_WIDTH_FRAC = 0.90  # Anteil der Seitenbreite (laengste Zeile)

# ---------------------------------------------------------------- Dreiecks-Parameter
SIDE   = 1400.0 * 1.15       # Seitenlaenge (+15%)
R      = 87.5                # Radius der Halbkreise
OFFSET = 240.0               # Aussenversatz der Eck-Halbkreise
MEDIAN_OFFSET = 340.0        # Aussenversatz der mittleren (Median-)Halbkreise
CORNER_T = 0.155             # Kantenanteil Eck-Halbkreise (kleiner = naeher an Ecke)
ROTATE_LABELS = False
LABEL_ARC_PAD = 10.0

BG         = "#f4f1ea"
# Kaum sichtbar: etwas dunkleres Beige, bleibt Hintergrund
SECTION_WATERMARK = "#ddd9ce"
TRI_FILL   = "#9b9b9b"
TRI_STROKE = "#6f6f6f"
_DIR = os.path.dirname(os.path.abspath(__file__))
TRI_IMAGE_KRANK = os.path.join(_DIR, "doppelmatrix-dreieck-krankheit.png")
TRI_IMAGE_GESUND = os.path.join(_DIR, "doppelmatrix-dreieck-gesundheit.png")
BG_IMAGE = os.path.join(_DIR, "doppelmatrix-hintergrund.jpg")
ARC_COLOR  = "#2b2b2b"
TXT_COLOR  = "#2b2b2b"
FONT       = "Georgia, 'Times New Roman', serif"
FONT_SIZE  = 18
LINE_H     = 22
BLOCK_FONT = 24
BLOCK_LH   = 34
BLOCK_PAD  = 60
BLOCK_PAD_LEFT = 28          # linke 7-Zeiler naeher an den Strahlen
BLOCK_PAD_RIGHT = 48
RAD_FONT   = 22
RAD_GAP    = 14
V_FONT_SIZE = 46
V_GAP      = 85
INNER_FONT = 70              # Leitprinzipien im Dreieck

BLOCK_NUDGE = {
    0: (0, -150),
    6: (0, -150),
}
# Feinschliff nach Zoom-Fit (Krankheit / Gesundheit), dx>0 rechts, dy>0 unten
BLOCK_FIT_NUDGE_KRANK = {}
BLOCK_FIT_NUDGE_GESUND = {}


# Beschriftung in der Reihenfolge:
# links oben / links unten / links Mitte(Median),
# unten links / unten rechts / unten Mitte,
# rechts oben / rechts unten / rechts Mitte
LABELS = [
    ["Recht \u2192", "Wirtschaft:",
     "Das Gesetz", "sichert den", "fairen Rahmen"],
    ["Wirtschaft \u2192", "Recht:",
     "Die Wirtschaft", "tr\u00e4gt den Staat"],
    ["Recht +", "Wirtschaft", "\u2192 Geist:",
     "Schutz und", "Versorgung", "befreien", "den Geist"],
    ["Wirtschaft \u2192", "Geist:",
     "Die Wirtschaft", "versorgt", "den Geist"],
    ["Geist \u2192", "Wirtschaft:",
     "F\u00e4higkeiten", "befruchten die", "Wirtschaft"],
    ["Geist +", "Wirtschaft", "\u2192 Recht:",
     "Einsicht und", "Mittel tragen", "den Staat"],
    ["Recht \u2192 Geist:",
     "Der Staat", "bewahrt die", "Freiheit des", "Einzelnen"],
    ["Geist \u2192 Recht:",
     "Sachkenntnis", "pr\u00e4gt das", "Recht"],
    ["Geist + Recht", "\u2192 Wirtschaft:",
     "Bildung und", "Rahmen", "erm\u00f6glichen", "das Wirtschaften"],
]

RADIAL = {
    7: ["Entfaltung", "Erfahrung", "Miturteil", "Verst\u00e4ndlichkeit",
        "Mitwirken", "Zutrauen", "Rechtssinn"],
    4: ["Bed\u00fcrfnisse", "Ideen", "Kapital", "Materialisierung",
        "\u00dcberblick", "Aufgaben", "Korrektur"],
    6: ["Freiheit", "Zugang", "Chancen", "Schenkung",
        "Offenheit", "Richten", "Mitreden"],
    0: ["Arbeit", "Boden", "Eigentum", "Vertrag",
        "Haftung", "Grenze", "Einspruch"],
    1: ["Ertrag", "Durchsetzung", "Sicherung", "Versorgung",
        "Lieferung", "Freistellung", "Enthaltung"],
    3: ["Unterhalt", "Werk- und Wirkungst\u00e4tten", "Verl\u00e4sslichkeit",
        "Gabe", "Verzicht", "Fr\u00fcchte", "Br\u00fcderlichkeit"],
}
RADIAL_REVERSE = False

LABEL_NUDGE = {
    6: (28, -88),
    4: (40, 40),
    3: (-40, 40),
}

BLOCKS = [
    (7, "right", [
        ("Entfaltung", "Jeder kann das werden, was in ihm steckt."),
        ("Erfahrung", "Gesetze aus Erfahrung \u2014 nicht aus Mehrheiten."),
        ("Miturteil", "Pr\u00fcfen, bevor es gilt."),
        ("Verst\u00e4ndlichkeit",
         "Gesetze muss jeder m\u00fcndige B\u00fcrger verstehen k\u00f6nnen."),
        ("Mitwirken", "Einsprechen, nachdem es gilt."),
        ("Zutrauen", "Richter aus Zutrauen \u2014 gew\u00e4hlt auf Zeit."),
        ("Rechtssinn", "Wer einsieht, braucht keinen Zwang."),
    ]),
    (4, "right", [
        ("Bed\u00fcrfnisse",
         "Das Bed\u00fcrfnis ist der Anfang \u2014 und kommt nicht aus der Wirtschaft."),
        ("Ideen", "Die Idee befeuert die Produktion \u2014 nicht Gewinn, nicht Zwang."),
        ("Kapital", "Kapital ist geronnener Geist."),
        ("Materialisierung",
         "Der Gedanke vermehrt sich beim Teilen \u2014 das Brot nicht."),
        ("\u00dcberblick", "Wer das Ganze \u00fcbersieht, arbeitet f\u00fcr andere."),
        ("Aufgaben",
         "F\u00e4higkeit trifft Aufgabe \u2014 besetzt nach K\u00f6nnen, "
         "nicht nach Rang oder Ausbildung."),
        ("Korrektur", "Pull Request statt Beschwerde \u2014 Kritik als Gabe."),
    ]),
    (6, "right", [
        ("Freiheit", "Niemand greift dir ins Denken."),
        ("Zugang", "Wissen ist Anspruch, nicht Gnade."),
        ("Chancen", "Gleicher Boden f\u00fcr jede Gabe."),
        ("Schenkung", "Die Wirtschaft gibt, ohne zu diktieren."),
        ("Offenheit", "Quelloffen, nicht blo\u00df auditierbar."),
        ("Richten", "Richten ohne Vorgabe."),
        ("Mitreden", "Kein Einwand geht verloren."),
    ]),
    (0, "left", [
        ("Arbeit", "Deine Arbeitskraft ist keine Ware."),
        ("Boden", "Die Trennlinie im Boden."),
        ("Eigentum", "Nutzen auf Zeit statt Besitz f\u00fcr immer."),
        ("Vertrag", "Das Recht bindet, ohne zu bestimmen."),
        ("Haftung", "Wer verursacht, tr\u00e4gt die Folgen."),
        ("Grenze", "Nicht alles ist k\u00e4uflich."),
        ("Einspruch", "Kein Missstand bleibt verborgen."),
    ]),
    (1, "left", [
        ("Ertrag", "Ohne Ertrag kein Rechtsstaat."),
        ("Durchsetzung", "Geltung braucht Werkzeuge."),
        ("Sicherung", "Die Wirtschaft f\u00fcllt, das Recht verteilt."),
        ("Versorgung", "Geld weist an \u2014 Brot tr\u00e4gt."),
        ("Lieferung", "Das Recht bestellt, die Wirtschaft liefert."),
        ("Freistellung", "Zeit ist die knappste Gabe."),
        ("Enthaltung", "Wer zahlt, bestimmt nicht."),
    ]),
    (3, "left", [
        ("Unterhalt", "Wer lehrt, muss essen."),
        ("Werk- und Wirkungst\u00e4tten",
         "Der Geist braucht Dach und Werkzeug."),
        ("Verl\u00e4sslichkeit",
         "Getragen wird in Jahren, nicht in Stunden."),
        ("Gabe", "Geben, ohne zu bestellen."),
        ("Verzicht", "Wer bestellt, bekommt nur Bestelltes."),
        ("Fr\u00fcchte", "Die Ernte \u00fcbertrifft die Bestellung."),
        ("Br\u00fcderlichkeit", "Wer versteht, braucht keine Rechnung."),
    ]),
]

# ---------------------------------------------------------------- Krankheit (dm-…k)
# Index = gleiche Halbkreis-Position wie Gesund.
LABELS_KRANK = {
    0: ["Recht \u2192", "Wirtschaft:",
        "Die Gewalt", "setzt den", "Preis"],
    1: ["Wirtschaft \u2192", "Recht:",
        "Das Geld", "kauft das", "Recht"],
    2: ["Recht +", "Wirtschaft", "\u2192 Geist:",
        "Macht und", "Geld formen", "den Geist"],
    3: ["Wirtschaft \u2192", "Geist:",
        "Der Profit", "kauft die", "Wahrheit"],
    4: ["Geist \u2192", "Wirtschaft:",
        "Das Dogma", "diktiert die", "Produktion"],
    5: ["Geist +", "Wirtschaft", "\u2192 Recht:",
        "Lehre und", "Kapital schreiben", "das Gesetz"],
    6: ["Recht \u2192 Geist:",
        "Die Macht", "beherrscht", "den Geist"],
    7: ["Geist \u2192 Recht:",
        "Ideologie", "macht sich", "zum Gesetz"],
    8: ["Geist + Recht", "\u2192 Wirtschaft:",
        "Idee und Staat", "befehlen der", "Produktion"],
}
RADIAL_KRANK = {
    7: ["Vorschrift", "Machtgesetz", "Scheinpr\u00fcfung", "Verklausulierung",
        "Abweisung", "Expertokratie", "Desinformation"],      # Geist -> Recht
    4: ["Verf\u00fchrung", "Dogma", "Erz\u00e4hlung", "Entgrenzung",
        "Kennzahl", "Vermarktung", "Verk\u00fcmmerung"],       # Geist -> Wirtschaft
    6: ["Verordnung", "Vorenthaltung", "Vermessung", "Zuteilung",
        "Verriegelung", "Zulassung", "Dienstweg"],            # Recht -> Geist
    0: ["Konzession", "Spekulation", "Papiermacht", "Vorrechte",
        "Zwangsabgabe", "Zollwaffe", "Verschleierung"],       # Recht -> Wirtschaft
    1: ["Erpressung", "L\u00e4hmung", "Schutzabbau", "Bestechung",
        "Privatjustiz", "Dreht\u00fcr", "Lobbykauf"],          # Wirtschaft -> Recht
    3: ["Zulieferung", "Dunkelkammer", "Kalk\u00fcl", "R\u00fcckkauf",
        "Bestellung", "Einz\u00e4unung", "Berechnung"],       # Wirtschaft -> Geist
}
BLOCKS_KRANK = [
    (7, "right", [
        ("Vorschrift", "Jeder soll denken, was ihm vorgedacht wird."),
        ("Machtgesetz", "Gesetze aus Macht \u2014 nicht aus Sachkenntnis."),
        ("Scheinpr\u00fcfung", "Gepr\u00fcft wird nur, was bestehen soll."),
        ("Verklausulierung",
         "Gesetze, die keiner versteht."),
        ("Abweisung", "Der Einwand kostet \u2014 die Korrektur entf\u00e4llt."),
        ("Expertokratie", "Experten entscheiden \u2014 B\u00fcrger schauen zu."),
        ("Desinformation", "Macht, als Wahrheit verkleidet."),
    ]),
    (4, "right", [
        ("Verf\u00fchrung",
         "Das Bed\u00fcrfnis wird gemacht \u2014 von dem, der es f\u00fcllt."),
        ("Dogma", "Das Dogma diktiert \u2014 die Sache schweigt."),
        ("Erz\u00e4hlung", "Kapital ist geronnener Glaube."),
        ("Entgrenzung",
         "Gerechnet wird, als vermehrte sich das Brot."),
        ("Kennzahl",
         "Wer die Zahl sieht, sieht die Sache nicht mehr."),
        ("Vermarktung", "Besetzt wird nach Auftritt, nicht nach K\u00f6nnen."),
        ("Verk\u00fcmmerung",
         "Wer Bed\u00fcrfnisse macht, erkennt keine mehr."),
    ]),
    (6, "right", [
        ("Verordnung", "Der Plan greift dir ins Denken."),
        ("Vorenthaltung", "Wissen ist Entgegenkommen \u2014 kein Anspruch."),
        ("Vermessung", "Gleiche Raster f\u00fcr verschiedene Menschen."),
        ("Zuteilung", "Wer zahlt, bestimmt."),
        ("Verriegelung",
         "Der Einzelne wird gl\u00e4sern \u2014 der Apparat bleibt zu."),
        ("Zulassung", "Die Akte entscheidet \u2014 nicht der Mensch."),
        ("Dienstweg", "Jeder Einwand versandet."),
    ]),
    (0, "left", [
        ("Konzession", "Arbeiten darf, wem es erlaubt wird."),
        ("Spekulation",
         "Wer wohnen muss, zahlt, was der Hortende verlangt."),
        ("Papiermacht", "Papier verf\u00fcgt \u2014 K\u00f6nnen geht leer aus."),
        ("Vorrechte", "Das Recht bestimmt, wer gewinnt."),
        ("Zwangsabgabe",
         "Bezahlt wird, was festgesetzt ist \u2014 nicht, was geschieht."),
        ("Zollwaffe", "Der Handel wird zur Geisel."),
        ("Verschleierung",
         "Vor Gericht steht eine Konstruktion \u2014 kein Mensch."),
    ]),
    (1, "left", [
        ("Erpressung", "Das Fundament droht dem Haus."),
        ("L\u00e4hmung", "Zu gro\u00df, um belangt zu werden."),
        ("Schutzabbau",
         "Der Schutz f\u00e4llt, damit die Rendite steht."),
        ("Bestechung", "Die Lieferung wird zur Anweisung."),
        ("Privatjustiz",
         "Die Wirtschaft liefert das Urteil gleich mit."),
        ("Dreht\u00fcr",
         "Die Zeit ist frei \u2014 das Urteil ist es nicht."),
        ("Lobbykauf", "Wer zahlt, bestimmt doch."),
    ]),
    (3, "left", [
        ("Zulieferung", "Wer lehrt, muss liefern."),
        ("Dunkelkammer", "Das Dach wird zum Deckel."),
        ("Kalk\u00fcl",
         "Gerechnet wird in Quartalen, nicht in Jahren."),
        ("R\u00fcckkauf", "Aus der Gabe wird eine Rechnung."),
        ("Bestellung",
         "Bestellt wird die Frage \u2014 und die Antwort dazu."),
        ("Einz\u00e4unung",
         "Wer den Zaun besitzt, hat den Baum nicht gepflanzt."),
        ("Berechnung",
         "Gerechnet wird mit dem Menschen, nicht f\u00fcr ihn."),
    ]),
]
LABEL_NUDGE_KRANK = {
    6: (28, -88),
    4: (40, 40),
    3: (-40, 40),
}
BLOCK_NUDGE_KRANK = {
    0: (0, -150),
    6: (0, -150),
}

VERTEX_LABELS = ["Recht", "Wirtschaft", "Kultur/Geist"]

# Leitprinzipien im Inneren (Wirtschaft, Kultur/Geist, Recht)
INNER_KRANK = ("Wettbewerb", "Leere Worte", "Vorrechte")
INNER_GESUND = ("Br\u00fcderlichkeit", "Freiheit", "Gleichheit")
INNER_BASE_FRAC = 0.20       # Abstand von der Grundlinie (Anteil der Hoehe)
INNER_EDGE_PAD = 70.0        # Abstand Textkante \u2192 Dreiecksschenkel
INNER_LEG_T = 0.52           # Position auf dem linken Schenkel (0 = Spitze)
INNER_LEG_INSET = 48.0       # Versatz vom linken Schenkel nach innen
# Vorrechte / Wettbewerb (Krankheit): 2× Schrift, aussen an der Kante
VORRECHTE_SCALE = 2.0
VORRECHTE_LEG_T = 0.06       # Anker nahe Spitze (Anteil Kante Spitze→Wirtschaft)
VORRECHTE_INSET_FRAC = 0.0   # Baseline auf der Aussenkante; Buchstaben nach aussen
WETTBEWERB_LEG_T = 0.06      # Anker nahe Wirtschaft (Anteil Kante Wirtschaft→Geist)
LEERE_WORTE_LEG_T = 0.06     # Anker nahe Kultur/Geist (Anteil Kante Geist→Recht)
# Krankheit, Boegen 0+1: CSS-Zoom, dann senkrecht nach aussen
ARC_ZOOM = 1.5               # wieder 15% kleiner als zuletzt (1.725)
ARC_CLEAR_PAD = 40.0         # Abstand Strahlen zu Vorrechte / Wettbewerb

# ---------------------------------------------------------------- Geometrie-Helfer
def sub(p, q):  return (p[0] - q[0], p[1] - q[1])
def add(p, q):  return (p[0] + q[0], p[1] + q[1])
def mul(p, s):  return (p[0] * s, p[1] * s)
def norm(p):
    l = math.hypot(*p)
    return (p[0] / l, p[1] / l)
def cross(p, q): return p[0] * q[1] - p[1] * q[0]


def triangle_vertices(apex, side):
    h = side * math.sqrt(3) / 2
    a = apex
    b = (apex[0] - side / 2, apex[1] + h)
    c = (apex[0] + side / 2, apex[1] + h)
    centroid = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3)
    return a, b, c, centroid


def build_arcs(a, b, c, centroid):
    """9 Halbkreise: (center, chord, bulge, outward_n, offset)."""
    arcs = []
    for P0, P1 in ((a, b), (b, c), (a, c)):
        u = norm(sub(P1, P0))
        M = add(P0, mul(u, SIDE / 2))
        n = (u[1], -u[0])
        if (sub(M, centroid)[0] * n[0] + sub(M, centroid)[1] * n[1]) < 0:
            n = (-n[0], -n[1])
        arcs.append((add(P0, mul(u, SIDE * CORNER_T)), n, mul(u, -1), n, OFFSET))
        arcs.append((add(P0, mul(u, SIDE * (1.0 - CORNER_T))), n, u, n, OFFSET))
        arcs.append((M, u, n, n, MEDIAN_OFFSET))
    return arcs


def arc_path(center, chord, bulge, offset, n):
    c = add(center, mul(n, offset))
    start = add(c, mul(chord, R))
    end = sub(c, mul(chord, R))
    sweep = 1 if cross(chord, bulge) > 0 else 0
    return (f"M {start[0]:.2f} {start[1]:.2f} "
            f"A {R:.2f} {R:.2f} 0 0 {sweep} {end[0]:.2f} {end[1]:.2f}")


def arc_points(center, chord, bulge, offset, n, steps=48):
    c = add(center, mul(n, offset))
    pts = []
    for i in range(steps + 1):
        t = math.pi * i / steps
        d = add(mul(chord, math.cos(t)), mul(bulge, math.sin(t)))
        pts.append(add(c, mul(d, R)))
    return pts


def text_w(t, size, bold=False):
    return (0.58 if bold else 0.52) * size * len(t)


def label_pos(center, chord, bulge, offset, n, lines, centroid):
    if isinstance(lines, str):
        lines = [lines]
    nlines = len(lines)
    c = add(center, mul(n, offset))

    if ROTATE_LABELS:
        ang = math.degrees(math.atan2(chord[1], chord[0]))
        if ang > 90 or ang <= -90:
            ang += 180
        a = math.radians(ang)
        local_x = (math.cos(a), math.sin(a))
        local_y = (-local_x[1], local_x[0])
        depth = (R - (nlines - 1) * LINE_H) / 2
        step = 1 if (local_y[0] * bulge[0] + local_y[1] * bulge[1]) > 0 else -1
        if step < 0:
            depth += (nlines - 1) * LINE_H
        return add(c, mul(bulge, depth)), ang

    ang = 0.0
    half_h = (nlines - 1) * LINE_H / 2.0 + FONT_SIZE * 0.35
    half_w = max((text_w(t, FONT_SIZE, bold=True) for t in lines), default=20) / 2.0
    limit = R - LABEL_ARC_PAD

    def hits_arc(mid):
        for sx in (-half_w, 0.0, half_w):
            for sy in (-half_h, 0.0, half_h):
                p = (mid[0] + sx, mid[1] + sy)
                v = sub(p, c)
                if v[0] * bulge[0] + v[1] * bulge[1] < -1e-6:
                    continue
                if math.hypot(v[0], v[1]) > limit:
                    return True
        return False

    toward = norm(add(norm(sub(centroid, c)), mul(bulge, -0.35)))
    mid = c
    if hits_arc(mid):
        lo, hi = 0.0, R + half_w + half_h
        for _ in range(24):
            mid_shift = (lo + hi) / 2
            cand = add(c, mul(toward, mid_shift))
            if hits_arc(cand):
                lo = mid_shift
            else:
                hi = mid_shift
        mid = add(c, mul(toward, hi))

    first = (mid[0], mid[1] - (nlines - 1) * LINE_H / 2.0)
    return first, ang


def radial_items(center, chord, bulge, offset, n, words):
    c = add(center, mul(n, offset))
    items = []
    k = len(words)
    seq = list(reversed(words)) if RADIAL_REVERSE else list(words)
    for i, w in enumerate(seq):
        t = math.pi * i / (k - 1)
        d = norm(add(mul(chord, math.cos(t)), mul(bulge, math.sin(t))))
        anchor_pt = add(c, mul(d, R + RAD_GAP))
        ang = math.degrees(math.atan2(d[1], d[0]))
        if -90 < ang <= 90:
            items.append((anchor_pt, ang, "start", w, d))
        else:
            items.append((anchor_pt, ang + 180, "end", w, d))
    return items


def line_w(word, satz):
    return (text_w(word + ": ", BLOCK_FONT)
            + text_w(satz, BLOCK_FONT, bold=True))


def vertex_items(a, b, c, centroid):
    items = []
    for V, txt in zip((a, b, c), VERTEX_LABELS):
        d = norm(sub(V, centroid))
        items.append((add(V, mul(d, V_GAP)), txt))
    return items


def inner_labels(a, b, c, words, recht_style=None, wirtschaft_style=None,
                 geist_style=None):
    """Leitprinzipien im Dreieck: (Wirtschaft, Kultur/Geist, Recht).

    a = Recht (Spitze), b = Wirtschaft (unten links),
    c = Kultur/Geist (unten rechts).
    Waagerechte Worte sitzen an der Grundlinie bei Wirtschaft bzw. Geist,
    sofern kein wirtschaft_style / geist_style die Aussenkante setzt.
    Das Rechts-Wort steht auf dem linken Schenkel, nach oben lesbar.

    Returns list of (pos, ang, txt, font_size, anchor, baseline).
    """
    w_txt, g_txt, r_txt = words
    h = b[1] - a[1]
    t_down = 1.0 - INNER_BASE_FRAC
    y = a[1] + h * t_down
    half_w = (c[0] - a[0]) * t_down
    cx = a[0]
    centroid = ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0)

    def horiz(txt, sign):
        half_tw = text_w(txt, INNER_FONT, bold=True) / 2.0
        edge_x = cx + sign * half_w
        x = edge_x - sign * (INNER_EDGE_PAD + half_tw)
        return ((x, y), 0.0, txt, INNER_FONT, "middle", "central")

    def edge_item(P0, P1, txt, style, ang_vec, default_anchor, default_base):
        scale = style.get("scale", 1.0)
        font = INNER_FONT * scale
        t = style.get("leg_t", INNER_LEG_T)
        inset_frac = style.get("inset_frac", None)
        inset = INNER_LEG_INSET if inset_frac is None else font * inset_frac
        u = sub(P1, P0)
        edge_pt = add(P0, mul(u, t))
        n = norm((u[1], -u[0]))
        to_c = sub(centroid, edge_pt)
        if to_c[0] * n[0] + to_c[1] * n[1] < 0:
            n = (-n[0], -n[1])
        if style.get("outward"):
            n = (-n[0], -n[1])
        pos = add(edge_pt, mul(n, inset))
        # rsvg ignoriert text-before-edge oft: Buchstaben unter die Grundkante
        # schieben, wenn die Schrift waagerecht aussen an der Basis sitzt.
        if style.get("drop_below"):
            pos = (pos[0], pos[1] + font * 0.78)
        ang = math.degrees(math.atan2(ang_vec[1], ang_vec[0]))
        return (pos, ang, txt, font,
                style.get("anchor", default_anchor),
                style.get("baseline", default_base))

    if wirtschaft_style:
        w_item = edge_item(
            b, c, w_txt, wirtschaft_style, sub(c, b),
            "start", "text-before-edge")
    else:
        w_item = horiz(w_txt, -1.0)

    if geist_style:
        # Rechter Schenkel: Ende an Kultur/Geist, nach oben zum Recht lesbar
        # (Wortende an c, Text erstreckt sich zur Spitze).
        g_item = edge_item(
            c, a, g_txt, geist_style, sub(c, a),
            "end", "alphabetic")
    else:
        g_item = horiz(g_txt, 1.0)

    rs = recht_style or {}
    r_item = edge_item(
        a, b, r_txt, rs if recht_style else {
            "scale": 1.0, "leg_t": INNER_LEG_T, "outward": False,
        },
        sub(a, b), "middle", "central")

    return [
        w_item,
        g_item,
        r_item,
    ]


def panel_extent(arcs, radial_by_arc, block_items, verts, a, b, c):
    xs, ys = [a[0], b[0], c[0]], [a[1], b[1], c[1]]
    for item in block_items:
        if len(item) == 5:
            _idx, bx, by, w_, t_ = item
        else:
            bx, by, w_, t_ = item
        xs += [bx, bx + line_w(w_, t_)]
        ys += [by - BLOCK_FONT, by + BLOCK_FONT]
    for items in radial_by_arc.values():
        for (px, py), _a, _an, word, d in items:
            wlen = text_w(word, RAD_FONT, bold=True)
            end = add((px, py), mul(d, wlen))
            xs += [px, end[0]]
            ys += [py - RAD_FONT, py + RAD_FONT, end[1] - RAD_FONT, end[1] + RAD_FONT]
    for (px, py), txt in verts:
        hw = 0.30 * V_FONT_SIZE * len(txt)
        xs += [px - hw, px + hw]
        ys += [py - V_FONT_SIZE * 0.7, py + V_FONT_SIZE * 0.7]
    for arc in arcs:
        center, chord, bulge, n, off = arc
        for p in arc_points(center, chord, bulge, off, n):
            xs.append(p[0]); ys.append(p[1])
    return min(xs), max(xs), min(ys), max(ys)


def translate_point(p, dx, dy):
    return (p[0] + dx, p[1] + dy)


def translate_arc(arc, dx, dy):
    center, chord, bulge, n, off = arc
    return (translate_point(center, dx, dy), chord, bulge, n, off)


# ---------------------------------------------------------------- Panel bauen
def build_panel_content(arcs, centroid, labels, radial, blocks,
                        label_nudge=None, block_nudge=None):
    """Labels, Strahlen, Bloecke fuer eine Haelfte.

    labels: Liste (alle 9) oder Dict {idx: lines}.
    """
    label_nudge = label_nudge or {}
    block_nudge = block_nudge or {}

    radial_by_arc = {}
    radial_all = []
    for idx, words in radial.items():
        center, chord, bulge, n, off = arcs[idx]
        items = radial_items(center, chord, bulge, off, n, words)
        radial_by_arc[idx] = items
        radial_all.extend((idx,) + item for item in items)

    def arc_extent(idx):
        center, chord, bulge, n, off = arcs[idx]
        ex, ey = [], []
        for pt in arc_points(center, chord, bulge, off, n):
            ex.append(pt[0]); ey.append(pt[1])
        for (px, py), _a, _an, word, d in radial_by_arc.get(idx, []):
            e = add((px, py), mul(d, text_w(word, RAD_FONT, bold=True)))
            ex += [px, e[0]]; ey += [py - RAD_FONT, py + RAD_FONT,
                                     e[1] - RAD_FONT, e[1] + RAD_FONT]
        return min(ex), max(ex), min(ey), max(ey)

    block_placements = {}
    for idx, side, items in blocks:
        center, chord, bulge, n, off = arcs[idx]
        c = add(center, mul(n, off))
        x0, x1, y0, y1 = arc_extent(idx)
        widths = [line_w(w, t) for w, t in items]
        if side == "right":
            bx = x1 + BLOCK_PAD_RIGHT
            by = c[1] - (len(items) - 1) * BLOCK_LH / 2
        elif side == "left":
            bx = x0 - BLOCK_PAD_LEFT - max(widths)
            by = c[1] - (len(items) - 1) * BLOCK_LH / 2
        else:
            bx = x0
            by = y1 + BLOCK_PAD
        ndx, ndy = block_nudge.get(idx, (0.0, 0.0))
        block_placements[idx] = (bx + ndx, by + ndy, items)

    block_items = []
    for idx, (bx, by, items) in block_placements.items():
        for i, (w, t) in enumerate(items):
            block_items.append((idx, bx, by + i * BLOCK_LH, w, t))

    if isinstance(labels, dict):
        label_iter = sorted(labels.items())
    else:
        label_iter = list(enumerate(labels))

    label_items = []
    for idx, lines in label_iter:
        if isinstance(lines, str):
            lines = [lines]
        center, chord, bulge, n, off = arcs[idx]
        (px, py), ang = label_pos(center, chord, bulge, off, n, lines, centroid)
        dx, dy = label_nudge.get(idx, (0.0, 0.0))
        label_items.append((idx, px + dx, py + dy, ang, lines))

    return label_items, radial_all, radial_by_arc, block_items


def render_panel(out, gid, a, b, c, arcs, verts,
                 label_items=None, radial_all=None, block_items=None,
                 inner_items=None, arc_zoom=None, fill_image=None):
    """arc_zoom: {idx: (origin, zoom, (shift_x, shift_y))} CSS-Zoom + Verschiebung."""
    arc_zoom = arc_zoom or {}
    label_items = label_items or []
    radial_all = radial_all or []

    def zoom_attr(idx):
        spec = arc_zoom.get(idx)
        if not spec:
            return None
        (ox, oy), z, (sx, sy) = spec
        return (f'transform="translate({sx:.2f},{sy:.2f}) '
                f'translate({ox:.2f},{oy:.2f}) scale({z}) '
                f'translate({-ox:.2f},{-oy:.2f})"')

    out.append(f'  <g id="{gid}">')
    pts = f"{a[0]:.2f},{a[1]:.2f} {b[0]:.2f},{b[1]:.2f} {c[0]:.2f},{c[1]:.2f}"
    if fill_image:
        xmin = min(a[0], b[0], c[0])
        xmax = max(a[0], b[0], c[0])
        ymin = min(a[1], b[1], c[1])
        ymax = max(a[1], b[1], c[1])
        clip_id = f"clip-{gid}"
        href = os.path.basename(fill_image)
        out.append(f'    <clipPath id="{clip_id}">')
        out.append(f'      <polygon points="{pts}"/>')
        out.append(f'    </clipPath>')
        out.append(
            f'    <image href="{href}" xlink:href="{href}" '
            f'x="{xmin:.2f}" y="{ymin:.2f}" '
            f'width="{xmax - xmin:.2f}" height="{ymax - ymin:.2f}" '
            f'preserveAspectRatio="none" clip-path="url(#{clip_id})"/>'
        )
        out.append(
            f'    <polygon points="{pts}" fill="none" stroke="{TRI_STROKE}" '
            f'stroke-width="3"/>'
        )
    else:
        out.append(
            f'    <polygon points="{pts}" fill="{TRI_FILL}" stroke="{TRI_STROKE}" '
            f'stroke-width="3"/>'
        )

    if inner_items:
        out.append(f'    <g font-family="{FONT}" font-weight="bold" '
                   f'fill="{TXT_COLOR}" dominant-baseline="central" '
                   f'letter-spacing="1">')
        for item in inner_items:
            (px, py), ang, txt = item[0], item[1], item[2]
            size = item[3] if len(item) > 3 else INNER_FONT
            anch = item[4] if len(item) > 4 else "middle"
            base = item[5] if len(item) > 5 else "central"
            out.append(f'      <text x="0" y="0" text-anchor="{anch}" '
                       f'dominant-baseline="{base}" font-size="{size}" '
                       f'transform="translate({px:.2f},{py:.2f}) '
                       f'rotate({ang:.2f})">{txt}</text>')
        out.append('    </g>')

    out.append(f'    <g fill="none" stroke="{ARC_COLOR}" stroke-width="5" '
               f'stroke-linecap="round">')
    for i, arc in enumerate(arcs):
        za = zoom_attr(i)
        center, chord, bulge, n, off = arc
        path = f'      <path d="{arc_path(center, chord, bulge, off, n)}"/>'
        if za:
            out.append(f'      <g {za}>')
            out.append(path)
            out.append('      </g>')
        else:
            out.append(path)
    out.append('    </g>')

    if label_items:
        out.append(f'    <g font-family="{FONT}" font-size="{FONT_SIZE}" '
                   f'font-weight="bold" fill="{TXT_COLOR}" text-anchor="middle" '
                   f'dominant-baseline="central">')
        for item in label_items:
            if len(item) == 5:
                idx, px, py, ang, lines = item
            else:
                idx, px, py, ang, lines = None, *item
            za = zoom_attr(idx) if idx is not None else None
            spans = "".join(
                f'<tspan x="0" dy="{0 if i == 0 else LINE_H}">{t}</tspan>'
                for i, t in enumerate(lines))
            text = (f'<text x="0" y="0" '
                    f'transform="translate({px:.2f},{py:.2f}) '
                    f'rotate({ang:.2f})">{spans}</text>')
            if za:
                out.append(f'      <g {za}>{text}</g>')
            else:
                out.append(f'      {text}')
        out.append('    </g>')

    if radial_all:
        out.append(f'    <g font-family="{FONT}" font-size="{RAD_FONT}" '
                   f'font-weight="bold" fill="{TXT_COLOR}" '
                   f'dominant-baseline="central">')
        for item in radial_all:
            if len(item) == 6:
                idx, (px, py), ang, anch, word, _d = item
            else:
                idx = None
                (px, py), ang, anch, word, _d = item
            za = zoom_attr(idx) if idx is not None else None
            text = (f'<text x="0" y="0" text-anchor="{anch}" '
                    f'transform="translate({px:.2f},{py:.2f}) '
                    f'rotate({ang:.2f})">{word}</text>')
            if za:
                out.append(f'      <g {za}>{text}</g>')
            else:
                out.append(f'      {text}')
        out.append('    </g>')

    if block_items:
        out.append(f'    <g font-family="{FONT}" font-size="{BLOCK_FONT}" '
                   f'fill="{TXT_COLOR}" dominant-baseline="central">')
        for item in block_items:
            if len(item) >= 5:
                _idx, bx, by, w_, t_ = item[0], item[1], item[2], item[3], item[4]
            else:
                bx, by, w_, t_ = item
            out.append(f'      <text x="{bx:.2f}" y="{by:.2f}">{w_}: '
                       f'<tspan font-weight="bold">{t_}</tspan></text>')
        out.append('    </g>')

    out.append(f'    <g font-family="{FONT}" font-size="{V_FONT_SIZE}" '
               f'fill="{TXT_COLOR}" text-anchor="middle" '
               f'dominant-baseline="central" letter-spacing="2">')
    for (px, py), txt in verts:
        out.append(f'      <text x="{px:.2f}" y="{py:.2f}">{txt}</text>')
    out.append('    </g>')
    out.append('  </g>')


def build_a2(write_files=True):
    """Baut den A2-Inhalt. Gibt Dict mit svg, inner, Bloecken, Massen zurueck.

    write_files: SVG/Dreiecke-SVG schreiben (CLI). A0 ruft mit False auf.
    """
    global R, FONT_SIZE, LINE_H, BLOCK_FONT, BLOCK_LH
    global RAD_FONT, RAD_GAP, V_FONT_SIZE, INNER_FONT
    _saved = (R, FONT_SIZE, LINE_H, BLOCK_FONT, BLOCK_LH,
              RAD_FONT, RAD_GAP, V_FONT_SIZE, INNER_FONT)
    try:
        # ---------------------------------------------------------------- Layout: zwei Haelften auf A2
        # Lokales Dreieck mit Spitze bei (0, 0) — wird spaeter verschoben.
        LOCAL_APEX = (0.0, 0.0)
        la, lb, lc, lcentroid = triangle_vertices(LOCAL_APEX, SIDE)
        local_arcs = build_arcs(la, lb, lc, lcentroid)
        local_verts = vertex_items(la, lb, lc, lcentroid)

        # Gesundheits-Inhalt in lokalen Koordinaten
        ges_labels, ges_radial, ges_radial_by_arc, ges_blocks = build_panel_content(
            local_arcs, lcentroid, LABELS, RADIAL, BLOCKS, LABEL_NUDGE, BLOCK_NUDGE)

        # Krankheits-Inhalt (dm-01k … dm-09k)
        kra_labels, kra_radial, kra_radial_by_arc, kra_blocks = build_panel_content(
            local_arcs, lcentroid, LABELS_KRANK, RADIAL_KRANK, BLOCKS_KRANK,
            LABEL_NUDGE_KRANK, BLOCK_NUDGE_KRANK)

        # Leitprinzipien im Inneren (lokale Koordinaten, vor Font-Skalierung)
        kra_inner = inner_labels(la, lb, lc, INNER_KRANK, recht_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": VORRECHTE_LEG_T,
            "inset_frac": VORRECHTE_INSET_FRAC,
            "anchor": "end",
            "outward": True,
            "baseline": "alphabetic",
        }, wirtschaft_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": WETTBEWERB_LEG_T,
            "inset_frac": 0.0,
            "anchor": "start",
            "outward": True,
            "baseline": "alphabetic",
            "drop_below": True,
        }, geist_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": LEERE_WORTE_LEG_T,
            "inset_frac": 0.0,
            "anchor": "end",
            "outward": True,
            "baseline": "alphabetic",
        })
        ges_inner = inner_labels(la, lb, lc, INNER_GESUND, recht_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": VORRECHTE_LEG_T,
            "inset_frac": VORRECHTE_INSET_FRAC,
            "anchor": "end",
            "outward": True,
            "baseline": "alphabetic",
        }, wirtschaft_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": WETTBEWERB_LEG_T,
            "inset_frac": 0.0,
            "anchor": "start",
            "outward": True,
            "baseline": "alphabetic",
            "drop_below": True,
        }, geist_style={
            "scale": VORRECHTE_SCALE,
            "leg_t": LEERE_WORTE_LEG_T,
            "inset_frac": 0.0,
            "anchor": "end",
            "outward": True,
            "baseline": "alphabetic",
        })

        # Ausdehnung der Haelften (inkl. Reserve fuer CSS-Zoom + Aussenversatz)
        # Etwas knapper: linke Bloecke ruecken naeher → mehr Platz fuer groesseres Dreieck
        ZOOM_LAYOUT_PAD = (ARC_ZOOM - 1.0) * (OFFSET + R + 200.0) + 140.0
        gx0, gx1, gy0, gy1 = panel_extent(
            local_arcs, ges_radial_by_arc, ges_blocks, local_verts, la, lb, lc)
        kx0, kx1, ky0, ky1 = panel_extent(
            local_arcs, kra_radial_by_arc, kra_blocks, local_verts, la, lb, lc)
        gx0 -= ZOOM_LAYOUT_PAD; gx1 += ZOOM_LAYOUT_PAD
        gy0 -= ZOOM_LAYOUT_PAD; gy1 += ZOOM_LAYOUT_PAD
        kx0 -= ZOOM_LAYOUT_PAD; kx1 += ZOOM_LAYOUT_PAD
        ky0 -= ZOOM_LAYOUT_PAD; ky1 += ZOOM_LAYOUT_PAD

        # Beides in die jeweilige A2-Haelfte einpassen (Breite + Hoehe)
        # Hauptueberschrift oben: Schriftgroesse so, dass die laengste Zeile
        # ≈ 90% der Seitenbreite einnimmt.
        _title_len = max(len(s) for s in MAIN_TITLE_LINES)
        MAIN_TITLE_FONT = ((MAIN_TITLE_WIDTH_FRAC * PAGE_W) / (0.52 * _title_len)) * 0.85
        MAIN_TITLE_LINE_H = MAIN_TITLE_FONT * 1.12
        MAIN_TITLE_BAND = (PAGE_MARGIN + MAIN_TITLE_FONT * 0.55
                           + (len(MAIN_TITLE_LINES) - 1) * MAIN_TITLE_LINE_H
                           + MAIN_TITLE_FONT * 0.70)

        half_h = (PAGE_H - PAGE_MARGIN - MAIN_TITLE_BAND - HALF_GAP - PAGE_MARGIN) / 2
        usable_w = PAGE_W - 2 * PAGE_MARGIN

        # Breite beider Panele (Gesundheit ist breiter wegen Textbloecken)
        content_w = max(gx1 - gx0, kx1 - kx0)
        content_h_ges = gy1 - gy0
        content_h_kra = ky1 - ky0
        # Gemeinsamer Massstab: beide Haelften gleich skalieren
        scale = min(usable_w / content_w,
                    half_h / content_h_ges,
                    half_h / content_h_kra)

        def place_panel(x0, x1, y0, y1, half_top):
            """dx, dy so, dass lokales Panel zentriert in der Haelfte landet."""
            cx = PAGE_MARGIN + usable_w / 2
            cy = half_top + half_h / 2
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            dx = cx - mid_x * scale
            dy = cy - mid_y * scale
            return dx, dy

        # Obere Haelfte = Krankheit (unter der Hauptueberschrift), untere = Gesundheit
        kra_top = MAIN_TITLE_BAND
        ges_top = MAIN_TITLE_BAND + half_h + HALF_GAP

        kra_dx, kra_dy = place_panel(kx0, kx1, ky0, ky1, kra_top)
        ges_dx, ges_dy = place_panel(gx0, gx1, gy0, gy1, ges_top)


        def xform_pt(p, dx, dy):
            return (p[0] * scale + dx, p[1] * scale + dy)


        def xform_arcs(arcs, dx, dy):
            out = []
            for center, chord, bulge, n, off in arcs:
                out.append((xform_pt(center, dx, dy), chord, bulge, n, off * scale))
            return out


        def xform_verts(verts, dx, dy):
            return [(xform_pt(p, dx, dy), t) for p, t in verts]


        # Radius und Abstaende skalieren mit — R wird in arc_path global genutzt.
        # Deshalb temporaer R/Offsets skalieren, indem wir R anpassen und
        # die Offsets schon in xform_arcs skaliert haben.
        R_ORIG = R
        R = R * scale
        FONT_SIZE_S = FONT_SIZE * scale
        LINE_H_S = LINE_H * scale
        BLOCK_FONT_S = BLOCK_FONT * scale
        BLOCK_LH_S = BLOCK_LH * scale
        RAD_FONT_S = RAD_FONT * scale
        RAD_GAP_S = RAD_GAP * scale
        V_FONT_SIZE_S = V_FONT_SIZE * scale
        INNER_FONT_S = INNER_FONT * scale

        # Font-Globals fuer Rendering anpassen
        FONT_SIZE = FONT_SIZE_S
        LINE_H = LINE_H_S
        BLOCK_FONT = BLOCK_FONT_S
        BLOCK_LH = BLOCK_LH_S
        RAD_FONT = RAD_FONT_S
        RAD_GAP = RAD_GAP_S
        V_FONT_SIZE = V_FONT_SIZE_S
        INNER_FONT = INNER_FONT_S
        V_GAP_S = V_GAP * scale

        # Vertices mit skaliertem V_GAP neu setzen
        def scaled_verts(a, b, c, centroid, dx, dy):
            items = []
            for V, txt in zip((a, b, c), VERTEX_LABELS):
                d = norm(sub(V, centroid))
                local = add(V, mul(d, V_GAP))  # V_GAP schon unskaliert in local space
                items.append((xform_pt(local, dx, dy), txt))
            return items


        # Krankheit
        kra_a = xform_pt(la, kra_dx, kra_dy)
        kra_b = xform_pt(lb, kra_dx, kra_dy)
        kra_c = xform_pt(lc, kra_dx, kra_dy)
        kra_arcs = xform_arcs(local_arcs, kra_dx, kra_dy)
        kra_verts = scaled_verts(la, lb, lc, lcentroid, kra_dx, kra_dy)
        kra_inner_t = [
            (xform_pt(p, kra_dx, kra_dy), ang, txt, size * scale, anch, base)
            for p, ang, txt, size, anch, base in kra_inner
        ]

        kra_labels_t = [
            (idx, px * scale + kra_dx, py * scale + kra_dy, ang, lines)
            for idx, px, py, ang, lines in kra_labels
        ]
        kra_radial_t = [
            (idx, xform_pt((px, py), kra_dx, kra_dy), ang, anch, word, d)
            for idx, (px, py), ang, anch, word, d in kra_radial
        ]
        kra_blocks_t = [
            (idx, bx * scale + kra_dx, by * scale + kra_dy, w, t)
            for idx, bx, by, w, t in kra_blocks
        ]

        # Gesundheit (mit Inhalt)
        ges_a = xform_pt(la, ges_dx, ges_dy)
        ges_b = xform_pt(lb, ges_dx, ges_dy)
        ges_c = xform_pt(lc, ges_dx, ges_dy)
        ges_arcs = xform_arcs(local_arcs, ges_dx, ges_dy)
        ges_verts = scaled_verts(la, lb, lc, lcentroid, ges_dx, ges_dy)
        ges_inner_t = [
            (xform_pt(p, ges_dx, ges_dy), ang, txt, size * scale, anch, base)
            for p, ang, txt, size, anch, base in ges_inner
        ]

        ges_labels_t = [
            (idx, px * scale + ges_dx, py * scale + ges_dy, ang, lines)
            for idx, px, py, ang, lines in ges_labels
        ]
        ges_radial_t = [
            (idx, xform_pt((px, py), ges_dx, ges_dy), ang, anch, word, d)
            for idx, (px, py), ang, anch, word, d in ges_radial
        ]
        ges_blocks_t = [
            (idx, bx * scale + ges_dx, by * scale + ges_dy, w, t)
            for idx, bx, by, w, t in ges_blocks
        ]


        def css_zoom_point(p, origin, z, shift):
            ox, oy = origin
            return (ox + z * (p[0] - ox) + shift[0],
                    oy + z * (p[1] - oy) + shift[1])


        def one_arc_zoom(arcs, labels, radials, inner, arc_idx, clear_names=None):
            """CSS-Zoom um den Kreis-Mittelpunkt, dann senkrecht nach aussen.

            clear_names: Liste von Innen-Beschriftungen, gegen die Abstand gehalten wird.
            Ohne clear_names: Mindest-Aussenversatz proportional zum Zoom.
            """
            center, chord, bulge, n, off = arcs[arc_idx]
            origin = add(center, mul(n, off))
            z = ARC_ZOOM
            pts = []
            for p in arc_points(center, chord, bulge, off, n):
                pts.append(p)
            for item in labels:
                if item[0] == arc_idx:
                    pts.append((item[1], item[2]))
            for item in radials:
                if item[0] != arc_idx:
                    continue
                (px, py), _ang, _an, word, d = item[1], item[2], item[3], item[4], item[5]
                pts.append((px, py))
                pts.append(add((px, py), mul(d, text_w(word, RAD_FONT, bold=True))))
            clear_names = clear_names or []
            extra = (z - 1.0) * R + ARC_CLEAR_PAD * 0.35
            for clear_name in clear_names:
                matches = [it for it in inner if it[2] == clear_name]
                if not matches:
                    continue
                (vx, vy), _vang, _txt, vsize, _a, _b = matches[0]
                obs_h = 1.05 * vsize
                min_along = None
                for p in pts:
                    q = css_zoom_point(p, origin, z, (0.0, 0.0))
                    along = (q[0] - vx) * n[0] + (q[1] - vy) * n[1]
                    min_along = along if min_along is None else min(min_along, along)
                need = (obs_h + ARC_CLEAR_PAD) - min_along
                if need > extra:
                    extra = need
            if extra < 0:
                extra = 0.0
            shift = mul(n, extra)
            return origin, z, shift


        # Welche Innen-Beschriftung den Aussenabstand setzt (Krankheit / Gesundheit)
        ARC_CLEAR_KRANK = {
            0: ["Vorrechte"],
            1: ["Vorrechte", "Wettbewerb"],
            2: [],
            3: ["Wettbewerb"],
            4: ["Wettbewerb", "Leere Worte"],
            5: [],
            6: ["Leere Worte"],
            7: ["Leere Worte"],
            8: [],
        }
        ARC_CLEAR_GESUND = {
            0: ["Gleichheit"],
            1: ["Gleichheit", "Br\u00fcderlichkeit"],
            2: [],
            3: ["Br\u00fcderlichkeit"],
            4: ["Br\u00fcderlichkeit", "Freiheit"],
            5: [],
            6: ["Freiheit"],
            7: ["Freiheit"],
            8: [],
        }
        # Bevorzugte Seite der 7-Zeilen; fit_blocks faellt auf freie Seite zurueck
        BLOCK_PLACE = {
            0: "left",
            1: "left",
            3: "left",
            4: "right",
            6: "right",
            7: "right",
        }


        def panel_arc_zooms(arcs, labels, radials, inner, clear_map):
            """Alle 9 Halbkreise gleich zoomen und nach aussen schieben."""
            out = {}
            for idx in range(9):
                out[idx] = one_arc_zoom(
                    arcs, labels, radials, inner, idx, clear_map.get(idx, []))
            return out


        # Untere Eck-Halbkreise (Wirtschaft → Geist / Geist → Wirtschaft)
        BASE_ARC_PAIR = (3, 4)


        def equalize_arc_pair_shift(arc_zoom, arcs, pair):
            """Gleiche Aussenverschiebung auf derselben Kante (gleiche Hoehe)."""
            a, b = pair
            n = arcs[a][3]
            extras = []
            for idx in pair:
                _o, _z, sh = arc_zoom[idx]
                extras.append(sh[0] * n[0] + sh[1] * n[1])
            extra = max(extras)
            shift = mul(n, extra)
            for idx in pair:
                origin, z, _sh = arc_zoom[idx]
                arc_zoom[idx] = (origin, z, shift)
            return arc_zoom


        def equalize_block_pair_y(blocks, pair):
            """7-Zeiler eines Paares auf dieselbe erste Zeile setzen."""
            a, b = pair
            first = {}
            for item in blocks:
                idx, _bx, by, _w, _t = item
                if idx in pair and idx not in first:
                    first[idx] = by
            if a not in first or b not in first:
                return blocks
            y = (first[a] + first[b]) / 2.0
            out = []
            for item in blocks:
                idx, bx, by, w, t = item
                if idx == a:
                    by = by + (y - first[a])
                elif idx == b:
                    by = by + (y - first[b])
                out.append((idx, bx, by, w, t))
            return out


        def fit_blocks_to_zoomed_arcs(blocks, arcs, radials, arc_zoom):
            """7 Einzeiler neben/ueber/unter den gezoomten Halbkreisen neu setzen."""
            def rad_w(word, z):
                return 0.65 * RAD_FONT * z * len(word)

            def fan_box(idx):
                origin, z, shift = arc_zoom[idx]
                center, chord, bulge, n, off = arcs[idx]
                xs, ys = [], []
                for p in arc_points(center, chord, bulge, off, n):
                    q = css_zoom_point(p, origin, z, shift)
                    xs.append(q[0]); ys.append(q[1])
                for item in radials:
                    if item[0] != idx:
                        continue
                    (px, py), _a, _an, word, d = item[1], item[2], item[3], item[4], item[5]
                    p0 = css_zoom_point((px, py), origin, z, shift)
                    wlen = rad_w(word, z)
                    p1 = add(p0, mul(d, wlen))
                    p2 = add(p0, mul(d, -wlen))
                    xs += [p0[0], p1[0], p2[0]]
                    ys += [p0[1], p1[1], p2[1]]
                return min(xs), max(xs), min(ys), max(ys)

            def try_place(place, x0, x1, y0, y1, max_w, n_lines):
                """Position ohne Seiten-Ueberlauf und ohne Fan-Ueberlappung, oder None."""
                block_h = (n_lines - 1) * BLOCK_LH
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2

                def clamp_x(bx):
                    bx = max(PAGE_MARGIN, bx)
                    if bx + max_w > PAGE_W - PAGE_MARGIN:
                        bx = PAGE_W - PAGE_MARGIN - max_w
                    return bx

                if place == "right":
                    bx = x1 + BLOCK_PAD_RIGHT
                    by0 = mid_y - block_h / 2
                    if bx + max_w > PAGE_W - PAGE_MARGIN:
                        # Enger an den Fan, wenn der rechte Rand zu knapp ist
                        bx = PAGE_W - PAGE_MARGIN - max_w
                        if bx < x1 + 8:
                            return None
                elif place == "left":
                    bx = x0 - BLOCK_PAD_LEFT - max_w
                    by0 = mid_y - block_h / 2
                    if bx < PAGE_MARGIN:
                        bx = PAGE_MARGIN
                        if bx + max_w > x0 - 8:
                            # Text wuerde in den Fan laufen — nur kleine Ueberlappung ok
                            pass
                elif place == "above":
                    bx = clamp_x(mid_x - max_w / 2)
                    by0 = y0 - BLOCK_PAD - block_h
                    if by0 < PAGE_MARGIN + BLOCK_FONT:
                        return None
                elif place == "below":
                    bx = clamp_x(mid_x - max_w / 2)
                    by0 = y1 + BLOCK_PAD
                    if by0 + block_h > PAGE_H - PAGE_MARGIN:
                        return None
                else:
                    return None
                # Fan-Bounding-Box: kleine Randberuehrung (geklammerte Linkstexte) zulassen
                pad_tol = BLOCK_PAD_LEFT if place == "left" else BLOCK_PAD_RIGHT
                ox = min(bx + max_w, x1) - max(bx, x0)
                oy = min(by0 + block_h, y1) - max(by0, y0)
                if ox > pad_tol and oy > pad_tol:
                    return None
                return bx, by0

            by_arc = {}
            for item in blocks:
                idx, bx, by, w, t = item
                by_arc.setdefault(idx, []).append((w, t))
            out = []
            for idx, entries in by_arc.items():
                if idx not in arc_zoom:
                    continue
                x0, x1, y0, y1 = fan_box(idx)
                max_w = max(line_w(w, t) for w, t in entries)
                n = len(entries)
                preferred = BLOCK_PLACE.get(idx, "left")
                if preferred == "left":
                    order = ("left", "above", "below")
                elif preferred == "right":
                    order = ("right", "below", "above")
                elif preferred == "above":
                    order = ("above", "left", "right", "below")
                else:
                    order = ("below", "right", "left", "above")
                placed = None
                for place in order:
                    placed = try_place(place, x0, x1, y0, y1, max_w, n)
                    if placed:
                        break
                if not placed:
                    # Notfall: an bevorzugte Seite klemmen
                    block_h = (n - 1) * BLOCK_LH
                    mid_y = (y0 + y1) / 2
                    if preferred == "right":
                        bx = max(x1 + BLOCK_PAD_RIGHT * 0.35,
                                 PAGE_W - PAGE_MARGIN - max_w)
                        by0 = mid_y - block_h / 2
                    elif preferred == "left":
                        bx = PAGE_MARGIN
                        by0 = mid_y - block_h / 2
                    else:
                        bx = PAGE_MARGIN if preferred == "above" else PAGE_W - PAGE_MARGIN - max_w
                        by0 = max(PAGE_MARGIN + BLOCK_FONT,
                                  min(y0 - BLOCK_PAD - block_h,
                                      PAGE_H - PAGE_MARGIN - block_h))
                    placed = (bx, by0)
                bx, by0 = placed
                for i, (w, t) in enumerate(entries):
                    out.append((idx, bx, by0 + i * BLOCK_LH, w, t))
            return out


        def nudge_blocks(blocks, nudge_map):
            """Optionale (dx, dy)-Korrektur pro Bogen nach dem Fit."""
            if not nudge_map:
                return blocks
            out = []
            for item in blocks:
                idx, bx, by, w, t = item
                dx, dy = nudge_map.get(idx, (0.0, 0.0))
                out.append((idx, bx + dx, by + dy, w, t))
            return out


        kra_arc_zoom = panel_arc_zooms(
            kra_arcs, kra_labels_t, kra_radial_t, kra_inner_t, ARC_CLEAR_KRANK)
        equalize_arc_pair_shift(kra_arc_zoom, kra_arcs, BASE_ARC_PAIR)
        kra_blocks_t = fit_blocks_to_zoomed_arcs(
            kra_blocks_t, kra_arcs, kra_radial_t, kra_arc_zoom)
        kra_blocks_t = equalize_block_pair_y(kra_blocks_t, BASE_ARC_PAIR)
        kra_blocks_t = nudge_blocks(kra_blocks_t, BLOCK_FIT_NUDGE_KRANK)

        ges_arc_zoom = panel_arc_zooms(
            ges_arcs, ges_labels_t, ges_radial_t, ges_inner_t, ARC_CLEAR_GESUND)
        equalize_arc_pair_shift(ges_arc_zoom, ges_arcs, BASE_ARC_PAIR)
        ges_blocks_t = fit_blocks_to_zoomed_arcs(
            ges_blocks_t, ges_arcs, ges_radial_t, ges_arc_zoom)
        ges_blocks_t = equalize_block_pair_y(ges_blocks_t, BASE_ARC_PAIR)
        ges_blocks_t = nudge_blocks(ges_blocks_t, BLOCK_FIT_NUDGE_GESUND)

        # ---------------------------------------------------------------- SVG schreiben
        out = []
        out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                   f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                   f'viewBox="0 0 {PAGE_W:.2f} {PAGE_H:.2f}" '
                   f'width="{PAGE_W:.0f}" height="{PAGE_H:.0f}">')
        out.append(f'  <rect x="0" y="0" width="{PAGE_W:.2f}" height="{PAGE_H:.2f}" '
                   f'fill="{BG}"/>')
        if os.path.isfile(BG_IMAGE):
            href = os.path.basename(BG_IMAGE)
            out.append(
                f'  <image href="{href}" xlink:href="{href}" '
                f'x="0" y="0" width="{PAGE_W:.2f}" height="{PAGE_H:.2f}" '
                f'preserveAspectRatio="none"/>'
            )

        # Hauptueberschrift ueber dem oberen Dreieck (zwei Zeilen, ~90% Breite)
        main_title_y = PAGE_MARGIN + MAIN_TITLE_FONT * 0.55
        _title_spans = "".join(
            f'<tspan x="{PAGE_W / 2:.2f}" dy="{0 if i == 0 else MAIN_TITLE_LINE_H:.2f}">{line}</tspan>'
            for i, line in enumerate(MAIN_TITLE_LINES))

        # Sektionsworte als Hintergrund (gleiche Groesse, nichts anderes verschieben)
        krank_wm_y = main_title_y + MAIN_TITLE_LINE_H * 2 + MAIN_TITLE_FONT * 0.38
        ges_wm_y = ges_a[1] - (kra_a[1] - krank_wm_y)


        def watermark(txt, y):
            out.append(f'  <text x="{PAGE_W / 2:.2f}" y="{y:.2f}" '
                       f'font-family="{FONT}" font-size="{MAIN_TITLE_FONT:.2f}" '
                       f'font-weight="bold" fill="{SECTION_WATERMARK}" '
                       f'text-anchor="middle" dominant-baseline="central" '
                       f'letter-spacing="2">{txt}</text>')


        watermark("Krankheit", krank_wm_y)
        watermark("Gesundheit", ges_wm_y)

        out.append(f'  <text x="{PAGE_W / 2:.2f}" y="{main_title_y:.2f}" '
                   f'font-family="{FONT}" font-size="{MAIN_TITLE_FONT:.2f}" '
                   f'font-weight="bold" fill="{TXT_COLOR}" text-anchor="middle" '
                   f'dominant-baseline="central" letter-spacing="2">'
                   f'{_title_spans}</text>')

        # Krankheit oben
        render_panel(
            out, "krankheit", kra_a, kra_b, kra_c, kra_arcs, kra_verts,
            label_items=kra_labels_t, radial_all=kra_radial_t, block_items=kra_blocks_t,
            inner_items=kra_inner_t, arc_zoom=kra_arc_zoom,
            fill_image=TRI_IMAGE_KRANK if os.path.isfile(TRI_IMAGE_KRANK) else None,
        )

        # Gesundheit unten
        render_panel(
            out, "gesundheit", ges_a, ges_b, ges_c, ges_arcs, ges_verts,
            label_items=ges_labels_t, radial_all=ges_radial_t, block_items=ges_blocks_t,
            inner_items=ges_inner_t, arc_zoom=ges_arc_zoom,
            fill_image=TRI_IMAGE_GESUND if os.path.isfile(TRI_IMAGE_GESUND) else None,
        )

        out.append('</svg>')

        svg = "\n".join(out)
        if write_files:
            _out_path = os.path.join(_DIR, "doppelmatrix-halbkreise.svg")
            with open(_out_path, "w") as f:
                f.write(svg)
            print(f"DIN A2 Portrait  {PAGE_W:.0f}\u00d7{PAGE_H:.0f}  (1 unit = 0.1 mm)")
            print(f"scale={scale:.4f}  OFFSET={OFFSET}  MEDIAN_OFFSET={MEDIAN_OFFSET}")
            for _i, (_o, _z, _sh) in sorted(kra_arc_zoom.items()):
                print(f"kra arc{_i} zoom={_z}  |shift|={math.hypot(*_sh):.1f}")
            for _i, (_o, _z, _sh) in sorted(ges_arc_zoom.items()):
                print(f"ges arc{_i} zoom={_z}  |shift|={math.hypot(*_sh):.1f}")
            print(f"wrote {_out_path}")

            _tri_path = os.path.join(_DIR, "doppelmatrix-halbkreise-dreiecke.svg")
            _tri = [
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_W:.2f} {PAGE_H:.2f}" '
                f'width="{PAGE_W:.0f}" height="{PAGE_H:.0f}">',
                f'  <polygon points="{kra_a[0]:.2f},{kra_a[1]:.2f} {kra_b[0]:.2f},{kra_b[1]:.2f} '
                f'{kra_c[0]:.2f},{kra_c[1]:.2f}" fill="{TRI_FILL}" stroke="{TRI_STROKE}" stroke-width="3"/>',
                f'  <polygon points="{ges_a[0]:.2f},{ges_a[1]:.2f} {ges_b[0]:.2f},{ges_b[1]:.2f} '
                f'{ges_c[0]:.2f},{ges_c[1]:.2f}" fill="{TRI_FILL}" stroke="{TRI_STROKE}" stroke-width="3"/>',
                '</svg>',
            ]
            with open(_tri_path, "w") as f:
                f.write("\n".join(_tri) + "\n")
            print(f"wrote {_tri_path}")

        # Seite ohne <svg>-Rahmen, ohne Seiten-Rect/Hintergrund (A0 legt beides selbst)
        inner_start = 1
        while inner_start < len(out) and (
            out[inner_start].lstrip().startswith("<rect ")
            or "doppelmatrix-hintergrund.jpg" in out[inner_start]
        ):
            inner_start += 1
        inner = "\n".join(out[inner_start:-1])

        def _blocks(items, panel):
            by_idx = {}
            for idx, bx, by, w, t in items:
                by_idx.setdefault(idx, []).append((bx, by, w, t))
            blocks = []
            for idx, rows in by_idx.items():
                rows.sort(key=lambda r: r[1])
                blocks.append({
                    "idx": idx,
                    "panel": panel,
                    "x": rows[0][0],
                    "y0": rows[0][1],
                    "y1": rows[-1][1],
                    "words": [r[2] for r in rows],
                    "font": BLOCK_FONT,
                    "lh": BLOCK_LH,
                })
            return blocks

        kra_blocks = _blocks(kra_blocks_t, "kra")
        ges_blocks = _blocks(ges_blocks_t, "ges")
        return {
            "svg": svg,
            "inner": inner,
            "page_w": PAGE_W,
            "page_h": PAGE_H,
            "bg": BG,
            "bg_image": BG_IMAGE if os.path.isfile(BG_IMAGE) else None,
            "font": FONT,
            "txt_color": TXT_COLOR,
            "block_font": BLOCK_FONT,
            "block_lh": BLOCK_LH,
            "kra_blocks": kra_blocks,
            "ges_blocks": ges_blocks,
            "seven_blocks": kra_blocks + ges_blocks,
        }
    finally:
        (R, FONT_SIZE, LINE_H, BLOCK_FONT, BLOCK_LH,
         RAD_FONT, RAD_GAP, V_FONT_SIZE, INNER_FONT) = _saved


if __name__ == "__main__":
    build_a2(write_files=True)
