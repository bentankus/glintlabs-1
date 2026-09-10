# HITs Study Insights references

This is the first-priority reference collection for `hits-study-insights`.

Use this folder for:

- validated HITs retrieval examples
- body-text keyword frequency and tag relevance calibration examples
- cross-study corroboration patterns
- examples that combine quantitative and qualitative evidence
- approved citation and caveat language

The HITs study content remains the source of truth. Reference material may guide
retrieval and synthesis, but it must not replace, expand, or contradict evidence in
the five selected studies.

Load `topic-lexicon.md` for validated query-expansion terms and aliases. Its frequency
counts document the 2026-08-24 audit and must be recomputed before being described as
current.

Load `study-topic-profile.md` for the audited per-study multi-topic occurrence matrix.
Use it to understand likely study coverage, then recount the current bodies before
ranking or reporting frequencies.

Load `retrieval-playbook.md` for observed connector limitations, corpus auditing,
normalization, specificity rules, and tested prompt mappings.

Load `golden-example.md` for the expected concise, declarative answer structure.

## Retrieval contract

1. Search the People Science HITs group unless the user requests another scope.
2. Retrieve a broad candidate corpus and reconcile study IDs against curated group
   membership. Do not treat the record-level `group` field as membership.
3. Remove boilerplate and count specific keyphrases across normalized full body text.
4. Rank by body-text keyword commonality, then tag/topic relevance, then publication
   date as a tie-breaker. Never use titles.
5. Interpret only the five highest-ranked credible studies.
6. Corroborate findings across those studies and distinguish single-study evidence.
7. Open with a two- or three-sentence cross-study summary containing only findings
   supported by at least two selected studies.
8. Cite study URLs and preserve population, method, and limitation context.
9. Put source links immediately below the finding they support, not in a detached
   source list.
