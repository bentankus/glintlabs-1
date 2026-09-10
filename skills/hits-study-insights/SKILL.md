---
name: hits-study-insights
description: "Find and synthesize People Science evidence from HITs studies. Use when a user asks a research-backed question such as how to sustain Copilot adoption, improve employee experience, support managers, or understand workplace behavior."
allowed-tools: hits-import, hits-view, Read, Glob, Grep
---

# HITs Study Insights

Answer People Science questions by measuring keyword commonality in HITs study body
text, reviewing the five strongest matches, and corroborating concise findings across
them.

## Use when

- The user asks a People Science question that should be grounded in HITs research.
- The user wants evidence, findings, recommendations, or implications from studies.
- The user asks what research says about a workplace, employee, manager, AI, or
  Copilot topic.

Do not use this skill to analyze raw survey files or interpret a vivaglint analysis
manifest. Use `analyze-survey` or `interpret-analysis` for those jobs.

## Required grounding

Inspect references in this order:

1. `references/skills/hits-study-insights/`
2. `references/general/`

Load `references/skills/hits-study-insights/topic-lexicon.md` to expand broad queries
with validated People Science terminology. Treat its counts as historical calibration
only and recompute counts against the current HITs corpus.

Load `references/skills/hits-study-insights/study-topic-profile.md` to understand the
multi-topic structure of the audited corpus. Use it as a historical index, not as a
substitute for recounting current study bodies.

Load `references/skills/hits-study-insights/retrieval-playbook.md` for connector
failure modes, corpus validation, normalization, specificity rules, and tested prompt
mappings. Use `golden-example.md` as the answer-quality reference.

Use the HITs MCP as the source of study metadata and content. Unless the user
explicitly requests another scope, restrict every query to:

`https://hits.microsoft.com/group/people-science`

## Process

### 1. Translate the question into retrieval concepts

Identify:

- the primary outcome or job, such as sustainable adoption
- the subject or product, such as Copilot
- close synonyms and directly related concepts

Keep the retrieval query faithful to the user's wording. Do not broaden it into a
generic People Science search.

### 2. Retrieve the candidate corpus

Use HITs to retrieve a broad candidate set with:

- study ID
- full body text
- tags or topics
- publication date
- URL
- group

Request enough candidates to avoid treating the MCP's first semantic results as the
final ranking. Establish membership from the requested HITs group or its enumerated
member IDs. The record-level `group` field may identify the originating research
organization and must not be used to exclude a curated group member.

Audit the corpus before counting:

- compare retrieved distinct study IDs with the group's current membership count
- deduplicate by study ID
- if the connector caps a response, retrieve additional batches until membership is
  complete
- do not report corpus-wide frequencies when any member body is missing or truncated

### 3. Build the body-text keyword profile

Normalize body text to lowercase and normalize whitespace and punctuation before
counting. Preserve multi-word phrases, so `employee listening` is counted as a phrase
rather than two unrelated words.

Remove titles, navigation, subscription language, privacy text, standard Research
Drop boilerplate, URLs, HTML attributes, and citation markup before counting. Follow
the complete normalization contract in `retrieval-playbook.md`.

For a question with named concepts, derive one to five exact keyphrases and close
variants from the user's wording. Use the topic lexicon to add only directly relevant
aliases or adjacent concepts. Count each phrase in every candidate's full body.

For an open-ended inventory question such as "What products are People Science
working on?", identify named products and recurring concept phrases in the candidate
bodies. Seed discovery with the topic lexicon, then allow new corpus terms to
outperform those seeds. Record:

- **term frequency**: exact occurrences in each study body
- **document frequency**: number of candidate study bodies containing the phrase
- **keyword coverage**: number of relevant phrases present in each study body

Retain the counts used for ranking so the selection can be explained. Do not interpret
findings during this pass.

### 4. Rank candidates in this strict order

Rank lexicographically, not with a blended relevance score:

1. **Prompt-topic frequency within each study**
2. **Prompt-topic coverage within each study**
3. **Tag/topic relevance**
4. **Publication date**, newest first, only as a tie-breaker

For each study, create a multi-label topic profile. Count every prompt-relevant topic
independently because one study may substantially discuss several topics.

Apply the specificity guard from `retrieval-playbook.md`. Never score generic actor or
action words such as `AI`, `manager`, `employee`, `team`, `use`, `support`, or
`training` alone. Score validated concepts such as `manager role modeling` or
`role-specific AI training`.

For each prompt topic, assign:

- exact user phrase: weight 3
- documented alias: weight 2
- directly relevant adjacent lexicon topic: weight 1

Calculate `topic_frequency = sum(normalized body occurrences * topic weight)`.
Rank by topic frequency first, then by the number of distinct prompt topics present.
Do not let a broad adjacent term overpower an exact prompt phrase: compare exact
phrase frequency before the weighted total whenever the user supplied a named phrase.

Body-text counts must dominate tags and date. A candidate with stronger prompt-topic
frequency must always outrank one selected only because of its tags or recency.
Assign tag relevance independently:

| Score | Meaning |
|---|---|
| 3 | Direct tag match to the user's subject and outcome |
| 2 | Strong match to one and clear relationship to the other |
| 1 | Adjacent or supporting relevance |
| 0 | No meaningful relevance |

Do not use study titles for retrieval, scoring, ranking, or tie-breaking. Deduplicate
by study ID and exclude candidates with no relevant body-text matches.

Select the top five studies. If fewer than five credible candidates exist, use the
credible set and state the limitation rather than padding it with weak matches.

### 5. Search only the selected studies for the answer

After ranking, interpret only the selected study IDs. Search each selected study for:

- direct answers to the user's question
- quantitative evidence: sample sizes, percentages, means, changes, effect sizes,
  frequencies, or other reported measures
- qualitative evidence: participant themes, observed behaviors, needs, barriers,
  motivations, and short attributable excerpts
- study context: population, method, product stage, and material limitations

Within each selected study, prioritize evidence passages associated with its
highest-frequency prompt topic. Across the selected set, order surfaced insights by:

1. number of selected studies corroborating the insight
2. summed prompt-topic frequency of those supporting studies
3. presence of both quantitative and qualitative evidence
4. practical usefulness to the prompter

Frequency controls retrieval priority, not truth strength. Repetition within one study
does not make a claim more valid, causal, or broadly generalizable.

The initial corpus bodies may be used only for keyword counting and selection. Do not
use evidence from studies outside the selected set after interpretation begins.
If a selected study contains no relevant evidence, say so; do not silently replace it
with a lower-ranked study.

### 6. Corroborate across the selected studies

Build findings from convergence rather than isolated claims:

- Treat a finding as **corroborated** when at least two selected studies independently
  support it.
- Label evidence found in only one study as **single-study evidence**.
- Surface meaningful disagreement or differences in population, method, or context.
- Prefer conclusions supported by both quantitative and qualitative evidence.
- Never manufacture a quantitative statistic, participant quote, or cross-study
  agreement.

Before drafting the answer, compare all selected studies in a simple evidence matrix:

- rows: candidate findings
- columns: selected studies
- cells: supports, contradicts, or does not address

Use the matrix to write a short opening synthesis. Include only findings supported by
at least two selected studies. If no finding meets that threshold, state that the
selected evidence does not yet converge. Do not imply that every selected study
supports a finding unless every study has direct supporting evidence.

### 7. Answer the question directly

Lead with a two- or three-sentence `## Cross-study summary` that states the strongest
corroborated pattern across the selected articles. Include the support count, such as
"Four of five studies indicate..." when it can be verified. Mention material
disagreement or coverage gaps in the same summary.

Then present two to four evidence-backed findings, ordered by usefulness to the user
rather than by study. Connect each recommendation to the evidence supporting it.

Write each finding as a short section with clear, declarative prose. Put its supporting
study links on a separate `Sources:` line immediately below that section. Do not defer
all citations to a source list at the end.

## Output format

```markdown
## Cross-study summary

<Two or three declarative sentences stating only themes corroborated by at least two
selected studies. Include verified support counts and any material disagreement.>

### <Declarative finding>

<Concise synthesis with quantitative evidence and qualitative context where
available.>

**Sources:** [Study title](URL); [Study title](URL)

### <Declarative finding>

<Concise evidence-backed synthesis.>

**Sources:** [Study title](URL)

**Evidence base:** Reviewed N studies. <One short sentence on coverage, disagreement,
or limitations when material.>
```

Keep the answer clean and concise. Do not provide the candidate-ranking table or
keyword counts unless the user asks how the studies were selected.

Before returning the answer, compare it with `golden-example.md` for readability,
evidence placement, source placement, and appropriate certainty.

## Guardrails

- Keep all HITs retrieval within the People Science group unless explicitly overridden.
- Do not confuse a study's originating `group` metadata with curated HITs group
  membership.
- Cite every substantive claim with one or more selected studies.
- Place source links directly beneath the section they support.
- Do not place a single-study claim in the cross-study summary.
- Preserve the study's population and method context; do not generalize beyond it.
- Do not imply causality from descriptive or correlational evidence.
- Do not expose participant identities, raw sensitive data, or identifiable comments.
- Quote only text present in the study and keep excerpts short.
- If no selected study provides an answer, say that the evidence base is insufficient.
- Never use historical lexicon counts as current evidence; recompute against the
  retrieved corpus.
- Never treat a tool call's `COMPLETED` status as proof that the corpus is complete.
