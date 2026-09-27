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
YAML_PATH = os.path.join(
    _DIR, "content", "Gesundheit und Krankheit des Sozialen Organismus.yaml")
HINTERGRUND = "hintergrund-web.jpg"
OUT_SVG = os.path.join(_DIR, "output", ".a0-render.svg")  # temp, deleted after JPG

A0_W, A0_H = 8410.0, 11890.0
SHIFT_Y = 0.0
PAGE_MARGIN = 64.0
# Krankheit mit Halbkreisen etwas nach unten
KRA_NUDGE_Y = 320.0
# Druck: A0 = 841×1189 mm → 9933×14043 px bei 300 dpi
DPI = 300
OUT_JPG = os.path.join(
    _DIR, "output",
    "gesundheit-und-krankheit-des-sozialen-organismus-a0.jpg")
OUT_PDF = os.path.join(
    _DIR, "output",
    "gesundheit-und-krankheit-des-sozialen-organismus-a0.pdf")
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

# Sozialer Hauptsatz (Steiner) — Mitte zwischen Krankheit und Gesundheit
HAUPTSATZ = (
    "„Das Heil einer Gesamtheit von zusammenarbeitenden Menschen "
    "ist um so größer, je weniger der einzelne die Erträgnisse seiner "
    "Leistungen für sich beansprucht, das heißt, je mehr er von diesen "
    "Erträgnissen an seine Mitarbeiter abgibt, und je mehr seine eigenen "
    "Bedürfnisse nicht aus seinen Leistungen, sondern aus den Leistungen "
    "der anderen befriedigt werden.“"
)
HAUPTSATZ_COLOR = "#7A4A6E"   # gedämpftes Violett (Klint-nah)
HAUPTSATZ_FONT = 93.6         # war 104; −10 %
HAUPTSATZ_WIDTH_FRAC = 0.5265 # war 0.585; −10 %
HAUPTSATZ_LH = 1.69           # relativ zur Fontgröße
HAUPTSATZ_AUTHOR = "Rudolf Steiner"
HAUPTSATZ_AUTHOR_SCALE = 0.72  # Namenszeile etwas kleiner als das Zitat

# Philo-Avatar im unteren Freifeld (Gelb/Blau-Grenze, etwas rechts)
AVATAR_SRC = os.path.join(_DIR, "..", "..", "assets", "avatar.png")
AVATAR_HREF = "avatar.png"
AVATAR_CAPTION = "Philo von Freisinn"
AVATAR_TRI_FRAC = 2.0 / 3.0
AVATAR_X_FRAC = 0.625  # Mitte auf der Gelb–Blau-Grenze
QR_SRC = os.path.join(_DIR, "assets", "qr-github.svg")
QR_HREF = "qr-github.svg"
QR_URL = (
    "https://github.com/cypherpunk-academy/philo-von-freisinn/tree/main/"
    "projects/Band%202%20-%20Gesundheit%20und%20Krankheit%20des%20Sozialen%20Organismus/output"
)
QR_SIZE = 300.0  # 3 cm; 1 SVG-Einheit = 0.1 mm
_DE_MONTHS = {
    1: "Jan.", 2: "Feb.", 3: "März", 4: "Apr.", 5: "Mai", 6: "Juni",
    7: "Juli", 8: "Aug.", 9: "Sep.", 10: "Okt.", 11: "Nov.", 12: "Dez.",
}

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
load_yaml_fields = A2.load_yaml_fields


def git_version_meta():
    """Kurze Git-Kennung und Datum der HEAD-Version (Hilfsrepo)."""
    repo = os.path.normpath(os.path.join(_DIR, "..", ".."))
    sha = subprocess.check_output(
        ["git", "-C", repo, "rev-parse", "--short=10", "HEAD"],
        text=True,
    ).strip()
    ymd = subprocess.check_output(
        ["git", "-C", repo, "log", "-1", "--format=%cs"],
        text=True,
    ).strip()
    year, month, day = (int(p) for p in ymd.split("-"))
    date = f"{day:02d}. {_DE_MONTHS[month]} {year}"
    return sha, date


def philo_intro_text(date):
    return (
        "Hallo, ich bin Philo, ein KI-Assistent und ein großer Fan der Bücher "
        "»Die Philosophie der Freiheit« und »Die Kernpunkte der sozialen Frage« "
        "und des damit Verbundenen. Diese Übersicht ist Teil meiner Wissensbasis, "
        "auf der ich Fragen zum Thema Dreigliederung des sozialen Organismus, "
        "zur Open Source-Kultur und zur Gesellschaft allgemein beantworte. "
        "Kurator ist Michael Schmidt (m@michaelschmidt.berlin). "
        f"Diese Version findest du über den QR-Code; sie ist vom {date}."
    )


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
        "arc": 0, "open": "left", "y_mode": "page_top",
        "heading_room": True,
        "v_align": "top",
        "x_shift": 780.0,
        "heading_x": "first_block",
        "heading_align": "end",  # rechtsbündig zur unteren Zeile
    },
    "dm-05k": {
        "panel": "kra", "side": "left",
        "arc": 1, "open": "right", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-04k",
        "x_shift": 1280.0,
        "align_heading_to": {
            "yaml_id": "dm-04k",
            "schlagwort": "Willkürpreis",
            "y_shift_lh": 0.4,  # ein klein wenig nach unten
        },
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
        "heading_x": "first_block",
    },
    # --- Krankheit rechts (spiegelbildlich zu 04/05/06k) ---
    "dm-03k": {
        "panel": "kra", "side": "right",
        "arc": 6, "open": "right", "y_mode": "page_top",
        "heading_room": True,
        "v_align": "top",
        "x_shift": 780.0,
        "heading_x": "first_block",
        "heading_x_frac": 0.0,   # linker Textrand
        "heading_align": "text-start",  # linksbündig mit dem Text
    },
    "dm-01k": {
        "panel": "kra", "side": "right",
        "arc": 7, "open": "left", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-03k",
        "x_shift": 1280.0,
        "heading_lines": ["Die Weltsicht wird", "zum Gesetz"],
        "align_heading_to": {
            "yaml_id": "dm-03k",
            "schlagwort": "Goldener Zügel",
        },
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
        "heading_x": "first_block",
        "heading_lines": ["Der Glaube diktiert", "die Produktion"],
    },
    # --- Gesundheit links ---
    "dm-04g": {
        "panel": "ges", "side": "left",
        "arc": 0, "open": "right", "y_mode": "heading_gap",
        "ref_bottom": "dm-05k",
        "heading_gap_ref": ("dm-06k", "dm-04k"),
        "heading_room": True,
        "v_align": "top",
        "x_shift": 1280.0,
        "heading_x": "first_block",
        "heading_x_frac": 1.0,   # rechter Textrand
        "heading_align": "text-end",  # rechtsbündig mit dem Text
        "align_heading_to": {
            "yaml_id": "dm-06k",
            "schlagwort": "Bestellung",
        },
    },
    "dm-05g": {
        "panel": "ges", "side": "left",
        "arc": 1, "open": "left", "y_mode": "top_at_sibling_center",
        "relative_to": "dm-04g",
        "y_shift_block": 1.5,  # bleibt stehen, wenn dm-04g um 0.5 nach oben geht
        "x_shift": 780.0,
        "x_shift_text_frac": 0.15,   # 15 % Textbreite nach rechts
        "heading_x": "first_block",
        "heading_x_frac": 0.0,   # linker Textrand
        "heading_align": "text-start",  # linksbündig mit dem Text
        "heading_lines": ["Die Wirtschaft", "trägt den Staat"],
        "align_heading_to": {
            "yaml_id": "dm-04g",
            "schlagwort": "Eigentumszeit",
        },
    },
    "dm-06g": {
        "panel": "ges", "side": "left",
        "arc": 3, "open": "right", "y_mode": "below",
        "below": "dm-04g",
        "heading_room": True,
        "v_align": "top",
        "x_shift": 1280.0,
        "x_shift_text_frac": -0.2,   # 20 % Textbreite nach links
        "heading_x": "first_block",
        "heading_x_frac": 1.0,   # rechter Rand des ersten Texts
        "heading_align": "text-end",  # rechtsbündig mit dem Text
        "heading_lines": ["Die Wirtschaft", "versorgt den Geist"],
        "align_heading_to": {
            "yaml_id": "dm-05g",
            "schlagwort": "Versorgung",
        },
        "shift_down_to_page": True,
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
        "heading_x": "first_block",
        "align_heading_to": {
            "yaml_id": "dm-02k",
            "schlagwort": "Kennzahl",
        },
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
        "heading_align": "middle",
        "heading_lines": ["Sachkenntnis prägt", "das Recht"],
        "align_heading_to": {
            "yaml_id": "dm-03g",
            "schlagwort": "Schutzraum",
        },
    },
    "dm-02g": {
        "panel": "ges", "side": "right",
        "arc": 4, "open": "left", "y_mode": "below",
        "below": "dm-03g",
        "heading_room": True,
        "v_align": "top",
        "y_shift_heading_lh": 1.0,
        "x_shift": 1280.0,
        "x_shift_text_frac": 0.2,    # spiegelbildlich zu dm-06g (−0.2)
        "heading_x": "first_block",
    },
}
FAN_ARC_HEIGHT = 2600.0
FAN_ARC_BULGE = 600.0
FAN_PAIR_GAP = 48.0  # horizontaler Abstand zwischen beiden Fächern
FAN_TEXT_WIDTH_SCALE = 1.05  # Textkästen etwas breiter → weniger Zeilen
# Vertikale Abstände im Fächer (in lh), vgl. Karten-Beispiel
FAN_TITLE_BODY_GAP = 0.0    # Überschrift → eigener Text (= normaler lh-Schritt)
FAN_ASPECT_GAP = 1.0       # mindestens eine Leerzeile zwischen den Texten
FAN_FIELD_HEADING_GAP = 1.0  # Feld-Titel → erster Aspekt-Titel
KEYWORD_ABOVE = 1.05       # Schlagwort über der Titel-Grundlinie (draw_aspect_bare)


def wrap_aspects(aspects, font, inner_w, *, split_keyword=False, body_key="kurztext"):
    """Je Aspekt: Titelzeile(n) + Erklaertext.

    split_keyword: Schlagsatz als Titel, Schlagwort separat (A0-Fächer).
    body_key: A0 setzt kurztext; fehlt er, fällt auf text zurück.
    """
    out = []
    for a in aspects:
        if split_keyword:
            title = wrap_text(a["schlagsatz"], font, inner_w)
            keyword = a["schlagwort"]
        else:
            title = wrap_text(f"{a['schlagwort']}: {a['schlagsatz']}", font, inner_w)
            keyword = None
        body = (a.get(body_key) or "").strip() or a.get("text") or ""
        out.append({
            "title": title,
            "body": wrap_text(body, font, inner_w),
            "keyword": keyword,
            "text": body,
            "schlagsatz": a["schlagsatz"],
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


def draw_aspect_bare(x, y, w, font, lh, block, title_body_gap=TITLE_BODY_GAP,
                     baseline_font=None, keyword=None, keyword_opacity=0.3):
    """Einzelnen Aspekt ohne Karten-Rechteck zeichnen.

    keyword: Schlagwort über der Überschrift, ohne den Abstand nach oben zu ändern.
    """
    esc = xml.escape
    base = baseline_font if baseline_font is not None else font
    ty = y + base * 0.45
    parts = []
    if keyword:
        kw_y = ty - font * 1.05
        parts.append(
            f'    <text x="{x:.2f}" y="{kw_y:.2f}" '
            f'font-family="{FONT}" font-size="{font:.2f}" font-weight="bold" '
            f'fill="{TXT_COLOR}" fill-opacity="{keyword_opacity:.2f}" '
            f'dominant-baseline="central">{esc(keyword)}</text>')
    parts.append(
        f'    <text font-family="{FONT}" font-size="{font:.2f}" '
        f'fill="{TXT_COLOR}" dominant-baseline="central">')
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


def draw_fan_heading(cx, y, lines, font_size, align="middle"):
    """Feld-Titel über einem Fächer (Special Elite, 15 % größer als Vorrechte).

    align=middle: Zeilen zentriert um cx.
    align=end: rechtsbündig; cx ist weiterhin der Mittel-Anker der
    *letzten* Zeile (die bleibt stehen), die übrigen Zeilen rücken nach.
    align=start: linksbündig zur letzten Zeile (letzte Zeile bleibt).
    align=text-start: alle Zeilen am Anker cx linksbündig (Textrand).
    align=text-end: alle Zeilen am Anker cx rechtsbündig (Textrand).
    """
    esc = xml.escape
    lh = font_size * 1.12
    if align == "text-start":
        anchor = "start"
        x = cx
    elif align == "text-end":
        anchor = "end"
        x = cx
    else:
        anchor = align if align in ("start", "middle", "end") else "middle"
        x = cx
        if anchor == "end" and lines:
            x = cx + text_w(lines[-1], font_size, bold=True) / 2.0
        elif anchor == "start" and lines:
            x = cx - text_w(lines[-1], font_size, bold=True) / 2.0
    parts = [
        f'    <text font-family="{A2.FONT_DERIVED}" font-size="{font_size:.2f}" '
        f'fill="{TXT_COLOR}" text-anchor="{anchor}" '
        f'dominant-baseline="central">',
    ]
    cursor = y
    for i, line in enumerate(lines):
        parts.append(
            f'      <tspan x="{x:.2f}" y="{cursor:.2f}">{esc(line)}</tspan>')
        if i + 1 < len(lines):
            cursor += lh
    parts.append("    </text>")
    return "\n".join(parts)


def draw_hauptsatz(cx, cy, lines, font_size, color, author=None):
    """Sozialen Hauptsatz zentriert, kursiv, in der freien Bandmitte."""
    esc = xml.escape
    lh = font_size * HAUPTSATZ_LH
    total_h = max(0, len(lines) - 1) * lh
    y0 = cy - total_h / 2.0
    parts = [
        f'    <text font-family="{FONT}" font-size="{font_size:.2f}" '
        f'font-style="italic" fill="{color}" text-anchor="middle" '
        f'dominant-baseline="central">',
    ]
    cursor = y0
    for i, line in enumerate(lines):
        parts.append(
            f'      <tspan x="{cx:.2f}" y="{cursor:.2f}">{esc(line)}</tspan>')
        if i + 1 < len(lines):
            cursor += lh
    parts.append("    </text>")
    if author:
        author_size = font_size * HAUPTSATZ_AUTHOR_SCALE
        author_y = cursor + lh * 0.85
        parts.append(
            f'    <text x="{cx:.2f}" y="{author_y:.2f}" '
            f'font-family="{FONT}" font-size="{author_size:.2f}" '
            f'font-style="italic" fill="{color}" text-anchor="middle" '
            f'dominant-baseline="central">{esc(author)}</text>')
    return "\n".join(parts)


def draw_philo_avatar(cx, cy, diameter, caption, font_size, intro_lines=None,
                      intro_x=None, intro_font=None, qr_size=None, qr_cx=None):
    """Runder Avatar mit Namenszeile — Mitte auf (cx, cy).

    intro_lines: kursiver Vorstellungstext links vom Bild.
    QR zentriert unter dem Namen, damit die rechte Textspalte frei bleibt.
    """
    r = diameter / 2.0
    clip_id = "philo-avatar-clip"
    cap_y = cy + r + font_size * 0.95
    esc = xml.escape
    parts = [
        "  <defs>",
        f'    <clipPath id="{clip_id}">',
        f'      <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>',
        "    </clipPath>",
        "  </defs>",
        f'  <image href="{AVATAR_HREF}" xlink:href="{AVATAR_HREF}" '
        f'x="{cx - r:.2f}" y="{cy - r:.2f}" '
        f'width="{diameter:.2f}" height="{diameter:.2f}" '
        f'clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice"/>',
        f'  <text x="{cx:.2f}" y="{cap_y:.2f}" '
        f'font-family="{A2.FONT_DERIVED}" font-size="{font_size:.2f}" '
        f'fill="{TXT_COLOR}" text-anchor="middle" '
        f'dominant-baseline="central">{esc(caption)}</text>',
    ]
    isize = intro_font if intro_font is not None else HAUPTSATZ_FONT
    qsize = qr_size if qr_size is not None else QR_SIZE
    pad = qsize * 0.06
    cap_bottom = cap_y + font_size * 0.42
    qr_y = cap_bottom + font_size * 0.4
    qr_x = cx - qsize / 2.0
    if qr_cx is not None:
        qr_x = qr_cx - qsize / 2.0
    parts.append(
        f'  <rect x="{qr_x - pad:.2f}" y="{qr_y - pad:.2f}" '
        f'width="{qsize + 2 * pad:.2f}" height="{qsize + 2 * pad:.2f}" '
        f'rx="{pad:.2f}" fill="{BG}"/>')
    parts.append(
        f'  <image href="{QR_HREF}" xlink:href="{QR_HREF}" '
        f'x="{qr_x:.2f}" y="{qr_y:.2f}" '
        f'width="{qsize:.2f}" height="{qsize:.2f}" '
        f'preserveAspectRatio="xMidYMid meet"/>')
    if intro_lines:
        x = intro_x if intro_x is not None else cx - r - isize * 0.7
        lh = isize * HAUPTSATZ_LH
        total_h = max(0, len(intro_lines) - 1) * lh
        y0 = cy - total_h / 2.0
        parts.append(
            f'  <text font-family="{FONT}" font-size="{isize:.2f}" '
            f'font-style="italic" fill="{TXT_COLOR}" text-anchor="end" '
            f'dominant-baseline="central">')
        cursor = y0
        for i, line in enumerate(intro_lines):
            parts.append(
                f'    <tspan x="{x:.2f}" y="{cursor:.2f}">{esc(line)}</tspan>')
            if i + 1 < len(intro_lines):
                cursor += lh
        parts.append("  </text>")
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


def estimate_aspect_fit(fan_items, font_draw, lh_draw):
    """Wie stark die 84 Aspekt-Texte gekürzt werden müssten, um ohne Überlauf zu passen."""
    by_id = {}
    for p in fan_items:
        yid = p.get("yaml_id")
        if not yid:
            continue
        by_id.setdefault(yid, []).append(p)
    n = 0
    n_over = 0
    chars_now = 0
    chars_fit = 0
    lines_now = 0
    lines_fit = 0
    over_fracs = []
    for items in by_id.values():
        items = sorted(items, key=lambda p: p["y"])
        for i, p in enumerate(items):
            db = p.get("draw_block") or p["block"]
            drawn_h = fan_block_height(db, font_draw, lh_draw)
            if i + 1 < len(items):
                avail = items[i + 1]["y"] - p["y"]
            else:
                avail = p["h"]
            n += 1
            body = db.get("text") or ""
            n_title = len(db["title"])
            n_body = len(db["body"])
            n_lines = n_title + n_body
            fit_lines = max(1, int(round((avail - font_draw) / lh_draw)) + 1)
            body_fit_lines = max(0, fit_lines - n_title)
            frac = 1.0 if n_body == 0 else min(1.0, body_fit_lines / n_body)
            chars_now += len(body)
            chars_fit += int(len(body) * frac)
            lines_now += n_lines
            lines_fit += min(n_lines, fit_lines)
            if drawn_h > avail + 1:
                n_over += 1
                over_fracs.append(1.0 - frac)
    cut_pct = (1.0 - chars_fit / chars_now) * 100 if chars_now else 0.0
    return {
        "n": n,
        "n_over": n_over,
        "cut_pct": cut_pct,
        "chars_now": chars_now,
        "chars_fit": chars_fit,
        "lines_now": lines_now,
        "lines_fit": lines_fit,
        "median_cut": (
            100 * sorted(over_fracs)[len(over_fracs) // 2] if over_fracs else 0.0),
    }


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
    if mode == "page_top":
        y_top = PAGE_MARGIN
    elif mode == "center":
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


def clamp_fan_margin(placed, *, x_min=PAGE_MARGIN, x_max=None):
    """Fächer-Aspekte in die Seite clampen (linker/rechter Rand).

    Vertikal nicht nach oben ziehen: das würde in den vorigen Aspekt laufen.
    """
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


def cascade_fan_down(placed, font, lh):
    """Abstand innerhalb einer 7er-Gruppe; andere Fächer bleiben unberührt."""
    if len(placed) < 2:
        return
    gap = lh * FAN_ASPECT_GAP + font * KEYWORD_ABOVE
    for i in range(1, len(placed)):
        prev = placed[i - 1]
        min_y = prev["y"] + prev["h"] + gap
        dy = min_y - placed[i]["y"]
        if dy > 0.5:
            for p in placed[i:]:
                p["y"] += dy


def lift_fan_onto_page(placed, y_max, others, font, lh, extra_top=0.0):
    """Ganzen Fächer nach oben, nur in freien Raum, wenn er unter den Seitenrand läuft."""
    if not placed:
        return 0.0
    overflow = max(p["y"] + p["h"] for p in placed) - y_max
    if overflow <= 1:
        return 0.0
    gap = FAN_ASPECT_GAP * lh
    max_up = overflow
    first = True
    for p in placed:
        top = p["y"] - (extra_top if first else font * 1.05)
        item_gap = 0.0 if first else gap
        first = False
        for o in others:
            overlap = (
                min(p["x"] + p["w"], o["x"] + o["w"])
                - max(p["x"], o["x"]))
            if overlap < 0.45 * min(p["w"], o["w"]):
                continue
            room = top - (o["y"] + o["h"]) - item_gap
            max_up = min(max_up, max(0.0, room))
    min_y = min(p["y"] for p in placed)
    max_up = min(max_up, max(0.0, min_y - extra_top - PAGE_MARGIN))
    if max_up > 1:
        for p in placed:
            p["y"] -= max_up
    return max_up


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
    a2 = A2.build_a2(write_files=False, draw_seven_liners=False)
    inner = a2["inner"]
    seven = a2["seven_blocks"]
    a2_w, a2_h = a2["page_w"], a2["page_h"]
    shift_x = (A0_W - a2_w) / 2.0
    leit_font = a2.get("kra_leit_font", a2["block_font"] * 2.0)
    heading_font = a2.get(
        "heading_font", leit_font * getattr(A2, "HEADING_TO_LEIT_SCALE", 1.15))
    heading_text_h = heading_font * 1.12  # eine Überschrift-Zeilenhöhe

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
    # Sichtbare Strahlen-Schlagwortgröße = RAD_FONT × ARC_ZOOM
    font_draw = a2.get("rad_font", font) * A2.ARC_ZOOM
    lh_draw = font_draw * (lh / font) if font else lh
    gutter_w = shift_x - PAGE_MARGIN - 20
    col_w = (gutter_w - COL_GAP) / 2 * FAN_TEXT_WIDTH_SCALE
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
        head_max = text_w("Die Wirtschaft versorgt", heading_font)
        head_lines = cfg.get("heading_lines") or wrap_text(
            fields[yaml_id]["titel"], heading_font, head_max)
        head_lh = heading_font * 1.12
        head_block_h = heading_font + head_lh
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
                target_head_y, blocks, font, lh, heading_font,
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
        meta = {"anchor": fg["anchor"], "side": fg["side"], "yaml_id": yaml_id}
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
        draw_blocks = wrap_aspects(
            fg["aspects"], font_draw, inner_w, split_keyword=True)
        for p, db in zip(placed, draw_blocks):
            p["draw_block"] = db
            p["h"] = fan_block_height(db, font_draw, lh_draw)
        if fan_side == "left":
            clamp_fan_margin(placed)
        else:
            clamp_fan_margin(
                placed, x_min=gutter_left_right - FAN_ARC_BULGE * 2,
                x_max=A0_W - PAGE_MARGIN)
        cascade_fan_down(placed, font_draw, lh_draw)
        extra_top = 0.0
        if cfg.get("heading_room"):
            extra_top = (lh * FAN_FIELD_HEADING_GAP + head_block_h
                         - heading_font * 0.45)
        lifted = lift_fan_onto_page(
            placed, y_limit, fan_items, font_draw, lh_draw, extra_top=extra_top)
        past_page = [p for p in placed if p["y"] + p["h"] > y_limit + 1]
        if past_page:
            print(f"  {yaml_id}: {len(past_page)} Aspekte unter dem Seitenrand "
                  f"(y={max(p['y']+p['h'] for p in placed):.0f} > {y_limit:.0f})")
        elif lifted > 1:
            print(f"  {yaml_id}: {lifted:.0f} nach oben, bleibt auf der Seite")
        fan_items.extend(placed)
        fan_centers[yaml_id] = center_y
        fan_bottom[yaml_id] = max(p["y"] + p["h"] for p in placed)

        min_x = min(p["x"] for p in placed)
        max_x = max(p["x"] + p["w"] for p in placed)
        min_y = min(p["y"] for p in placed)
        head_y = min_y - lh * FAN_FIELD_HEADING_GAP - head_block_h + heading_font * 0.45
        fan_heading_top[yaml_id] = head_y
        head_x = fan_heading_x(placed, col_w, min_x, max_x, cfg)
        if cfg.get("heading_x_compensate_text_frac"):
            head_x -= text_dx
        fan_headings.append({
            "id": yaml_id,
            "x": head_x,
            "y": head_y,
            "lines": head_lines,
            "font": heading_font,
            "align": cfg.get("heading_align", "middle"),
        })
        align = cfg.get("align_heading_to")
        if align:
            target = None
            for p in fan_items:
                db = p.get("draw_block") or p["block"]
                if (p.get("yaml_id") == align["yaml_id"]
                        and db.get("keyword") == align["schlagwort"]):
                    target = p
                    break
            if target is None:
                raise SystemExit(
                    f"{yaml_id}: align_heading_to {align} nicht gefunden")
            dy = (target["y"] - head_y
                  + align.get("y_shift_lh", 0.0) * head_lh)
            for p in placed:
                p["y"] += dy
            head_y += dy
            fan_headings[-1]["y"] = head_y
            fan_heading_top[yaml_id] = head_y
            fan_bottom[yaml_id] = max(p["y"] + p["h"] for p in placed)
            fan_centers[yaml_id] = center_y + dy
            print(f"  {yaml_id}: Überschrift auf {align['schlagwort']} "
                  f"({dy:+.0f})")

    by_fan = {}
    for p in fan_items:
        by_fan.setdefault(p.get("yaml_id"), []).append(p)
    for yaml_id in FAN_ORDER:
        group = by_fan.get(yaml_id)
        if not group:
            continue
        cfg = FAN_GROUPS[yaml_id]
        extra_top = 0.0
        if cfg.get("heading_room"):
            extra_top = (lh * FAN_FIELD_HEADING_GAP + heading_font * 2.12
                         - heading_font * 0.45)
        others = [p for p in fan_items if p.get("yaml_id") != yaml_id]
        lift_fan_onto_page(
            group, y_limit, others, font_draw, lh_draw, extra_top=extra_top)
    g06 = by_fan.get("dm-06g") or []
    if g06:
        overflow = max(p["y"] + p["h"] for p in g06) - y_limit
        if overflow > 1:
            for fid in ("dm-04g", "dm-05g", "dm-06g"):
                for p in by_fan.get(fid, []):
                    p["y"] -= overflow
            print(f"  dm-04g/05g/06g: {overflow:.0f} nach oben, bleibt auf der Seite")
    for fh in fan_headings:
        group = by_fan.get(fh["id"], [])
        if not group:
            continue
        min_y = min(p["y"] for p in group)
        hf = fh["font"]
        hbh = hf + hf * 1.12
        fh["y"] = min_y - lh * FAN_FIELD_HEADING_GAP - hbh + hf * 0.45
        fan_bottom[fh["id"]] = max(p["y"] + p["h"] for p in group)
        past = [p for p in group if p["y"] + p["h"] > y_limit + 1]
        if past:
            print(f"  {fh['id']}: nach Abstand {len(past)} Aspekte unter dem Seitenrand "
                  f"(y={max(p['y']+p['h'] for p in group):.0f} > {y_limit:.0f})")

    for yaml_id, cfg in FAN_GROUPS.items():
        align = cfg.get("align_heading_to")
        if not align:
            continue
        fh = next((h for h in fan_headings if h["id"] == yaml_id), None)
        group = by_fan.get(yaml_id) or []
        target = None
        for p in fan_items:
            db = p.get("draw_block") or p["block"]
            if (p.get("yaml_id") == align["yaml_id"]
                    and db.get("keyword") == align["schlagwort"]):
                target = p
                break
        if fh is None or target is None or not group:
            continue
        dy = (target["y"] - fh["y"]
              + align.get("y_shift_lh", 0.0) * heading_font * 1.12)
        if abs(dy) < 1:
            continue
        for p in group:
            p["y"] += dy
        fh["y"] += dy
        print(f"  {yaml_id}: Überschrift erneut auf {align['schlagwort']} ({dy:+.0f})")

    for yaml_id, cfg in FAN_GROUPS.items():
        if not cfg.get("shift_down_to_page"):
            continue
        group = by_fan.get(yaml_id) or []
        fh = next((h for h in fan_headings if h["id"] == yaml_id), None)
        if not group:
            continue
        slack = y_limit - max(p["y"] + p["h"] for p in group)
        if slack > 1:
            for p in group:
                p["y"] += slack
            if fh:
                fh["y"] += slack
            print(f"  {yaml_id}: {slack:.0f} nach unten, 7. Text bleibt auf der Seite")

    if fan_headings:
        top_h = min(fh["y"] for fh in fan_headings)
        bot_t = max(p["y"] + p["h"] for p in fan_items)
        print(f"Faecher  oben@{top_h:.0f}  unten@{bot_t:.0f}  Rand {PAGE_MARGIN:.0f}…{y_limit:.0f}")

    av_d = av_cx = av_cy = cap_font = 0.0
    if os.path.isfile(AVATAR_SRC) and tri_h > 0:
        free_top = ges_bot_a2 + ges_dy
        free_bot = A0_H - PAGE_MARGIN
        av_d = tri_h * AVATAR_TRI_FRAC
        cap_font = heading_font * 0.48
        stack_below = (av_d / 2.0 + cap_font * 1.6 + QR_SIZE + cap_font * 0.9)
        av_cx = A0_W * AVATAR_X_FRAC
        av_cy = (free_top + free_bot) / 2.0
        av_cy = min(av_cy, free_bot - stack_below)
        av_cy = max(av_cy, free_top + av_d / 2.0 + 24.0)
        r = av_d / 2.0
        clear_x = av_cx + r + font_draw
        for p in fan_items:
            if (p["x"] < av_cx + r and p["x"] + p["w"] > av_cx - r
                    and p["y"] < av_cy + r + cap_font * 2 + QR_SIZE
                    and p["y"] + p["h"] > av_cy - r):
                p["x"] = max(p["x"], clear_x)
        clamp_fan_margin(
            [p for p in fan_items if p.get("yaml_id") == "dm-01g"],
            x_min=PAGE_MARGIN, x_max=A0_W - PAGE_MARGIN)

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
    out.append(A2.font_face_svg())
    out.append(
        f'  <rect x="0" y="0" width="{A0_W:.2f}" height="{A0_H:.2f}" fill="{BG}"/>')
    hg = os.path.join(_DIR, "assets", HINTERGRUND)
    if os.path.isfile(hg):
        out.append(
            f'  <image href="{HINTERGRUND}" xlink:href="{HINTERGRUND}" '
            f'x="0" y="0" width="{A0_W:.2f}" height="{A0_H:.2f}" '
            f'preserveAspectRatio="none"/>')

    # Fächer-Blöcke (ohne Karten-Rechteck; 7-Zeiler am Dreieck sind aus)
    for fi in fan_items:
        db = fi.get("draw_block", fi["block"])
        out.append(draw_aspect_bare(
            fi["x"], fi["y"], fi["w"], font_draw, lh_draw, db,
            title_body_gap=FAN_TITLE_BODY_GAP,
            keyword=db.get("keyword")))

    for fh in fan_headings:
        out.append(draw_fan_heading(
            fh["x"], fh["y"], fh["lines"], fh["font"],
            align=fh.get("align", "middle")))

    # Sozialer Hauptsatz in der freien Mitte (Krankheit → Gesundheit)
    ges_top = ges_top_a2 + ges_dy
    hauptsatz_lh = HAUPTSATZ_FONT * HAUPTSATZ_LH
    hauptsatz_cx = shift_x + a2_w / 2.0 - A0_W * 0.01  # 3 % links, dann 2 % rechts
    hauptsatz_cy = (kra_bot + ges_top) / 2.0 - hauptsatz_lh  # eine Zeilenhöhe nach oben
    hauptsatz_lines = wrap_text(
        HAUPTSATZ, HAUPTSATZ_FONT, a2_w * HAUPTSATZ_WIDTH_FRAC)
    out.append(draw_hauptsatz(
        hauptsatz_cx, hauptsatz_cy, hauptsatz_lines,
        HAUPTSATZ_FONT, HAUPTSATZ_COLOR, author=HAUPTSATZ_AUTHOR))

    out.append(f'  <g id="a2-content" transform="translate({shift_x:.2f},{SHIFT_Y:.2f})">')
    out.append(inner.rstrip())
    out.append("  </g>")

    if os.path.isfile(AVATAR_SRC) and tri_h > 0 and av_d > 0:
        sha, ver_date = git_version_meta()
        intro_font = HAUPTSATZ_FONT * 0.80
        intro_x = av_cx - av_d / 2.0 - intro_font * 0.7
        intro_w = min(a2_w * HAUPTSATZ_WIDTH_FRAC,
                      intro_x - PAGE_MARGIN - 80.0)
        intro_lines = wrap_text(
            philo_intro_text(ver_date), intro_font, intro_w)
        out.append(draw_philo_avatar(
            av_cx, av_cy, av_d, AVATAR_CAPTION, cap_font,
            intro_lines=intro_lines, intro_x=intro_x,
            intro_font=intro_font, qr_size=QR_SIZE))
        print(f"Avatar  {av_d:.0f}px  @ {av_cx:.0f},{av_cy:.0f}  "
              f"QR {QR_SIZE:.0f} darunter  {QR_URL}  {ver_date}")

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
    print(f"Faecher-Font  {font:.1f} → {font_draw:.1f}  "
          f"(Strahlen {a2.get('rad_font', 0):.1f} × {A2.ARC_ZOOM})")
    fit = estimate_aspect_fit(fan_items, font_draw, lh_draw)
    print(
        f"Kuerzung  {fit['n']} Texte, {fit['n_over']} ueberlaufen: "
        f"ca. {fit['cut_pct']:.0f} % der Erklaertexte "
        f"({fit['chars_now'] - fit['chars_fit']:.0f} von {fit['chars_now']} Zeichen, "
        f"{fit['lines_now'] - fit['lines_fit']} von {fit['lines_now']} Zeilen)"
    )
    # JPG in Druckauflösung (A0 @ 300 dpi)
    # rsvg-convert resolves image hrefs relative to the SVG's directory only,
    # so temporarily copy referenced assets into output/ for rendering.
    import shutil
    out_dir = os.path.dirname(OUT_SVG)
    asset_dir = os.path.join(_DIR, "assets")
    tmp_copies = []
    font_copy = A2.copy_derived_font(out_dir)
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

    if os.path.isfile(AVATAR_SRC):
        dst = os.path.join(out_dir, AVATAR_HREF)
        if not os.path.exists(dst):
            shutil.copy2(AVATAR_SRC, dst)
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
        subprocess.run(
            ["magick", png_tmp,
             "-density", str(DPI), "-units", "PixelsPerInch",
             "-compress", "JPEG", "-quality", "92",
             OUT_PDF],
            check=True,
        )
        print(f"wrote {OUT_JPG}  {JPG_W}×{JPG_H} @ {DPI} dpi")
        print(f"wrote {OUT_PDF}  DIN A0  841×1189 mm @ {DPI} dpi")
    finally:
        for tmp in [png_tmp, OUT_SVG]:
            if os.path.isfile(tmp):
                os.remove(tmp)
        for f in tmp_copies:
            if os.path.isfile(f):
                os.remove(f)


if __name__ == "__main__":
    main()
