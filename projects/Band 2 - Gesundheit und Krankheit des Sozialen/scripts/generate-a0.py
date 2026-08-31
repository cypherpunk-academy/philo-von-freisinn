#!/usr/bin/env python3
"""
Soziale Gesundheit auf DIN A0 — A2-Inhalt, Freiraum unter beiden Tafeln ausgeglichen.

Je 7er-Gruppe ein Rechteck mit den YAML-Erklaertexten (ohne Titel/Schlagwort),
zwei Spalten: 1. innen, 2. aussen (halb versetzt), 3. wieder innen (Krankheit);
Gesundheit: aussen / innen / aussen.

A2 kommt aus build_a2() in halbkreise.py (kein SVG-Parse).
Krankheit rueckt etwas nach unten; Gesundheit so, dass der Freiraum darunter
dem Freiraum unter der Krankheit entspricht.
"""
import importlib.util
import math
import os
import re
import subprocess
import xml.sax.saxutils as xml

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_PATH = os.path.join(_DIR, "content", "soziale-gesundheit.yaml")
HINTERGRUND = "hintergrund-web.jpg"
OUT_SVG = os.path.join(_DIR, "output", ".a0-render.svg")  # temp, deleted after JPG

A0_W, A0_H = 8410.0, 11890.0
SHIFT_Y = 0.0
PAGE_MARGIN = 64.0
# Krankheit mit Halbkreisen etwas nach unten
KRA_NUDGE_Y = 320.0
# Druck: A0 = 841×1189 mm → 9933×14043 px bei 300 dpi
DPI = 300
OUT_JPG = os.path.join(_DIR, "output", "halbkreise-a0.jpg")
JPG_W = round(841.0 / 25.4 * DPI)  # 9933
JPG_H = round(1189.0 / 25.4 * DPI)  # 14043

CARD_FILL = "#f4f1ea"
CARD_FILL_K = "#f0ebe3"
CARD_FILL_G = "#eceae3"
CARD_STROKE = "#b7b1a6"
LINE_COLOR = "#6a655c"

CARD_PAD = 14.0
CARD_RX = 14.0
COL_GAP = 16.0
ROW_GAP = 12.0
GROUP_GAP = 28.0
# Extra zwischen 1. und 3. Gruppe derselben Spalte (innen oben / aussen unten)
STACK_EXTRA = 180.0  # ~18 mm, Daumenbreit

# Vorübergehend ausgeblendet (Layout folgt)
HIDDEN_GROUPS = frozenset()

# yaml-id, Seite des 7er-Blocks, Tafel, Richtungs-Label
GROUPS = [
    ("dm-04k", "left",  "kra", "Recht \u2192 Wirtschaft"),
    ("dm-05k", "left",  "kra", "Wirtschaft \u2192 Recht"),
    ("dm-06k", "left",  "kra", "Wirtschaft \u2192 Geist"),
    ("dm-03k", "right", "kra", "Recht \u2192 Geist"),
    ("dm-01k", "right", "kra", "Geist \u2192 Recht"),
    ("dm-02k", "right", "kra", "Geist \u2192 Wirtschaft"),
    ("dm-04g", "left",  "ges", "Recht \u2192 Wirtschaft"),
    ("dm-05g", "left",  "ges", "Wirtschaft \u2192 Recht"),
    ("dm-06g", "left",  "ges", "Wirtschaft \u2192 Geist"),
    ("dm-03g", "right", "ges", "Recht \u2192 Geist"),
    ("dm-01g", "right", "ges", "Geist \u2192 Recht"),
    ("dm-02g", "right", "ges", "Geist \u2192 Wirtschaft"),
]


def _a2_module():
    path = os.path.join(_DIR, "scripts", "generate-a2.py")
    spec = importlib.util.spec_from_file_location("halbkreise", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A2 = _a2_module()
FONT = A2.FONT
TXT_COLOR = A2.TXT_COLOR
BG = A2.BG
text_w = A2.text_w


def wrap_text(text, size, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, size) <= max_w or not cur:
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
    # Trailing Einzel-# oder ' #' am Ende
    body = re.sub(r"\s*#\s*$", "", body).strip()
    return body


def load_yaml_fields():
    with open(YAML_PATH, encoding="utf-8") as f:
        src = f.read()
    fields = {}
    for m in re.finditer(r"- id: (dm-\d+[gk])\n(.*?)(?=\n  - id: |\n\Z)", src, re.S):
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
            body = _clean_aspect_text(am.group(3))
            aspects.append({
                "schlagwort": am.group(1).strip(),
                "schlagsatz": am.group(2).strip(),
                "text": body,
            })
        fields[fid] = {
            "titel": titel_m.group(1) if titel_m else "",
            "richtung": richtung_m.group(1) if richtung_m else "",
            "aspects": aspects,
        }
    return fields


PARA_GAP = 1.15  # Abstand zwischen den 7 Aspekten (in lh)
TITLE_BODY_GAP = 0.15  # kleiner Zusatz nach der Titelzeile
FILL_OPACITY = 0.2

# Fächer-Layout (linke + rechte Halbkreise Krankheit/Gesundheit)
FAN_LEFT_Y_SHIFT = -260.0    # dm-04k nach oben (dm-04g nutzt Abstand zu dm-05k)
FAN_ORDER = (
    "dm-04k", "dm-05k", "dm-06k",
    "dm-03k", "dm-01k", "dm-02k",
    "dm-04g", "dm-05g", "dm-06g",
    "dm-03g", "dm-01g", "dm-02g",
)
FAN_GROUPS = {
    # --- Krankheit links ---
    "dm-04k": {
        "panel": "kra", "side": "left",
        "arc": 0, "open": "left", "y_mode": "center",
        "heading_room": True,
        "y_shift": FAN_LEFT_Y_SHIFT,
        "y_shift_heading_lh": 0.5,  # halbe Überschrift-Zeilenhöhe nach unten
        "x_shift": 780.0,
        "heading_lines": ["Die Gewalt setzt", "den Preis"],
        "heading_x": "first_block",
    },
    "dm-05k": {
        "panel": "kra", "side": "left",
        "arc": 1, "open": "right", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-04k",
        "x_shift": 1280.0,
        "heading_lines": ["Das Geld kauft", "das Recht"],
    },
    "dm-06k": {
        "panel": "kra", "side": "left",
        "arc": 3, "open": "left", "y_mode": "below",
        "below": "dm-04k",
        "heading_room": True,
        "v_align": "top",
        "y_shift_heading_lh": 1.0,   # ganze Überschrift-Zeilenhöhe nach unten
        "x_shift": 780.0,
        "x_shift_text_frac": 0.2,    # 20 % Textbreite nach rechts
        "heading_lines": ["Der Profit kauft", "die Wahrheit"],
        "heading_x": "first_block",
    },
    # --- Krankheit rechts (spiegelbildlich zu 04/05/06k) ---
    "dm-03k": {
        "panel": "kra", "side": "right",
        "arc": 6, "open": "right", "y_mode": "center",
        "heading_room": True,
        "y_shift": FAN_LEFT_Y_SHIFT,
        "y_shift_heading_lh": 0.5,
        "x_shift": 780.0,
        "heading_lines": ["Die Macht beherrscht", "den Geist"],
        "heading_x": "first_block",
    },
    "dm-01k": {
        "panel": "kra", "side": "right",
        "arc": 7, "open": "left", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-03k",
        "x_shift": 1280.0,
        "heading_lines": ["Ideologie macht sich", "zum Gesetz"],
    },
    "dm-02k": {
        "panel": "kra", "side": "right",
        "arc": 4, "open": "right", "y_mode": "below",
        "below": "dm-03k",
        "heading_room": True,
        "v_align": "top",
        "y_shift_heading_lh": 1.0,
        "x_shift": 780.0,
        "x_shift_text_frac": -0.2,   # spiegelbildlich zu dm-06k (+0.2)
        "heading_lines": ["Das Dogma diktiert", "die Produktion"],
        "heading_x": "first_block",
    },
    # --- Gesundheit links ---
    "dm-04g": {
        "panel": "ges", "side": "left",
        "arc": 0, "open": "right", "y_mode": "heading_gap",
        "ref_bottom": "dm-05k",
        "heading_gap_ref": ("dm-06k", "dm-04k"),
        "heading_room": True,
        "y_shift_heading_lh": 0.5,
        "y_shift_block": 2,  # zwei Textblöcke nach unten
        "x_shift": 1280.0,
        "heading_lines": ["Das Gesetz sichert", "den fairen Rahmen"],
        "heading_x": "first_block",
    },
    "dm-05g": {
        "panel": "ges", "side": "left",
        "arc": 1, "open": "left", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-04g",
        "y_shift_block": 1,  # eine Textbox-Höhe nach oben (gegenüber 2)
        "x_shift": 780.0,
        "x_shift_text_frac": 0.15,   # 15 % Textbreite nach rechts (ohne Überschrift)
        "heading_x_compensate_text_frac": True,
        "heading_lines": ["Die Wirtschaft trägt", "den Staat"],
    },
    "dm-06g": {
        "panel": "ges", "side": "left",
        "arc": 3, "open": "right", "y_mode": "below",
        "below": "dm-04g",
        "heading_room": True,
        "v_align": "top",
        "y_shift_heading_lh": 1.0,
        "x_shift": 1280.0,
        "x_shift_text_frac": -0.2,   # 20 % Textbreite nach links
        "heading_lines": ["Die Wirtschaft versorgt", "den Geist"],
        "heading_x": "first_block",
    },
    # --- Gesundheit rechts (spiegelbildlich zu 04/05/06g) ---
    "dm-03g": {
        "panel": "ges", "side": "right",
        "arc": 6, "open": "left", "y_mode": "heading_gap",
        "ref_bottom": "dm-01k",
        "heading_gap_ref": ("dm-02k", "dm-03k"),
        "heading_room": True,
        "y_shift_heading_lh": 0.5,
        "y_shift_block": 2.5,  # +0.5 Texthöhe nach unten
        "x_shift": 1280.0,
        "heading_lines": ["Der Staat bewahrt", "die Freiheit des Einzelnen"],
        "heading_x": "first_block",
    },
    "dm-01g": {
        "panel": "ges", "side": "right",
        "arc": 7, "open": "right", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-03g",
        "y_shift_block": 0,  # eine Texthöhe nach oben (war 1)
        "y_shift_tri_frac": 1.0,  # eine Dreieckshöhe nach unten
        "x_shift": 780.0,
        "x_shift_text_frac": -0.15,  # spiegelbildlich zu dm-05g (+0.15)
        "heading_x_compensate_text_frac": True,
        "heading_lines": ["Sachkenntnis prägt", "das Recht"],
    },
    "dm-02g": {
        "panel": "ges", "side": "right",
        "arc": 4, "open": "left", "y_mode": "below",
        "below": "dm-03g",
        "heading_room": True,
        "v_align": "top",
        "y_shift_heading_lh": 1.0,
        "y_shift_tri_frac": 1.0,  # eine Dreieckshöhe nach unten
        "x_shift": 1280.0,
        "x_shift_text_frac": 0.2,    # spiegelbildlich zu dm-06g (−0.2)
        "heading_lines": ["Fähigkeiten befruchten", "die Wirtschaft"],
        "heading_x": "first_block",
    },
}
FAN_ARC_HEIGHT = 2600.0
FAN_ARC_BULGE = 600.0
FAN_PAIR_GAP = 48.0  # horizontaler Abstand zwischen beiden Fächern
# Vertikale Abstände im Fächer (in lh), vgl. Karten-Beispiel
FAN_TITLE_BODY_GAP = 0.0    # Überschrift → eigener Text (= normaler lh-Schritt)
FAN_ASPECT_GAP = 1.375     # Text darüber → nächste Überschrift (halbiert)
FAN_FIELD_HEADING_GAP = 1.0  # Feld-Titel → erster Aspekt-Titel


def wrap_aspects(aspects, font, inner_w):
    """Je Aspekt: Titelzeile(n) 'Schlagwort: Schlagsatz' + Erklaertext."""
    out = []
    for a in aspects:
        title = f"{a['schlagwort']}: {a['schlagsatz']}"
        out.append({
            "title": wrap_text(title, font, inner_w),
            "body": wrap_text(a["text"], font, inner_w),
        })
    return out


def group_height(blocks, font, lh):
    """Hoehe passend zu draw_group (ohne Cursor-Bug)."""
    n_lines = 0
    for b in blocks:
        n_lines += len(b["title"]) + len(b["body"])
    n_aspects = len(blocks)
    # zwischen Titel und Body je Aspekt + zwischen Aspekten
    n_title_body = n_aspects  # je einmal TITLE_BODY_GAP
    n_gaps = max(0, n_aspects - 1)
    # first baseline bei CARD_PAD + font*0.45; last line + font*0.55 + CARD_PAD
    return (
        CARD_PAD * 2
        + font
        + max(0, n_lines - 1) * lh
        + n_title_body * lh * TITLE_BODY_GAP
        + n_gaps * lh * PARA_GAP
    )


def draw_group(x, y, w, h, font, lh, blocks, fill):
    ty = y + CARD_PAD + font * 0.45
    esc = xml.escape
    tx = x + CARD_PAD
    parts = [
        f'    <rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'rx="{CARD_RX:.2f}" ry="{CARD_RX:.2f}" fill="{fill}" '
        f'fill-opacity="{FILL_OPACITY}" stroke="{CARD_STROKE}" '
        f'stroke-width="1.2" stroke-opacity="{FILL_OPACITY}"/>',
        f'    <text font-family="{FONT}" font-size="{font:.2f}" '
        f'fill="{TXT_COLOR}" dominant-baseline="central">',
    ]
    cursor = ty
    for bi, block in enumerate(blocks):
        if bi:
            cursor += lh * PARA_GAP
        for i, line in enumerate(block["title"]):
            parts.append(
                f'      <tspan x="{tx:.2f}" y="{cursor:.2f}" '
                f'font-weight="bold">{esc(line)}</tspan>')
            cursor += lh
        cursor += lh * TITLE_BODY_GAP
        for line in block["body"]:
            parts.append(
                f'      <tspan x="{tx:.2f}" y="{cursor:.2f}">'
                f'{esc(line)}</tspan>')
            cursor += lh
    parts.append("    </text>")
    return "\n".join(parts)


def draw_aspect_bare(x, y, w, font, lh, block, title_body_gap=TITLE_BODY_GAP):
    """Einzelnen Aspekt ohne Karten-Rechteck zeichnen."""
    esc = xml.escape
    ty = y + font * 0.45
    parts = [
        f'    <text font-family="{FONT}" font-size="{font:.2f}" '
        f'fill="{TXT_COLOR}" dominant-baseline="central">',
    ]
    cursor = ty
    for line in block["title"]:
        parts.append(
            f'      <tspan x="{x:.2f}" y="{cursor:.2f}" '
            f'font-weight="bold">{esc(line)}</tspan>')
        cursor += lh
    cursor += lh * title_body_gap
    for line in block["body"]:
        parts.append(
            f'      <tspan x="{x:.2f}" y="{cursor:.2f}">'
            f'{esc(line)}</tspan>')
        cursor += lh
    parts.append("    </text>")
    return "\n".join(parts)


def draw_fan_heading(cx, y, lines, font_size):
    """Feld-Titel über einem Fächer (Größe wie Vorrechte/Wettbewerb)."""
    esc = xml.escape
    lh = font_size * 1.12
    parts = [
        f'    <text font-family="{FONT}" font-size="{font_size:.2f}" '
        f'font-weight="bold" fill="{TXT_COLOR}" text-anchor="middle" '
        f'dominant-baseline="central">',
    ]
    cursor = y
    for i, line in enumerate(lines):
        parts.append(
            f'      <tspan x="{cx:.2f}" y="{cursor:.2f}">{esc(line)}</tspan>')
        if i + 1 < len(lines):
            cursor += lh
    parts.append("    </text>")
    return "\n".join(parts)


def fan_block_height(block, font, lh):
    """Höhe eines Fächer-Aspekts passend zu draw_aspect_bare."""
    n_title = len(block["title"])
    n_body = len(block["body"])
    return (
        font
        + max(0, n_title - 1) * lh
        + lh  # normaler Schritt Titel → erster Body
        + FAN_TITLE_BODY_GAP * lh
        + max(0, n_body - 1) * lh
    )


def aspect_height(block, font, lh):
    """Höhe eines einzelnen Aspekt-Textblocks."""
    n = len(block["title"]) + len(block["body"])
    return font + max(0, n - 1) * lh + lh * TITLE_BODY_GAP


def fan_heading_x(placed, col_w, min_x, max_x, cfg):
    """Horizontaler Anker für die Fächer-Überschrift."""
    mode = cfg.get("heading_x", "fan_center")
    if mode == "first_block" and placed:
        first = placed[0]
        frac = cfg.get("heading_x_frac", 0.5)
        shift = cfg.get("heading_x_shift", 0.0)
        return first["x"] + col_w * frac + shift
    return (min_x + max_x) / 2.0


def fan_y_from_heading(target_heading_y, blocks, font, lh, leit_font,
                       arc_height, v_align="center"):
    """y_top so setzen, dass die Feld-Überschrift bei target_heading_y beginnt."""
    head_lh = leit_font * 1.12
    head_block_h = leit_font + head_lh
    n = len(blocks)
    heights = [fan_block_height(b, font, lh) for b in blocks]
    stack_h = sum(heights) + max(0, n - 1) * FAN_ASPECT_GAP * lh
    y_cursor = (target_heading_y + lh * FAN_FIELD_HEADING_GAP
                + head_block_h - leit_font * 0.45)
    if v_align == "top":
        return y_cursor
    return y_cursor - max(0.0, (arc_height - stack_h) / 2.0)


def fan_y_top(cfg, fan_centers, fan_bottom, ray_center, head_block_h, lh):
    """Vertikaler Start des Fächer-Stapels."""
    mode = cfg.get("y_mode", "center")
    if mode == "center":
        y_top = ray_center - FAN_ARC_HEIGHT / 2
    elif mode == "top_at_sibling_center":
        ref = cfg.get("relative_to", "dm-04k")
        if ref not in fan_centers:
            raise SystemExit(f"{ref} muss vor dem relativen Fächer platziert sein")
        y_top = fan_centers[ref]
    elif mode == "below":
        ref = cfg.get("below", "dm-04k")
        if ref not in fan_bottom:
            raise SystemExit(f"{ref} muss vor dem unteren Fächer platziert sein")
        y_top = fan_bottom[ref] + lh * FAN_ASPECT_GAP
    else:
        raise SystemExit(f"Unbekannter y_mode: {mode}")
    if cfg.get("heading_room"):
        y_top += head_block_h + lh * FAN_FIELD_HEADING_GAP
    return y_top + cfg.get("y_shift", 0.0)


def _ray_center_y(radial, arc_idx, panel_dy):
    ys = [py + panel_dy for idx, (px, py), *_ in radial if idx == arc_idx]
    if not ys:
        raise SystemExit(f"Keine Strahlen fuer Bogen {arc_idx}")
    return (min(ys) + max(ys)) / 2.0


def place_fan(blocks, *, open_side, y_top, gutter_edge, col_w,
              arc_height, arc_bulge, x_shift, font, lh, meta,
              v_align="center", side="left"):
    """Sieben Aspekte entlang eines Halbkreis-Fächers platzieren.

    side=left:  gutter_edge = rechter Rand des linken Gutters
    side=right: gutter_edge = linker Rand des rechten Gutters (spiegelbildlich)
    open_side: Öffnungsrichtung des Bogens (visuell)
    x_shift > 0: zum Diagramm hin
    """
    n = len(blocks)
    heights = [fan_block_height(b, font, lh) for b in blocks]
    stack_h = sum(heights) + max(0, n - 1) * FAN_ASPECT_GAP * lh
    if v_align == "top":
        y_cursor = y_top
    else:
        y_cursor = y_top + max(0.0, (arc_height - stack_h) / 2.0)
    items = []
    for i in range(n):
        t = math.pi * i / (n - 1) if n > 1 else math.pi / 2
        if side == "left":
            if open_side == "left":
                bx = (gutter_edge - col_w
                      - arc_bulge * (1.0 - math.sin(t)) + x_shift)
            else:
                right_edge = (gutter_edge - col_w - arc_bulge
                              - FAN_PAIR_GAP + x_shift)
                bx = right_edge - col_w - arc_bulge * math.sin(t)
        else:
            # Spiegelung der linken Formeln um die Seitenmitte
            if open_side == "right":
                bx = (gutter_edge
                      + arc_bulge * (1.0 - math.sin(t)) - x_shift)
            else:
                bx = (gutter_edge + col_w + arc_bulge + FAN_PAIR_GAP
                      - x_shift + arc_bulge * math.sin(t))
        bh = heights[i]
        items.append({
            "x": bx, "y": y_cursor, "w": col_w, "h": bh,
            "block": blocks[i],
            **meta,
        })
        y_cursor += bh + FAN_ASPECT_GAP * lh
    center_y = y_top + arc_height / 2.0
    return items, center_y


def clamp_fan_margin(placed, *, x_min=PAGE_MARGIN, x_max=None, y_max=None):
    """Fächer-Aspekte in die Seite clampen (linker/rechter/unterer Rand)."""
    if not placed:
        return
    min_x = min(p["x"] for p in placed)
    if min_x < x_min:
        dx = x_min - min_x
        for p in placed:
            p["x"] += dx
    if x_max is not None:
        max_r = max(p["x"] + p["w"] for p in placed)
        if max_r > x_max:
            dx = max_r - x_max
            for p in placed:
                p["x"] -= dx
    if y_max is not None:
        overflow = max(p["y"] + p["h"] for p in placed) - y_max
        if overflow > 0:
            for p in placed:
                p["y"] -= overflow


def place_staggered(groups, x0, y0, y_limit, col_w, font, lh,
                    side="left", start="inner"):
    """Zwei Spalten, vertikal halb versetzt.

    start=inner: 1. innen, 2. aussen, 3. innen (Krankheit).
    start=outer: 1. aussen, 2. innen, 3. aussen (Gesundheit).
    side=left: innen = rechte Spalte; side=right: innen = linke Spalte.
    """
    inner_w = col_w - 2 * CARD_PAD
    # physisch: 0 = linke Spalte des Paares, 1 = rechte
    col_x = [x0, x0 + col_w + COL_GAP]
    if side == "left":
        inner_col, outer_col = 1, 0
    else:
        inner_col, outer_col = 0, 1
    if start == "outer":
        col_order = [outer_col, inner_col, outer_col]
    else:
        col_order = [inner_col, outer_col, inner_col]

    col_y = [None, None]
    placed, overflow = [], []
    first_h = None
    for i, g in enumerate(groups):
        blocks = wrap_aspects(g["aspects"], font, inner_w)
        h = group_height(blocks, font, lh)
        col = col_order[i % len(col_order)]
        if col_y[col] is None:
            # 2./4. … Gruppe: halb versetzt
            staggered = (i % 2 == 1)
            col_y[col] = y0 + ((first_h or h) / 2.0 if staggered else 0.0)
        y = col_y[col]
        item = {
            **g,
            "blocks": blocks,
            "x": col_x[col],
            "y": y,
            "w": col_w,
            "h": h,
            "col": col,
        }
        if y + h > y_limit + 1:
            overflow.append(g)
            continue
        placed.append(item)
        # Nach der 1. Gruppe: groesserer Abstand zur 3. (gleiche Spalte, andere Richtung)
        gap = GROUP_GAP + (STACK_EXTRA if i == 0 else 0.0)
        col_y[col] = y + h + gap
        if i == 0 and first_h is None:
            first_h = h
            second_col = col_order[1]
            if col_y[second_col] is None:
                col_y[second_col] = y0 + first_h / 2.0
    return placed, overflow


def _shift_panel(inner, gid, dy, watermark=None):
    """Panel-Gruppe (und optional Wasserzeichen) vertikal verschieben."""
    if abs(dy) < 0.01:
        return inner
    inner = re.sub(
        rf'<g id="{gid}">',
        f'<g id="{gid}" transform="translate(0,{dy:.2f})">',
        inner,
        count=1,
    )
    if watermark:
        def _bump_y(m):
            return f'{m.group(1)}{float(m.group(2)) + dy:.2f}{m.group(3)}'

        inner = re.sub(
            rf'(<text\b[^>]*\by=")(\d+(?:\.\d+)?)("[^>]*>{re.escape(watermark)}</text>)',
            _bump_y,
            inner,
            count=1,
        )
    return inner


def main():
    a2 = A2.build_a2(write_files=False)
    inner = a2["inner"]
    seven = a2["seven_blocks"]
    a2_w, a2_h = a2["page_w"], a2["page_h"]
    shift_x = (A0_W - a2_w) / 2.0
    leit_font = a2.get("kra_leit_font", a2["block_font"] * 2.0)
    heading_text_h = leit_font * 1.12  # eine Überschrift-Zeilenhöhe

    kra_dy = KRA_NUDGE_Y + heading_text_h
    # Gesundheit so, dass Freiraum unter beiden Tafeln (7er-Bloecke) gleich ist
    kra_bot = max(b["y1"] for b in a2["kra_blocks"]) + kra_dy
    ges_top_a2 = min(b["y0"] for b in a2["ges_blocks"])
    ges_bot_a2 = max(b["y1"] for b in a2["ges_blocks"])
    # free_kra = ges_top - kra_bot; free_ges = page_bottom - ges_bot; equalize
    ges_dy = (A0_H - PAGE_MARGIN - ges_bot_a2 - ges_top_a2 + kra_bot) / 2.0

    inner = _shift_panel(inner, "krankheit", kra_dy, watermark="Krankheit")
    inner = _shift_panel(inner, "gesundheit", ges_dy, watermark="Gesundheit")

    # Hintergrundschriften: Farbe am finalen A0-Ort (BG − 10 %)
    hg = os.path.join(_DIR, "assets", HINTERGRUND)
    krank_y_a0 = SHIFT_Y + a2.get("krank_wm_y", 0.0) + kra_dy
    ges_y_a0 = SHIFT_Y + a2.get("ges_wm_y", 0.0) + ges_dy
    wm_x_a0 = shift_x + a2_w / 2.0
    krank_fill = A2.sample_bg_darker(hg, A0_W, A0_H, wm_x_a0, krank_y_a0)
    ges_fill = A2.sample_bg_darker(hg, A0_W, A0_H, wm_x_a0, ges_y_a0)
    inner = A2.recolor_watermark(inner, "Krankheit", krank_fill)
    inner = A2.recolor_watermark(inner, "Gesundheit", ges_fill)
    print(f"Wasserzeichen  Krankheit@{krank_y_a0:.0f}→{krank_fill}  "
          f"Gesundheit@{ges_y_a0:.0f}→{ges_fill}")

    fields = load_yaml_fields()

    by_first = {(b["panel"], b["words"][0]): b for b in seven}

    font = a2["block_font"]
    lh = a2["block_lh"]
    gutter_w = shift_x - PAGE_MARGIN - 20
    col_w = (gutter_w - COL_GAP) / 2
    left_x = PAGE_MARGIN
    right_x = shift_x + a2_w + 20

    kra_y0 = 70.0 + kra_dy
    ges_y0 = ges_top_a2 + ges_dy
    # Kra darf in die Mitte ragen: gestapelte Spalte ist innen, Gesundheit stapelt aussen
    y_limit = A0_H - PAGE_MARGIN
    y_limit_kra = y_limit

    prepared = []
    for yaml_id, side, panel, label in GROUPS:
        if yaml_id in HIDDEN_GROUPS:
            continue
        field = fields.get(yaml_id)
        if not field or len(field["aspects"]) != 7:
            raise SystemExit(
                f"{yaml_id}: {0 if not field else len(field['aspects'])} Aspekte")
        first = field["aspects"][0]["schlagwort"]
        blk = by_first.get((panel, first))
        if not blk:
            raise SystemExit(f"7er-Block nicht gefunden fuer {first} ({yaml_id})")
        bx = shift_x + blk["x"]
        by_mid = SHIFT_Y + (blk["y0"] + blk["y1"]) / 2
        by_mid += kra_dy if panel == "kra" else ges_dy
        prepared.append({
            "yaml_id": yaml_id,
            "label": label,
            "panel": panel,
            "side": side,
            "fill": CARD_FILL_K if panel == "kra" else CARD_FILL_G,
            "aspects": field["aspects"],
            "anchor": (bx, by_mid),
            "block": blk,
        })

    def gutter_x(side):
        return left_x if side == "left" else right_x

    # --- Fächer-Layout links + rechts (Krankheit/Gesundheit) ---
    fan_items = []
    fan_headings = []
    fan_by_id = {g["yaml_id"]: g for g in prepared if g["yaml_id"] in FAN_GROUPS}
    regular = [g for g in prepared if g["yaml_id"] not in FAN_GROUPS]
    gutter_right_left = shift_x - 40          # rechter Rand linker Gutter
    gutter_left_right = A0_W - gutter_right_left  # spiegelbildlich
    inner_w = col_w - 2 * CARD_PAD
    fan_centers = {}
    fan_bottom = {}
    fan_heading_top = {}
    tri_h = a2.get("tri_h", 0.0)

    for yaml_id in FAN_ORDER:
        fg = fan_by_id.get(yaml_id)
        if not fg:
            continue
        cfg = FAN_GROUPS[yaml_id]
        blocks = wrap_aspects(fg["aspects"], font, inner_w)
        head_lines = cfg.get("heading_lines") or [fields[yaml_id]["titel"], ""]
        head_lh = leit_font * 1.12
        head_block_h = leit_font + head_lh
        panel = cfg.get("panel", "kra")
        fan_side = cfg.get("side", "left")
        panel_dy = kra_dy if panel == "kra" else ges_dy
        radial = a2["kra_radial"] if panel == "kra" else a2["ges_radial"]
        y_mode = cfg.get("y_mode", "center")
        v_align = cfg.get("v_align", "center")
        if y_mode == "heading_gap":
            ref_bottom = cfg["ref_bottom"]
            ref_h, ref_b = cfg["heading_gap_ref"]
            if ref_h not in fan_heading_top or ref_b not in fan_bottom:
                raise SystemExit(
                    f"heading_gap fuer {yaml_id}: {ref_h}/{ref_b} fehlt")
            if ref_bottom not in fan_bottom:
                raise SystemExit(f"ref_bottom {ref_bottom} fehlt fuer {yaml_id}")
            gap = fan_heading_top[ref_h] - fan_bottom[ref_b]
            target_head_y = fan_bottom[ref_bottom] + gap
            y_top = fan_y_from_heading(
                target_head_y, blocks, font, lh, leit_font,
                FAN_ARC_HEIGHT, v_align=v_align)
        else:
            ray_center = _ray_center_y(radial, cfg["arc"], panel_dy)
            y_top = fan_y_top(cfg, fan_centers, fan_bottom, ray_center,
                              head_block_h, lh)
        y_top += cfg.get("y_shift_heading_lh", 0.0) * head_lh
        y_top += cfg.get("y_shift_block", 0) * fan_block_height(blocks[0], font, lh)
        y_top += cfg.get("y_shift_tri_frac", 0.0) * tri_h
        text_dx = cfg.get("x_shift_text_frac", 0.0) * col_w
        x_shift = cfg.get("x_shift", 0.0)
        meta = {"anchor": fg["anchor"], "side": fg["side"]}
        gutter_edge = (gutter_right_left if fan_side == "left"
                       else gutter_left_right)
        placed, center_y = place_fan(
            blocks,
            open_side=cfg["open"],
            y_top=y_top,
            gutter_edge=gutter_edge,
            col_w=col_w,
            arc_height=FAN_ARC_HEIGHT,
            arc_bulge=FAN_ARC_BULGE,
            x_shift=x_shift,
            font=font,
            lh=lh,
            meta=meta,
            v_align=v_align,
            side=fan_side,
        )
        if text_dx:
            for p in placed:
                p["x"] += text_dx
        if fan_side == "left":
            clamp_fan_margin(placed, y_max=y_limit)
        else:
            clamp_fan_margin(
                placed, x_min=gutter_left_right - FAN_ARC_BULGE * 2,
                x_max=A0_W - PAGE_MARGIN, y_max=y_limit)
        fan_items.extend(placed)
        fan_centers[yaml_id] = center_y
        fan_bottom[yaml_id] = max(p["y"] + p["h"] for p in placed)

        min_x = min(p["x"] for p in placed)
        max_x = max(p["x"] + p["w"] for p in placed)
        min_y = min(p["y"] for p in placed)
        head_y = min_y - lh * FAN_FIELD_HEADING_GAP - head_block_h + leit_font * 0.45
        fan_heading_top[yaml_id] = head_y
        head_x = fan_heading_x(placed, col_w, min_x, max_x, cfg)
        if cfg.get("heading_x_compensate_text_frac"):
            head_x -= text_dx
        fan_headings.append({
            "x": head_x,
            "y": head_y,
            "lines": head_lines,
            "font": leit_font,
        })

    clusters = []
    overflow = []
    for side in ("left", "right"):
        x = gutter_x(side)
        kra_batch = [g for g in regular if g["side"] == side and g["panel"] == "kra"]
        placed_k, left_k = place_staggered(
            kra_batch, x, kra_y0, y_limit_kra, col_w, font, lh,
            side=side, start="inner")
        clusters.extend(placed_k)
        overflow.extend(left_k)
        ges_batch = [g for g in regular if g["side"] == side and g["panel"] == "ges"]
        placed_g, left_g = place_staggered(
            ges_batch, x, ges_y0, y_limit, col_w, font, lh,
            side=side, start="outer")
        clusters.extend(placed_g)
        overflow.extend(left_g)

    if overflow:
        extra, still = place_staggered(
            overflow, PAGE_MARGIN, ges_y0, y_limit, col_w, font, lh, side="left")
        clusters.extend(extra)
        overflow = still
        if still:
            raise SystemExit(f"{len(still)} Gruppen passen nicht auf die Seite")

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {A0_W:.2f} {A0_H:.2f}" '
        f'width="{A0_W:.0f}" height="{A0_H:.0f}">')
    out.append(
        f'  <rect x="0" y="0" width="{A0_W:.2f}" height="{A0_H:.2f}" fill="{BG}"/>')
    hg = os.path.join(_DIR, "assets", HINTERGRUND)
    if os.path.isfile(hg):
        out.append(
            f'  <image href="{HINTERGRUND}" xlink:href="{HINTERGRUND}" '
            f'x="0" y="0" width="{A0_W:.2f}" height="{A0_H:.2f}" '
            f'preserveAspectRatio="none"/>')

    out.append(f'  <g fill="none" stroke="{LINE_COLOR}" stroke-width="1.1" '
               f'stroke-opacity="0.35">')
    for cl in clusters:
        if cl["side"] == "left":
            attach_x = cl["x"] + cl["w"]
        else:
            attach_x = cl["x"]
        attach_y = cl["y"] + cl["h"] / 2
        ax, ay = cl["anchor"]
        mx = (ax + attach_x) / 2
        out.append(
            f'    <path d="M {ax:.1f},{ay:.1f} C {mx:.1f},{ay:.1f} '
            f'{mx:.1f},{attach_y:.1f} {attach_x:.1f},{attach_y:.1f}"/>')
    out.append("  </g>")

    for cl in clusters:
        out.append(draw_group(
            cl["x"], cl["y"], cl["w"], cl["h"],
            font, lh, cl["blocks"], cl["fill"]))

    # Fächer-Blöcke (ohne Karten-Rechteck)
    for fi in fan_items:
        out.append(draw_aspect_bare(
            fi["x"], fi["y"], fi["w"], font, lh, fi["block"],
            title_body_gap=FAN_TITLE_BODY_GAP))

    for fh in fan_headings:
        out.append(draw_fan_heading(
            fh["x"], fh["y"], fh["lines"], fh["font"]))

    out.append(f'  <g id="a2-content" transform="translate({shift_x:.2f},{SHIFT_Y:.2f})">')
    out.append(inner.rstrip())
    out.append("  </g>")
    out.append("</svg>")

    svg = "\n".join(out) + "\n"
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"DIN A0  {A0_W:.0f}×{A0_H:.0f}")
    print(f"kra_dy={kra_dy:.0f}  ges_dy={ges_dy:.0f}  "
          f"ges {ges_top_a2 + ges_dy:.0f}…{ges_bot_a2 + ges_dy:.0f}  "
          f"free≈{(ges_top_a2 + ges_dy) - kra_bot:.0f}")
    print(f"7er-Bloecke: {len(seven)}  Gruppen: {len(clusters)}  "
          f"Faecher: {len(fan_headings)}")
    print(f"Ueberlauf unten: {len(overflow)}")
    # JPG in Druckauflösung (A0 @ 300 dpi)
    # rsvg-convert resolves image hrefs relative to the SVG's directory only,
    # so temporarily copy referenced assets into output/ for rendering.
    import shutil
    out_dir = os.path.dirname(OUT_SVG)
    asset_dir = os.path.join(_DIR, "assets")
    tmp_copies = []
    for name in os.listdir(asset_dir):
        dst = os.path.join(out_dir, name)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(asset_dir, name), dst)
            tmp_copies.append(dst)

    png_tmp = os.path.join(out_dir, ".a0-render.png")
    try:
        subprocess.run(
            ["rsvg-convert", "-w", str(JPG_W), "-h", str(JPG_H),
             OUT_SVG, "-o", png_tmp],
            check=True,
        )
        subprocess.run(
            ["magick", png_tmp,
             "-density", str(DPI), "-units", "PixelsPerInch",
             "-quality", "92", OUT_JPG],
            check=True,
        )
        print(f"wrote {OUT_JPG}  {JPG_W}×{JPG_H} @ {DPI} dpi")
    finally:
        for tmp in [png_tmp, OUT_SVG]:
            if os.path.isfile(tmp):
                os.remove(tmp)
        for f in tmp_copies:
            if os.path.isfile(f):
                os.remove(f)


if __name__ == "__main__":
    main()
