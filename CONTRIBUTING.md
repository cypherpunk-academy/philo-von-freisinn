# Contributing to Philo von Freisinn

Thank you for your interest in contributing! This project lives at the intersection of philosophy, AI, and open culture. Whether you're a Steiner scholar, a developer, a writer, or simply curious — there's room for you here.

## What You Can Contribute

### Quotes (`sources/quotes/`)

Curated quotes from Rudolf Steiner's works or related authors, each in a `.quote.md` file:

```markdown
---
source: "Die Kernpunkte der sozialen Frage, GA 23"
chapter: "II. Die am wirklichen Leben orientierten Lösungsversuche..."
---

> The quote text here.

**Explanation:** A brief note on why this quote matters and how it connects to the broader themes.
```

### Concepts (`sources/concepts/`)

Additions or corrections to the curated concept lexicon in `concepts-curated.jsonl`. Each line is a JSON object defining a philosophical term as Steiner used it.

### Talks (`writings/talks/`)

Philosophical dialogues in Socratic style. Place them in the appropriate subfolder:

- `3gl/` — Social threefolding (Dreigliederung des sozialen Organismus)
- `phdf/` — Philosophy of Freedom and epistemology
- `foss/` — Free software, transparency, digital rights

Use kebab-case filenames without prefixes: `my-topic-title.md`

### Blog Posts (`projects/blog-posts/`)

Short philosophical essays ("Grundgedanken") that make Steiner's ideas accessible to a contemporary audience.

### Project Contributions

Each folder under `projects/` is a larger creative work. Read the existing content first and open an issue to discuss your idea before submitting a PR.

## What Not to Edit

- **`prompts/`** — AI system prompts are infrastructure; changes here affect the assistant's behavior globally.
- **`assistant-manifest.yaml`** — Pipeline configuration managed by the maintainer.
- **`.generated/`** — This folder is excluded via `.gitignore`. It contains computed data produced by the ragkeep pipeline.

## How to Submit

1. Fork the repository
2. Create a feature branch (`git checkout -b add-quote-xyz`)
3. Make your changes
4. Commit with a clear message
5. Open a Pull Request

## Style Guidelines

- **Language:** Content is in German. PRs, issues, and commit messages can be in German or English.
- **Tone:** Lively, precise, accessible. Humor welcome, irony not.
- **Terminology:** Use Steiner's own terms (German). Avoid foreign philosophical jargon he didn't use (e.g., say "Notwendigkeit" not "Determinismus").
- **Filenames:** Lowercase kebab-case, ASCII-safe where possible (use `ae` for `ä`, `ue` for `ü`, etc.)

## Questions?

Open an issue — we're happy to help you find the right place for your contribution.
