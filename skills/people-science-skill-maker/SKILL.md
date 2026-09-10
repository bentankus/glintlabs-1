---
name: people-science-skill-maker
description: "Create and evolve new skills inside the eve-people-science plugin suite. Use when adding People Science analytics, interpretation, QA, manager guidance, artifact-generation, or workflow skills that should reuse the shared analysis manifest, prioritized references, privacy guardrails, and vivaglint integration."
allowed-tools: Bash, Read, Write, Glob, Grep
---

# People Science Skill Maker

Create high-quality, maintainable skills inside the `eve-people-science` plugin suite. This is the repo-local skill-authoring guide for extending the suite over time.

## Use when

Use this skill when the user asks to:

- add another skill to `eve-people-science`
- turn a People Science workflow into a skill
- create a skill that uses `vivaglint` outputs
- add a new interpretation, QA, MAT, customer-readout, or artifact workflow
- update the plugin architecture after learning a new convention or decision

## Core rule

Do not create one giant skill. Add focused skills that share contracts, references, schemas, and runner utilities.

Every new skill should have:

```text
skills/<skill-name>/SKILL.md
references/skills/<skill-name>/README.md
```

Use `references/skills/<skill-name>/` as the first-priority reference collection for that skill. Use `references/general/` as second-priority shared context.

## Authoring process

1. **Clarify the user job.** Define the exact task the skill owns and what it should not own.
2. **Choose the right form.** Most additions should be a skill. Use scripts only when deterministic execution is required.
3. **Check for overlap.** Reuse existing skills when the job is already covered:
   - `analyze-survey` runs codebooks and produces manifests.
   - `analysis-qa` checks validity, privacy, and readiness.
   - `interpret-analysis` synthesizes People Science findings.
   - `manager-action-taking` creates manager-facing guidance.
4. **Define inputs and outputs.** Prefer `analysis-manifest.json` and generated artifacts as the interface.
5. **Add first-priority references.** Create `references/skills/<skill-name>/README.md` and list the source documents/examples that belong there.
6. **Reference general context.** Tell the skill to inspect `references/general/` after its own folder.
7. **Respect privacy.** Do not expose raw employee-level rows, small cells, comments, or identifiable data in narrative outputs.
8. **Add or update schemas only when the shared contract changes.**
9. **Update plugin docs.** Add the skill to `plugins/eve-people-science/README.md`.
10. **Test the structure.** Run existing tests and add small contract tests when behavior changes.

## Standard skill skeleton

```markdown
---
name: <skill-name>
description: "<One sharp router sentence. Use when the user asks for concrete trigger phrases.>"
allowed-tools: Read, Glob, Grep
---

# <Skill Title>

<One-paragraph job statement.>

## Use when

- <trigger>
- <trigger>

## Required grounding

Inspect references in this order:

1. `references/skills/<skill-name>/`
2. `references/general/`

Then load:

- `analysis-manifest.json` when interpreting outputs
- relevant artifacts listed in the manifest

## Process

1.
2.
3.

## Output format

```markdown
## <Output title>
```

## Guardrails

- Do not expose raw employee-level rows.
- Do not overstate causality.
- Do not proceed when QA or repeatability checks fail.
```

## Decision log

Keep this section current whenever a durable repo convention is learned.

| Date | Decision |
|---|---|
| 2026-08-17 | Use a multi-skill plugin suite named `eve-people-science`, not one monolithic skill. |
| 2026-08-17 | Keep `vivaglint` as the source-of-truth analysis engine; do not copy analysis code into the plugin. |
| 2026-08-17 | Use `analysis-manifest.json` as the stable contract between execution, QA, interpretation, and manager-action skills. |
| 2026-08-17 | `analyze-survey` must run twice by default and compare completed artifacts by SHA-256 before outputs are interpretation-ready. |
| 2026-08-17 | Each skill has first-priority references under `references/skills/<skill-name>/`; shared second-priority context lives under `references/general/`. |
| 2026-08-17 | Survey-analysis workflows must start by asking: "Do you have survey data you would like to reference? If not, you can use demo data." If the user chooses demo data, use `demo-data/survey/config.json` and `demo-data/survey/glint_demo_data.csv`. |
| 2026-08-17 | The demo survey dataset is a `wide_items` file, so the runner supports `input_format: wide_items` by converting numeric item columns into a `vivaglint`-compatible in-memory survey. |
| 2026-08-17 | Do not author Manager Action Taking context proactively. Keep MAT context clean and add only user-provided materials. |
| 2026-08-17 | The user-provided `Action Planning Taxonomy.xlsx` workbook is the primary source for Manager Action Taking. Match canonical symbolic question IDs to generated candidate sets and use only the action records authorized for that question. |
| 2026-08-17 | Each taxonomy workbook row is a distinct focus-area action record. Rows sharing a template are manager choices, not mandatory ordered steps in one combined plan. |
| 2026-08-17 | Generate a small question map, candidate-set files, and row-level action-record files for efficient skill retrieval. Do not keep the former denormalized compatibility index; verify every generated artifact against the workbook in CI. |
| 2026-08-17 | MAT action records include semantic `action_type` and `selection_signals`; use `selection-logic.md` plus `golden-examples.json` to choose among authorized records for a matched question. |
| 2026-08-17 | `PSE - Collaborative Action Taking.pdf` is secondary MAT context. Use ACT (Acknowledge, Collaborate, Take one step) to frame manager conversations and choose among authorized taxonomy records, but never to override the primary taxonomy match. |
| 2026-08-17 | `Propel action-taking through conversations with Microsoft Viva Glint` is secondary MAT context for evidence and framing: use its action-taking evidence, manager roles, 3-6 month business-priority lens, and existing-meeting check-in guidance to frame recommendations. |
| 2026-08-17 | `3 Steps to Build Psychological Safety on Your Team` is secondary MAT context for voice/trust/inclusion recommendations. Use it to frame psychological safety behaviors: check negative reactivity, listen without agenda, and model vulnerability. |
| 2026-08-17 | `Adoption & Actions Storytelling Deck Updated for PS 2.0.pptx` is tertiary MAT context. Use it only as a presentation/storytelling template when the user asks for slides, never to select actions. |
| 2026-08-17 | MAT selection logic should explicitly separate decision phases, manager roles, anti-selection rules, and presentation packaging so secondary/tertiary context improves framing without overriding taxonomy-authorized records. |
| 2026-08-24 | HITs insight ranking ignores titles and prioritizes normalized body-text keyword frequency and cross-study commonality, followed by tags and publication date. Curated group membership must be reconciled by study ID; record-level `group` metadata may identify another originating research organization. |
| 2026-08-24 | Maintain a skill-specific HITs topic lexicon for query expansion. Historical corpus counts calibrate terminology but must be recomputed before being presented as current evidence. |
| 2026-08-24 | Maintain a multi-label per-study HITs topic profile. Rank studies by prompt-topic body frequency and coverage, then rank insights by corroboration and summed supporting-study topic frequency. |
| 2026-08-24 | HITs insight answers use short declarative sections with source links immediately beneath each supported section. |
| 2026-08-24 | HITs insight answers open with a short cross-study synthesis based on an all-selected-study evidence matrix; summary claims require support from at least two selected studies. |
| 2026-08-24 | HITs retrieval must defend against 20-record caps, semantic substitutions, incomplete bodies, and origin-group metadata. Remove boilerplate and do not score generic words such as `AI` or `manager` alone. |
| 2026-08-24 | Preserve tested query mappings and a golden answer example in skill-specific references so later runs reproduce validated behavior. |
| 2026-08-24 | Distribute the HITs insight skill and MCP as a deterministic ZIP containing the complete skill references, merge-safe MCP JSON, agent instructions, and no credentials or user-specific paths. |

## When learning something new

When a new durable convention, architecture choice, quality bar, or workflow rule emerges:

1. Update this `people-science-skill-maker` skill.
2. Update the relevant `references/skills/<skill-name>/README.md` or `references/general/` document.
3. Update schemas or tests if the contract changed.
4. Commit the change with a clear message.
