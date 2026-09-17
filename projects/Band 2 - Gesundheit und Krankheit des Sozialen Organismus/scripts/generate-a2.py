#!/usr/bin/env python3
"""
Soziale Gesundheit — DIN-A2-Hochformat mit zwei Dreiecken untereinander.

  Obere Haelfte:  Krankheit
  Untere Haelfte: Gesundheit

Zusammenhang mit der YAML
-----------------------------------------
Die YAML ist die inhaltliche Quelle (Titel, Schlagwort, Schlagsatz).
A2 und A0 lesen sie. Layout (Bogenindex, Seite, Zeilenumbruch) bleibt hier.

Halbkreis-Index  <->  YAML
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

A0 ruft build_a2() als Bibliothek auf.

Klint-Fuellungen (optional): dreieck-krankheit.png /
dreieck-gesundheit.png im selben Ordner werden in die
Dreiecksflaechen gelegt; fehlen sie, bleibt die graue Flaeche.
Hintergrund (optional): hintergrund.jpg fuellt die Seite
statt der Beige-Flaeche (DIN-A, z. B. A0-Zuschnitt).
"""
import math
import os
import pathlib
import re
import shutil
import subprocess

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
A2_TITLE_WIDTH_FRAC = 0.72    # A2: Titel mit Rand, damit er ins Bild passt

# ---------------------------------------------------------------- Dreiecks-Parameter
SIDE   = 1400.0 * 1.15       # Seitenlaenge (+15%)
R      = 87.5                # Radius der Halbkreise
OFFSET = 240.0               # Aussenversatz der Eck-Halbkreise
MEDIAN_OFFSET = 340.0        # Aussenversatz der mittleren (Median-)Halbkreise
CORNER_T = 0.155             # Kantenanteil Eck-Halbkreise (kleiner = naeher an Ecke)
ROTATE_LABELS = False
LABEL_ARC_PAD = 10.0

BG         = "#f4f1ea"
# Fallback, falls Hintergrundbild nicht lesbar ist
SECTION_WATERMARK = "#ddd9ce"
WATERMARK_SCALE = 2.0        # Hintergrundworte relativ zur Hauptueberschrift
WATERMARK_DARKEN = 0.10      # 10 % dunkler als die BG-Farbe an der Textstelle
WATERMARK_OPACITY = 0.6      # Krankheit / Gesundheit
TRI_FILL   = "#9b9b9b"
TRI_STROKE = "#6f6f6f"
_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_PATH = os.path.join(
    _DIR, "content", "Gesundheit und Krankheit des Sozialen Organismus.yaml")
TRI_IMAGE_KRANK = os.path.join(_DIR, "assets", "dreieck-krankheit-web.png")
TRI_IMAGE_GESUND = os.path.join(_DIR, "assets", "dreieck-gesundheit-web.png")
BG_IMAGE = os.path.join(_DIR, "assets", "hintergrund-web.jpg")
FONT_DERIVED_FILE = os.path.join(
    _DIR, "assets", "fonts", "SpecialElite-Regular.ttf")
FONT_DERIVED_BASENAME = "SpecialElite-Regular.ttf"
ARC_COLOR  = "#2b2b2b"
TXT_COLOR  = "#2b2b2b"
FONT       = "Georgia, 'Times New Roman', serif"
# Leitprinzipien am Dreieck (Wettbewerb, Vorrechte, …)
FONT_DERIVED = "Special Elite"
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
# Anteil an Blockbreite/-hoehe, dx<0 links, dy<0 oben
BLOCK_FIT_NUDGE_FRAC_KRANK = {
    0: (-0.15, 0.15),   # dm-04k
    1: (-0.25, -0.15),  # dm-05k
    4: (-0.3, 0.0),     # dm-02k: 30 % Textbreite nach links (war −60 %)
}
BLOCK_FIT_NUDGE_GESUND = {}
# Anteil an Blockbreite/-hoehe, dx>0 rechts, dy<0 oben
BLOCK_FIT_NUDGE_FRAC_GESUND = {
    1: (-0.5, 0.0),    # dm-05g: 50 % Textbreite nach links (schräg links über dem Fan)
    7: (0.4, 0.0),     # dm-01g: 40 % Textbreite nach rechts
}
# dm-05g (Bogen 1): fx = Anteil Blockbreite, fy_lh = Zeilenhöhen (dy<0 oben)
BLOCK_FIT_NUDGE_LH_GESUND = {}

# Rahmen um die 7-Zeilen-Bloecke (wie A0-Karten)
BLOCK_FRAME_STROKE = "#b7b1a6"
BLOCK_FRAME_RX = 12.0
BLOCK_FRAME_PAD = 10.0
BLOCK_FRAME_SW = 1.0


# Bogenindex → YAML-IDs (gesund, krank). Nur Layout, kein Inhalt.
ARC_FIELD = {
    0: ("dm-04g", "dm-04k"),
    1: ("dm-05g", "dm-05k"),
    2: ("dm-09g", "dm-09k"),
    3: ("dm-06g", "dm-06k"),
    4: ("dm-02g", "dm-02k"),
    5: ("dm-08g", "dm-08k"),
    6: ("dm-03g", "dm-03k"),
    7: ("dm-01g", "dm-01k"),
    8: ("dm-07g", "dm-07k"),
}
# Zeilenumbruch der Richtung im Halbkreis (passt in den Bogen, nicht in die YAML).
DIRECTION_PREFIX = {
    0: ["Recht \u2192", "Wirtschaft:"],
    1: ["Wirtschaft \u2192", "Recht:"],
    2: ["Recht +", "Wirtschaft", "\u2192 Geist:"],
    3: ["Wirtschaft \u2192", "Geist:"],
    4: ["Geist \u2192", "Wirtschaft:"],
    5: ["Geist +", "Wirtschaft", "\u2192 Recht:"],
    6: ["Recht \u2192 Geist:"],
    7: ["Geist \u2192 Recht:"],
    8: ["Geist + Recht", "\u2192 Wirtschaft:"],
}
# 7-Zeiler: links oder rechts vom Bogen
BLOCK_SIDE = {
    7: "right", 4: "right", 6: "right",
    0: "left", 1: "left", 3: "left",
}
LABEL_TITLE_MAX_W = 160.0
TITLE_WRAP = {
    "dm-01g": ["Sachkenntnis prägt", "das Recht"],
    "dm-01k": ["Die Weltsicht wird", "zum Gesetz"],
    "dm-02k": ["Der Glaube diktiert", "die Produktion"],
    "dm-05g": ["Die Wirtschaft", "trägt den Staat"],
    "dm-06g": ["Die Wirtschaft", "versorgt den Geist"],
}

RADIAL_REVERSE = False

# Titel, Schlagworte, Schlagsätze: yaml_arc_content() liest die YAML.

LABEL_NUDGE = {}
LABEL_NUDGE_KRANK = {}
BLOCK_NUDGE_KRANK = {
    0: (0, -150),
    6: (0, -150),
}

VERTEX_LABELS = ["Politik und Recht", "Wirtschaft", "Kultur/Geist"]

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
INNER_EDGE_MARGIN_FRAC = 0.05  # Luft Wort↔Kante, Anteil der Schrifthoehe
HEADING_TO_LEIT_SCALE = 1.15  # Halbkreis-Titel vs. Vorrechte / Wettbewerb
WETTBEWERB_LEG_T = 0.06      # Anker nahe Wirtschaft (Anteil Kante Wirtschaft→Geist)
LEERE_WORTE_LEG_T = 0.06     # Anker nahe Kultur/Geist (Anteil Kante Geist→Recht)
# Krankheit, Boegen 0+1: CSS-Zoom, dann senkrecht nach aussen
ARC_ZOOM = 1.5               # wieder 15% kleiner als zuletzt (1.725)
ARC_CLEAR_PAD = 40.0         # Abstand Strahlen zu Vorrechte / Wettbewerb
# 3 px ueber Mini-Titel (richtung:) und ueber Schlagsatz, visuell auf A2/A0 @ 300 dpi
LABEL_SECTION_MARGIN_PX = 3.0
A2_PX_PER_UNIT = (420.0 / 25.4 * 300.0) / PAGE_W


def label_section_margin():
    """Abstand in SVG-Einheiten der gerenderten (skalierten) Labels."""
    return LABEL_SECTION_MARGIN_PX / (ARC_ZOOM * A2_PX_PER_UNIT)

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


def wrap_line(text, size, max_w, bold=False):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, size, bold=bold) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _clean_aspect_text(raw):
    """YAML-Fliesstext: Kommentarzeilen (# / ═══) und Artefakte entfernen."""
    lines = []
    for ln in raw.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            break
        if set(s) <= set("═=-_─— "):
            break
        lines.append(s)
    body = " ".join(lines)
    body = re.sub(r"\s*#\s*$", "", body).strip()
    return body


def _yaml_scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def load_yaml_fields(path=None):
    """Titel, Richtung, Aspekte (Schlagwort / Schlagsatz / Text) aus der YAML."""
    with open(path or YAML_PATH, encoding="utf-8") as f:
        src = f.read()
    fields = {}
    for m in re.finditer(r"- id: (dm-\d+[gk])\n(.*?)(?=\n  - id: |\Z)", src, re.S):
        fid, block = m.group(1), m.group(2)
        titel_m = re.search(r"titel: \"([^\"]+)\"", block)
        richtung_m = re.search(r"richtung: \"([^\"]+)\"", block)
        aspects = []
        for am in re.finditer(
            r"- schlagwort: ([^\n]+)\n"
            r"        schlagsatz: ([^\n]+)\n"
            r"        text: >\s*\n"
            r"(.*?)(?="
            r"\n        zitate:"
            r"|\n      - schlagwort:"
            r"|\n  - id: "
            r"|\n  #"
            r"|\n\Z)",
            block, re.S,
        ):
            aspects.append({
                "schlagwort": _yaml_scalar(am.group(1)),
                "schlagsatz": _yaml_scalar(am.group(2)),
                "text": _clean_aspect_text(am.group(3)),
            })
        fields[fid] = {
            "titel": titel_m.group(1) if titel_m else "",
            "richtung": richtung_m.group(1) if richtung_m else "",
            "aspects": aspects,
        }
    return fields


def yaml_arc_content():
    """Halbkreis-Labels, Strahlen und 7-Zeiler aus der YAML."""
    fields = load_yaml_fields()
    missing = [fid for pair in ARC_FIELD.values() for fid in pair
               if fid not in fields]
    if missing:
        raise SystemExit(f"YAML fehlt: {', '.join(missing)}")
    labels_g, labels_k = [], {}
    radial_g, radial_k = {}, {}
    blocks_g, blocks_k = [], []
    for idx in range(9):
        gid, kid = ARC_FIELD[idx]
        prefix = DIRECTION_PREFIX[idx]
        g, k = fields[gid], fields[kid]
        g_title = TITLE_WRAP.get(gid) or wrap_line(
            g["titel"], FONT_SIZE, LABEL_TITLE_MAX_W, bold=True)
        k_title = TITLE_WRAP.get(kid) or wrap_line(
            k["titel"], FONT_SIZE, LABEL_TITLE_MAX_W, bold=True)
        labels_g.append(prefix + g_title)
        labels_k[idx] = prefix + k_title
        if idx in BLOCK_SIDE:
            if len(g["aspects"]) != 7 or len(k["aspects"]) != 7:
                raise SystemExit(
                    f"{gid}/{kid}: {len(g['aspects'])}/{len(k['aspects'])} "
                    "Aspekte, erwartet 7")
            gaspects = [(a["schlagwort"], a["schlagsatz"]) for a in g["aspects"]]
            kaspects = [(a["schlagwort"], a["schlagsatz"]) for a in k["aspects"]]
            radial_g[idx] = [a[0] for a in gaspects]
            radial_k[idx] = [a[0] for a in kaspects]
            side = BLOCK_SIDE[idx]
            blocks_g.append((idx, side, gaspects))
            blocks_k.append((idx, side, kaspects))
    return labels_g, radial_g, blocks_g, labels_k, radial_k, blocks_k


def font_face_svg():
    """@font-face für Special Elite — rsvg-convert liest die gebündelte TTF."""
    href = pathlib.Path(FONT_DERIVED_FILE).as_uri() if os.path.isfile(
        FONT_DERIVED_FILE) else FONT_DERIVED_BASENAME
    return (
        '  <defs>\n'
        '    <style type="text/css"><![CDATA[\n'
        f"      @font-face {{\n"
        f"        font-family: '{FONT_DERIVED}';\n"
        f"        src: url('{href}') format('truetype');\n"
        f"      }}\n"
        '    ]]></style>\n'
        '  </defs>'
    )


def copy_derived_font(out_dir):
    """TTF neben das Render-SVG legen (Fallback, falls file:// nicht greift)."""
    if not os.path.isfile(FONT_DERIVED_FILE):
        return None
    dst = os.path.join(out_dir, FONT_DERIVED_BASENAME)
    if not os.path.exists(dst):
        shutil.copy2(FONT_DERIVED_FILE, dst)
        return dst
    return None


def _parse_hex_rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (221, 217, 206)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def darken_rgb(rgb, frac=WATERMARK_DARKEN):
    """RGB um frac abdunkeln (1.0 = schwarz)."""
    k = max(0.0, 1.0 - frac)
    return tuple(max(0, min(255, int(round(c * k)))) for c in rgb)


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def sample_bg_darker(img_path, page_w, page_h, x, y,
                     darken=WATERMARK_DARKEN, fallback=SECTION_WATERMARK):
    """Farbe der auf page_w×page_h gestreckten BG-Datei an (x,y), abgedunkelt."""
    if not img_path or not os.path.isfile(img_path):
        return rgb_to_hex(darken_rgb(_parse_hex_rgb(fallback), darken))
    try:
        geom = subprocess.check_output(
            ["magick", "identify", "-format", "%w %h", img_path],
            text=True,
        ).strip()
        iw, ih = map(int, geom.split())
        px = max(0, min(iw - 1, int(round(x / page_w * (iw - 1)))))
        py = max(0, min(ih - 1, int(round(y / page_h * (ih - 1)))))
        raw = subprocess.check_output(
            ["magick", img_path,
             "-crop", f"1x1+{px}+{py}", "+repage",
             "-format",
             "%[fx:int(255*u.r)],%[fx:int(255*u.g)],%[fx:int(255*u.b)]",
             "info:"],
            text=True,
        ).strip()
        rgb = tuple(int(v) for v in raw.split(","))
        if len(rgb) != 3:
            raise ValueError(raw)
        return rgb_to_hex(darken_rgb(rgb, darken))
    except (OSError, subprocess.CalledProcessError, ValueError):
        return rgb_to_hex(darken_rgb(_parse_hex_rgb(fallback), darken))


def recolor_watermark(svg_text, word, fill):
    """fill-Attribut der Hintergrundschrift <word> setzen."""
    return re.sub(
        rf'(<text\b[^>]*\bfill=")[^"]+("[^>]*>{re.escape(word)}</text>)',
        rf'\g<1>{fill}\2',
        svg_text,
        count=1,
    )


def direction_line_count(lines):
    """Richtung (YAML richtung:) = Zeilen bis einschliesslich der mit ':'."""
    for i, t in enumerate(lines):
        if t.rstrip().endswith(":"):
            return i + 1
    return 0


def label_line_metrics(lines):
    """richtung: regular, visuell = 7-Zeiler (BLOCK_FONT); Titel bold + FONT_SIZE.

    Die Halbkreis-Labels liegen im ARC_ZOOM, die 7-Zeiler nicht —
    deshalb lokale Groesse BLOCK_FONT / ARC_ZOOM.
    """
    if isinstance(lines, str):
        lines = [lines]
    n_dir = direction_line_count(lines)
    dir_size = BLOCK_FONT / ARC_ZOOM
    dir_lh = LINE_H * (dir_size / FONT_SIZE) if FONT_SIZE else LINE_H
    out = []
    for i, t in enumerate(lines):
        if i < n_dir:
            out.append((t, dir_size, False, dir_lh))
        else:
            out.append((t, FONT_SIZE, True, LINE_H))
    return out


def label_pos(center, chord, bulge, offset, n, lines, centroid):
    if isinstance(lines, str):
        lines = [lines]
    metrics = label_line_metrics(lines)
    c = add(center, mul(n, offset))
    stack_h = sum(m[3] for m in metrics[1:]) if metrics else 0.0

    if ROTATE_LABELS:
        ang = math.degrees(math.atan2(chord[1], chord[0]))
        if ang > 90 or ang <= -90:
            ang += 180
        a = math.radians(ang)
        local_x = (math.cos(a), math.sin(a))
        local_y = (-local_x[1], local_x[0])
        depth = (R - stack_h) / 2
        step = 1 if (local_y[0] * bulge[0] + local_y[1] * bulge[1]) > 0 else -1
        if step < 0:
            depth += stack_h
        return add(c, mul(bulge, depth)), ang

    ang = 0.0
    # Im Bogenmittelpunkt halten. hits_arc schob lange Titel zum Dreieck
    # und aus der Mulde (oben: nach unten, seitlich: nach links/rechts).
    first = (c[0], c[1] - stack_h / 2.0)
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


def block_frame_rects(block_items):
    """Rahmen-Rechtecke je 7-Zeiler-Bogen."""
    by_arc = {}
    for item in block_items:
        idx, bx, by, w, t = item[0], item[1], item[2], item[3], item[4]
        by_arc.setdefault(idx, []).append((bx, by, w, t))
    rects = []
    pad = BLOCK_FRAME_PAD
    for idx, rows in by_arc.items():
        rows.sort(key=lambda r: r[1])
        x = rows[0][0]
        y0, y1 = rows[0][1], rows[-1][1]
        max_w = max(line_w(w, t) for _bx, _by, w, t in rows)
        h = (y1 - y0) + BLOCK_FONT
        rects.append((
            idx,
            x - pad,
            y0 - BLOCK_FONT * 0.5 - pad,
            max_w + 2 * pad,
            h + 2 * pad,
        ))
    return rects


def nudge_blocks_frac(blocks, frac_map):
    """Relative Verschiebung pro Bogen (Anteil an Breite/Hoehe des 7-Zeilers)."""
    if not frac_map:
        return blocks
    dims = {}
    by_arc = {}
    for item in blocks:
        idx, bx, by, w, t = item
        by_arc.setdefault(idx, []).append((bx, by, w, t))
    for idx in frac_map:
        rows = by_arc.get(idx, [])
        if not rows:
            continue
        max_w = max(line_w(w, t) for _bx, _by, w, t in rows)
        ys = [by for _bx, by, _w, _t in rows]
        dims[idx] = (max_w, (max(ys) - min(ys)) + BLOCK_FONT)
    out = []
    for item in blocks:
        idx, bx, by, w, t = item
        if idx in frac_map and idx in dims:
            max_w, h = dims[idx]
            fx, fy = frac_map[idx]
            bx += fx * max_w
            by += fy * h
        out.append((idx, bx, by, w, t))
    return out


def nudge_blocks_lh(blocks, lh_map, lh):
    """Feinschliff: fx × Blockbreite, fy_lh × Zeilenhöhe (dy<0 = nach oben)."""
    if not lh_map:
        return blocks
    dims = {}
    by_arc = {}
    for item in blocks:
        idx, bx, by, w, t = item
        by_arc.setdefault(idx, []).append((bx, by, w, t))
    for idx in lh_map:
        rows = by_arc.get(idx, [])
        if not rows:
            continue
        dims[idx] = max(line_w(w, t) for _bx, _by, w, t in rows)
    out = []
    for item in blocks:
        idx, bx, by, w, t = item
        if idx in lh_map and idx in dims:
            fx, fy_lh = lh_map[idx]
            bx += fx * dims[idx]
            by += fy_lh * lh
        out.append((idx, bx, by, w, t))
    return out


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
        margin = 0.0
        if style.get("outward"):
            n = (-n[0], -n[1])
            margin = font * style.get(
                "edge_margin_frac", INNER_EDGE_MARGIN_FRAC)
        pos = add(edge_pt, mul(n, inset + margin))
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
        out.append(f'    <g font-family="{FONT_DERIVED}" '
                   f'fill="{TXT_COLOR}" dominant-baseline="central" '
                   f'letter-spacing="1">')
        for item in inner_items:
            (px, py), ang, txt = item[0], item[1], item[2]
            size = item[3] if len(item) > 3 else INNER_FONT
            anch = item[4] if len(item) > 4 else "middle"
            base = item[5] if len(item) > 5 else "central"
            out.append(f'      <text x="0" y="0" text-anchor="{anch}" '
                       f'font-family="{FONT_DERIVED}" '
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
        out.append(f'    <g font-family="{FONT}" fill="{TXT_COLOR}" '
                   f'text-anchor="middle" dominant-baseline="central">')
        for item in label_items:
            if len(item) == 5:
                idx, px, py, ang, lines = item
            else:
                idx, px, py, ang, lines = None, *item
            za = zoom_attr(idx) if idx is not None else None
            metrics = label_line_metrics(lines)
            n_dir = direction_line_count(lines)
            gap = label_section_margin()
            spans = []
            for i, (t, sz, bold, lh) in enumerate(metrics):
                dy = 0.0 if i == 0 else metrics[i - 1][3]
                if i == n_dir and n_dir > 0:
                    dy += gap  # ueber dem Schlagsatz
                is_title = i >= n_dir
                family = FONT_DERIVED if is_title else FONT
                wt = "normal" if is_title else ("bold" if bold else "normal")
                spans.append(
                    f'<tspan x="0" dy="{dy:.2f}" font-size="{sz:.2f}" '
                    f'font-family="{family}" font-weight="{wt}">{t}</tspan>')
            extra = gap if n_dir else 0.0
            py = py - extra / 2.0  # Abstand Mini-Titel/Schlagsatz, Block bleibt zentriert
            text = (f'<text x="0" y="0" '
                    f'transform="translate({px:.2f},{py:.2f}) '
                    f'rotate({ang:.2f})">{"".join(spans)}</text>')
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
        out.append(f'    <g fill="none" stroke="{BLOCK_FRAME_STROKE}" '
                   f'stroke-width="{BLOCK_FRAME_SW}">')
        for idx, fx, fy, fw, fh in block_frame_rects(block_items):
            out.append(
                f'      <rect x="{fx:.2f}" y="{fy:.2f}" width="{fw:.2f}" '
                f'height="{fh:.2f}" rx="{BLOCK_FRAME_RX:.2f}" '
                f'ry="{BLOCK_FRAME_RX:.2f}"/>')
        out.append('    </g>')
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


def build_a2(write_files=False, a2_page=False):
    """Baut den A2-Inhalt. Gibt Dict mit svg, inner, Bloecken, Massen zurueck.

    write_files: SVG/Dreiecke-SVG schreiben (CLI). A0 ruft mit False auf.
    a2_page: A2-Ausgabe — Titel schmaler, Krankheit/Gesundheit eine
    Ueberschrifthoehe nach unten. A0 laesst beides unangetastet.
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

        labels, radial, blocks, labels_k, radial_k, blocks_k = yaml_arc_content()

        # Gesundheits-Inhalt in lokalen Koordinaten
        ges_labels, ges_radial, ges_radial_by_arc, ges_blocks = build_panel_content(
            local_arcs, lcentroid, labels, radial, blocks, LABEL_NUDGE, BLOCK_NUDGE)

        # Krankheits-Inhalt (dm-01k … dm-09k)
        kra_labels, kra_radial, kra_radial_by_arc, kra_blocks = build_panel_content(
            local_arcs, lcentroid, labels_k, radial_k, blocks_k,
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
        title_frac = A2_TITLE_WIDTH_FRAC if a2_page else MAIN_TITLE_WIDTH_FRAC
        MAIN_TITLE_FONT = ((title_frac * PAGE_W) / (0.52 * _title_len)) * 0.85
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
        BLOCK_PLACE_KRANK = {
            0: "above",
            1: "below",
            3: "left",
            4: "below",  # dm-02k unter dem Strahlenhalbkreis
            6: "above",  # dm-03k über dem Strahlenhalbkreis
            7: "below",  # dm-01k unter Strahlenhalbkreis (Feinposition via refit)
        }
        BLOCK_PLACE_GESUND = {
            **BLOCK_PLACE_KRANK,
            1: "above",  # dm-05g oberhalb des Strahlenhalbkreises
            3: "below",  # dm-06g unter dem Strahlenhalbkreis
            4: "below",  # dm-02g unter dem Strahlenhalbkreis (wie dm-06g)
            6: "right",  # dm-03g bleibt rechts
            7: "below",  # dm-01g unter dem Strahlenhalbkreis
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


        def equalize_block_pair_y(blocks, pair, skip=frozenset()):
            """7-Zeiler eines Paares auf dieselbe erste Zeile setzen."""
            a, b = pair
            if a in skip or b in skip:
                return blocks
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


        def match_block_y(blocks, src_idx, dst_idx):
            """dst_idx auf dieselbe erste Zeile wie src_idx setzen."""
            first = {}
            for item in blocks:
                idx, _bx, by, _w, _t = item
                if idx in (src_idx, dst_idx) and idx not in first:
                    first[idx] = by
            if src_idx not in first or dst_idx not in first:
                return blocks
            dy = first[src_idx] - first[dst_idx]
            return [
                (idx, bx, by + dy if idx == dst_idx else by, w, t)
                for idx, bx, by, w, t in blocks
            ]


        def fit_blocks_to_zoomed_arcs(blocks, arcs, radials, arc_zoom, block_place):
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
                preferred = block_place.get(idx, "left")
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


        def refit_below_centered(blocks, arc_idx, arcs, radials, arc_zoom,
                                 extra_lh=0):
            """7-Zeiler mittig unter fan_box, optional zusaetzliche lh nach unten."""
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

            entries = [(w, t) for idx, _bx, _by, w, t in blocks if idx == arc_idx]
            if not entries or arc_idx not in arc_zoom:
                return blocks
            x0, x1, _y0, y1 = fan_box(arc_idx)
            mid_x = (x0 + x1) / 2.0
            max_w = max(line_w(w, t) for w, t in entries)
            bx = mid_x - max_w / 2.0
            by0 = y1 + BLOCK_PAD + extra_lh * BLOCK_LH
            rest = [item for item in blocks if item[0] != arc_idx]
            rest.extend(
                (arc_idx, bx, by0 + i * BLOCK_LH, w, t)
                for i, (w, t) in enumerate(entries))
            return rest


        def refit_above_centered(blocks, arc_idx, arcs, radials, arc_zoom,
                                 extra_lh=0):
            """7-Zeiler mittig über fan_box, optional zusaetzliche lh nach oben."""
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

            entries = [(w, t) for idx, _bx, _by, w, t in blocks if idx == arc_idx]
            if not entries or arc_idx not in arc_zoom:
                return blocks
            x0, x1, y0, _y1 = fan_box(arc_idx)
            mid_x = (x0 + x1) / 2.0
            max_w = max(line_w(w, t) for w, t in entries)
            n = len(entries)
            block_h = (n - 1) * BLOCK_LH
            bx = mid_x - max_w / 2.0
            by0 = y0 - BLOCK_PAD - block_h - extra_lh * BLOCK_LH
            rest = [item for item in blocks if item[0] != arc_idx]
            rest.extend(
                (arc_idx, bx, by0 + i * BLOCK_LH, w, t)
                for i, (w, t) in enumerate(entries))
            return rest


        def refit_below_right_of(blocks, arc_idx, arcs, radials, arc_zoom,
                                 anchor_x, anchor_half_w, extra_lh=0):
            """7-Zeiler unter fan_box, rechts neben einem Anker (z. B. Kultur/Geist)."""
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

            entries = [(w, t) for idx, _bx, _by, w, t in blocks if idx == arc_idx]
            if not entries or arc_idx not in arc_zoom:
                return blocks
            _x0, _x1, _y0, y1 = fan_box(arc_idx)
            bx = anchor_x + anchor_half_w + BLOCK_PAD_RIGHT
            by0 = y1 + BLOCK_PAD + extra_lh * BLOCK_LH
            rest = [item for item in blocks if item[0] != arc_idx]
            rest.extend(
                (arc_idx, bx, by0 + i * BLOCK_LH, w, t)
                for i, (w, t) in enumerate(entries))
            return rest


        def mirror_above_horizontal(blocks, ref_idx, mir_idx, arcs, radials, arc_zoom):
            """mir_idx horizontal spiegeln zu ref_idx (gleiche y-Höhe)."""
            def rad_w(word, z):
                return 0.65 * RAD_FONT * z * len(word)

            def fan_mid(idx):
                origin, z, shift = arc_zoom[idx]
                center, chord, bulge, n, off = arcs[idx]
                xs = []
                for p in arc_points(center, chord, bulge, off, n):
                    xs.append(css_zoom_point(p, origin, z, shift)[0])
                for item in radials:
                    if item[0] != idx:
                        continue
                    (px, py), _a, _an, word, d = item[1], item[2], item[3], item[4], item[5]
                    p0 = css_zoom_point((px, py), origin, z, shift)
                    wlen = rad_w(word, z)
                    xs += [p0[0], add(p0, mul(d, wlen))[0], add(p0, mul(d, -wlen))[0]]
                return (min(xs) + max(xs)) / 2.0

            ref_rows = [(bx, by, w, t) for idx, bx, by, w, t in blocks if idx == ref_idx]
            mir_entries = [(w, t) for idx, _bx, _by, w, t in blocks if idx == mir_idx]
            if not ref_rows or not mir_entries:
                return blocks
            max_w_r = max(line_w(w, t) for _bx, _by, w, t in ref_rows)
            bx_r, by_r, _w0, _t0 = ref_rows[0]
            offset_x = (bx_r + max_w_r / 2.0) - fan_mid(ref_idx)
            max_w_m = max(line_w(w, t) for w, t in mir_entries)
            bx_m = fan_mid(mir_idx) - offset_x - max_w_m / 2.0
            rest = [item for item in blocks if item[0] != mir_idx]
            rest.extend(
                (mir_idx, bx_m, by_r + i * BLOCK_LH, w, t)
                for i, (w, t) in enumerate(mir_entries))
            return rest


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
            kra_blocks_t, kra_arcs, kra_radial_t, kra_arc_zoom, BLOCK_PLACE_KRANK)
        kra_blocks_t = refit_below_centered(
            kra_blocks_t, 4, kra_arcs, kra_radial_t, kra_arc_zoom)
        kra_blocks_t = refit_above_centered(
            kra_blocks_t, 0, kra_arcs, kra_radial_t, kra_arc_zoom)
        kra_blocks_t = refit_above_centered(
            kra_blocks_t, 6, kra_arcs, kra_radial_t, kra_arc_zoom)
        kultur_pos, _kultur_txt = kra_verts[2]
        kultur_half_w = text_w("Kultur/Geist", V_FONT_SIZE) / 2.0
        kra_blocks_t = refit_below_right_of(
            kra_blocks_t, 7, kra_arcs, kra_radial_t, kra_arc_zoom,
            kultur_pos[0], kultur_half_w)
        kra_blocks_t = equalize_block_pair_y(kra_blocks_t, BASE_ARC_PAIR, skip={4})
        kra_blocks_t = nudge_blocks(kra_blocks_t, BLOCK_FIT_NUDGE_KRANK)
        kra_blocks_t = nudge_blocks_frac(kra_blocks_t, BLOCK_FIT_NUDGE_FRAC_KRANK)
        kra_blocks_t = mirror_above_horizontal(
            kra_blocks_t, 0, 6, kra_arcs, kra_radial_t, kra_arc_zoom)

        ges_arc_zoom = panel_arc_zooms(
            ges_arcs, ges_labels_t, ges_radial_t, ges_inner_t, ARC_CLEAR_GESUND)
        equalize_arc_pair_shift(ges_arc_zoom, ges_arcs, BASE_ARC_PAIR)
        ges_blocks_t = fit_blocks_to_zoomed_arcs(
            ges_blocks_t, ges_arcs, ges_radial_t, ges_arc_zoom, BLOCK_PLACE_GESUND)
        ges_blocks_t = refit_below_centered(
            ges_blocks_t, 3, ges_arcs, ges_radial_t, ges_arc_zoom, extra_lh=3)
        ges_blocks_t = refit_below_centered(
            ges_blocks_t, 4, ges_arcs, ges_radial_t, ges_arc_zoom, extra_lh=3)
        ges_blocks_t = match_block_y(ges_blocks_t, 3, 4)  # dm-02g = Höhe dm-06g
        ges_blocks_t = nudge_blocks(ges_blocks_t, BLOCK_FIT_NUDGE_GESUND)
        ges_blocks_t = nudge_blocks_frac(ges_blocks_t, BLOCK_FIT_NUDGE_FRAC_GESUND)
        ges_blocks_t = nudge_blocks_lh(ges_blocks_t, BLOCK_FIT_NUDGE_LH_GESUND, BLOCK_LH)

        # ---------------------------------------------------------------- SVG schreiben
        out = []
        out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                   f'xmlns:xlink="http://www.w3.org/1999/xlink" '
                   f'viewBox="0 0 {PAGE_W:.2f} {PAGE_H:.2f}" '
                   f'width="{PAGE_W:.0f}" height="{PAGE_H:.0f}">')
        out.append(font_face_svg())
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

        # Sektionsworte als Hintergrund (2× Titelgroesse; Farbe = BG − 5 %)
        wm_font = MAIN_TITLE_FONT * WATERMARK_SCALE
        krank_wm_y = (main_title_y + MAIN_TITLE_LINE_H * 2 + MAIN_TITLE_FONT * 0.38
                      - 0.8 * wm_font)  # 80 % Texthöhe nach oben
        ges_wm_y = ges_a[1] - (kra_a[1] - krank_wm_y)
        if a2_page:
            krank_wm_y += wm_font
            ges_wm_y += wm_font
        bg_for_sample = BG_IMAGE if os.path.isfile(BG_IMAGE) else None
        krank_wm_fill = sample_bg_darker(
            bg_for_sample, PAGE_W, PAGE_H, PAGE_W / 2, krank_wm_y)
        ges_wm_fill = sample_bg_darker(
            bg_for_sample, PAGE_W, PAGE_H, PAGE_W / 2, ges_wm_y)


        def watermark(txt, y, fill):
            out.append(f'  <text x="{PAGE_W / 2:.2f}" y="{y:.2f}" '
                       f'font-family="{FONT}" font-size="{wm_font:.2f}" '
                       f'font-weight="bold" fill="{fill}" '
                       f'fill-opacity="{WATERMARK_OPACITY}" '
                       f'text-anchor="middle" dominant-baseline="central" '
                       f'letter-spacing="2">{txt}</text>')


        watermark("Krankheit", krank_wm_y, krank_wm_fill)
        watermark("Gesundheit", ges_wm_y, ges_wm_fill)

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

        # Seite ohne <svg>-Rahmen, ohne Seiten-Rect/Hintergrund (A0 legt beides selbst)
        inner_start = 1
        while inner_start < len(out) and (
            out[inner_start].lstrip().startswith("<rect ")
            or out[inner_start].lstrip().startswith("<defs")
            or "hintergrund" in out[inner_start]
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
            "tri_h": SIDE * math.sqrt(3) / 2 * scale,
            "krank_wm_y": krank_wm_y,
            "ges_wm_y": ges_wm_y,
            "kra_blocks": kra_blocks,
            "ges_blocks": ges_blocks,
            "seven_blocks": kra_blocks + ges_blocks,
            "kra_radial": kra_radial_t,
            "ges_radial": ges_radial_t,
            "kra_leit_font": INNER_FONT * VORRECHTE_SCALE,
            "heading_font": INNER_FONT * VORRECHTE_SCALE * HEADING_TO_LEIT_SCALE,
        }
    finally:
        (R, FONT_SIZE, LINE_H, BLOCK_FONT, BLOCK_LH,
         RAD_FONT, RAD_GAP, V_FONT_SIZE, INNER_FONT) = _saved


def write_a2_jpg(svg, dpi=300):
    """A2-SVG nach output/halbkreise.jpg rendern (wie generate-a0.py)."""
    out_dir = os.path.join(_DIR, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_svg = os.path.join(out_dir, ".a2-render.svg")
    out_jpg = os.path.join(out_dir, "halbkreise.jpg")
    jpg_w = round(420.0 / 25.4 * dpi)
    jpg_h = round(594.0 / 25.4 * dpi)
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write(svg if svg.endswith("\n") else svg + "\n")

    asset_dir = os.path.join(_DIR, "assets")
    tmp_copies = []
    font_copy = copy_derived_font(out_dir)
    if font_copy:
        tmp_copies.append(font_copy)
    for name in os.listdir(asset_dir):
        src = os.path.join(asset_dir, name)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(out_dir, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            tmp_copies.append(dst)

    png_tmp = os.path.join(out_dir, ".a2-render.png")
    try:
        subprocess.run(
            ["rsvg-convert", "-w", str(jpg_w), "-h", str(jpg_h),
             out_svg, "-o", png_tmp],
            check=True,
        )
        subprocess.run(
            ["magick", png_tmp,
             "-density", str(dpi), "-units", "PixelsPerInch",
             "-quality", "92", out_jpg],
            check=True,
        )
        print(f"wrote {out_jpg}  {jpg_w}×{jpg_h} @ {dpi} dpi")
    finally:
        for tmp in [png_tmp, out_svg]:
            if os.path.isfile(tmp):
                os.remove(tmp)
        for path in tmp_copies:
            if os.path.isfile(path):
                os.remove(path)


if __name__ == "__main__":
    result = build_a2(a2_page=True)
    write_a2_jpg(result["svg"])
