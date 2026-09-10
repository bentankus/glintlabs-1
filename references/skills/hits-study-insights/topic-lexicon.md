# People Science HITs topic lexicon

Use this lexicon to expand retrieval terms when a user's question is broad or uses a
closely related concept. Body-text evidence still determines ranking; these terms do
not override counts from the current corpus.

## Corpus basis

- Audited: 2026-08-24
- Corpus: 29 current People Science HITs study bodies
- Titles excluded from counting
- Matching: case-insensitive, with obvious singular/plural and hyphen variants merged
- Priority: document frequency first, then total body occurrences

`Copilot` and `Employee Listening` were treated as established seed phrases and are
listed separately from the ten expansion topics.

## Established seed phrases

| Canonical topic | Body occurrences | Study bodies | Variants |
|---|---:|---:|---|
| Copilot | 68 | 6 | Copilot |
| Employee Listening | 12 | 6 | employee listening |

## Expansion topics

| Canonical topic | Body occurrences | Study bodies | Include these variants |
|---|---:|---:|---|
| AI transformation | 62 | 15 | AI transformation |
| AI tools | 38 | 15 | AI tool, AI tools |
| AI adoption | 42 | 13 | AI adoption |
| AI agents | 58 | 10 | AI agent, AI agents |
| AI value | 47 | 10 | AI value, value of AI, value from AI |
| Psychological safety | 36 | 9 | psychological safety, psychologically safe |
| Viva Glint | 70 | 8 | Viva Glint |
| Employee feedback | 22 | 8 | employee feedback |
| Action taking | 40 | 7 | action taking, action-taking, take action |
| Employee surveys | 19 | 7 | employee survey, employee surveys |

## Important adjacent aliases

- Treat `agentic AI` as adjacent to `AI agents`, but preserve both counts during
  ranking. In the audited corpus, `agentic AI` appeared 55 times across 9 bodies.
- Treat `AI at work` as adjacent to `AI value` and `AI adoption` when the user's
  question concerns workplace outcomes.
- Treat `Viva Insights` as adjacent to `Viva Glint` only when the question concerns
  combined sentiment and work-pattern analysis.

## Usage rules

1. Start with the user's exact terms.
2. Add only lexicon topics that are semantically necessary to improve recall.
3. Count exact normalized occurrences of every selected term and variant in the
   current study bodies.
4. Rank using current body counts, not the historical counts in this file.
5. Keep distinct concepts separate. Do not collapse all AI-related terms into one
   score.
6. Re-audit this lexicon when the HITs group membership changes materially. Never
   present these historical counts as current without recomputing them.
