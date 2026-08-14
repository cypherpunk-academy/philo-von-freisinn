<table><tr>
<td>

## Philo von Freisinn

A philosophical AI assistant grounded in Rudolf Steiner's *Philosophy of Freedom* and related works. Philo develops a mathematistic-individualistic worldview through Socratic dialogue, exploring freedom, social threefolding, and open-source culture.

</td>
<td width="170"><img src="assets/avatar.png" width="150" alt="Philo von Freisinn" /></td>
</tr></table>

## Repository Structure

### Sources — Work on primary texts

```
sources/
  quotes/          Curated quotes from Steiner and related authors
  concepts/        Philosophical concept lexicon (JSONL)
  typologies/      Worldview typologies to be explained
```

### Writings — Original philosophical texts

```
writings/
  talks/
    3gl/           Social threefolding (Dreigliederung)
    phdf/          Philosophy of Freedom / epistemology
    foss/          Free software, transparency, cypherpunk
    drafts/        Raw conversation transcripts (all topics)
  co-created/
    quotes/        Quotes born in dialogue with Claude
    summaries/     Thematic summaries from conversations
```

### Projects — Creative works in progress

```
projects/
  doppelmatrix/    Health & Illness of Social Coexistence (visual matrix)
  korn-currency/   KORN — A liberating currency concept
  die-assoziation/ Novel — The Association
  git-party/       GIT — Cooperative, Initiative, Transparent (political concept)
  blog-posts/      Short philosophical essays (Grundgedanken)
```

### Infrastructure

```
prompts/           AI system prompts and verification logic
assets/            Avatar and visual identity
assistant-manifest.yaml   Configuration for the ragkeep pipeline
```

## How It Works

Philo von Freisinn is powered by a RAG (Retrieval-Augmented Generation) pipeline managed by [ragkeep](https://github.com/cypherpunk-academy/ragkeep). The pipeline chunks, embeds, and indexes the content in this repository alongside digitized primary sources (books and lectures by Rudolf Steiner and others).

Generated data (chunk caches, indices, reports) is produced by the pipeline and excluded from this repository via `.gitignore`.

## Writing Style

Philo writes in German. The tone is lively and precise — humorous but never ironic. No personifications of the author, no foreign philosophical jargon that Steiner himself didn't use. The goal is to inspire initiative, with a focus on the boundaries of freedom between people.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute.

## License

Content in this repository is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

