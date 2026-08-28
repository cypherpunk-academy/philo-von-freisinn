# Soziale Gesundheit — Gesundheit und Krankheit des sozialen Zusammenlebens

A visual matrix mapping healthy and pathological dynamics across Steiner's social threefolding (Geist, Recht, Wirtschaft).

## Directory Structure

```
content/       YAML source of truth for all matrix fields
scripts/       Python generators (A2 poster, A0 large-format)
output/        Generated SVG/JPG (auto-regenerated via pre-commit hook)
assets/        Reference images, backgrounds, triangle graphics
prompts/       AI prompts for field content and image generation
docs/          Specification and design documents
```

## Two Levels of Change

### Level 1: YAML-only (auto-regenerated)

Edit `content/soziale-gesundheit.yaml` and commit. The pre-commit hook runs both generators and stages the updated output automatically.

Good for: text corrections, label changes, rewording aspects.

```bash
# One-time setup (per clone)
git config core.hooksPath .githooks
```

### Level 2: LLM-assisted (structural)

The A2 generator (`scripts/generate-a2.py`) has all field content **hardcoded in Python** for precise layout control. Structural changes — new fields, redesigned aspects, layout changes — require editing the Python scripts, typically with AI assistance using the prompts in `prompts/`.

Good for: adding new fields, changing the visual structure, reworking content with philosophical depth.

## Generating Output

```bash
cd projects/soziale-gesundheit
python scripts/generate-a2.py    # A2 poster (SVG + triangles SVG)
python scripts/generate-a0.py    # A0 large-format (SVG + JPG, reads YAML)
```

Requires: Python 3, `cairosvg`, `PyYAML`.
