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
import os
import re
import subprocess
import xml.sax.saxutils as xml

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_PATH = os.path.join(_DIR, "content", "soziale-gesundheit.yaml")
HINTERGRUND = "hintergrund.jpg"
OUT_SVG = os.path.join(_DIR, "output", "halbkreise-a0.svg")

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

    kra_dy = KRA_NUDGE_Y
    # Gesundheit so, dass Freiraum unter beiden Tafeln (7er-Bloecke) gleich ist
    kra_bot = max(b["y1"] for b in a2["kra_blocks"]) + kra_dy
    ges_top_a2 = min(b["y0"] for b in a2["ges_blocks"])
    ges_bot_a2 = max(b["y1"] for b in a2["ges_blocks"])
    # free_kra = ges_top - kra_bot; free_ges = page_bottom - ges_bot; equalize
    ges_dy = (A0_H - PAGE_MARGIN - ges_bot_a2 - ges_top_a2 + kra_bot) / 2.0

    inner = _shift_panel(inner, "krankheit", kra_dy, watermark="Krankheit")
    inner = _shift_panel(inner, "gesundheit", ges_dy, watermark="Gesundheit")
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

    clusters = []
    overflow = []
    for side in ("left", "right"):
        x = gutter_x(side)
        kra_batch = [g for g in prepared if g["side"] == side and g["panel"] == "kra"]
        placed_k, left_k = place_staggered(
            kra_batch, x, kra_y0, y_limit_kra, col_w, font, lh,
            side=side, start="inner")
        clusters.extend(placed_k)
        overflow.extend(left_k)
        ges_batch = [g for g in prepared if g["side"] == side and g["panel"] == "ges"]
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
            f'  <image href="../assets/{HINTERGRUND}" xlink:href="../assets/{HINTERGRUND}" '
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
    print(f"7er-Bloecke: {len(seven)}  Gruppen: {len(clusters)}")
    print(f"Ueberlauf unten: {len(overflow)}")
    print(f"wrote {OUT_SVG}")

    # JPG in Druckauflösung (A0 @ 300 dpi)
    png_tmp = os.path.join(_DIR, "output", ".a0-render.png")
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
        if os.path.isfile(png_tmp):
            os.remove(png_tmp)


if __name__ == "__main__":
    main()
