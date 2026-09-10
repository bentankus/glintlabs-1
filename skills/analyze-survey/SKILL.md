---
name: analyze-survey
description: "Run the standard People Science survey analysis package using vivaglint and produce a stable analysis manifest. Use when the user has Viva Glint survey exports, survey CSVs, cycle files, attribute files, or attrition files and asks to run descriptives, correlations, factor analysis, cycle comparisons, by-attribute analysis, or attrition analysis."
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Analyze Survey

Run a standard, local People Science analysis workflow over Viva Glint survey exports using the pinned `vivaglint` package. Do not copy analysis code into this plugin. The skill's job is orchestration, validation, and manifest creation.

## Use when

Use this skill when the user asks to:

- run a survey analysis package
- analyze a Viva Glint export
- produce descriptives, correlations, factor analysis, cycle comparisons, by-attribute analysis, or attrition analysis
- generate an analysis manifest for downstream interpretation
- prepare outputs for `interpret-analysis`, `analysis-qa`, or `manager-action-taking`

Do not use this skill when the user only wants an interpretation of existing results. Use `interpret-analysis` instead.

## Required inputs

Always start a survey-analysis request by asking:

> Do you have survey data you would like to reference? If not, you can use demo data.

If the user does not provide data or chooses demo data, use:

```text
demo-data/survey/config.json
demo-data/survey/glint_demo_data.csv
```

Ask for missing required inputs:

| Input | Required | Notes |
|---|---:|---|
| Survey CSV | Yes | Primary Viva Glint export. |
| Scale points | Yes | Usually 5, but confirm. |
| Employee ID column | Yes | Required for import and joins. |
| Attribute file | Optional | Needed for by-attribute analysis. |
| Attribute columns | Optional | Required when attribute file is provided. |
| Attrition file | Optional | Needed for attrition analysis. |
| Termination date column | Optional | Required when attrition file is provided. |
| Cycle CSVs | Optional | Needed for cycle comparisons. |

The demo dataset uses `input_format: wide_items`, `emp_id_col: user_id`, and numeric `Q_*` survey item columns.

## Process

1. Inspect first-priority references in `references/skills/analyze-survey/`.
2. Inspect second-priority shared references in `references/general/`, especially `codebook-catalog.md`, `privacy-and-minimum-n.md`, and `architecture.md`.
3. Confirm the intended output directory.
4. Create or validate an `analysis-config.json` matching `schemas/analysis-config.schema.json`.
5. Run `scripts/run_vivaglint_analysis.py` with the config and output directory.
6. Require the built-in repeatability check to run. The script runs the analysis twice, compares completed artifacts by SHA-256 hash, and writes `repeatability_check` into `analysis-manifest.json`.
7. Inspect `analysis-manifest.json`.
8. Report what completed, what skipped, what failed, whether repeatability passed, and what should be interpreted next.

## Output contract

The skill must produce or point to:

```text
analysis-manifest.json
descriptives.csv
response_distribution.csv
correlations.csv
factor_analysis_summary.csv
cycle_comparisons.csv
by_attribute.csv
attrition.csv
```

Only artifacts for completed analyses are required. Skipped or failed analyses must be recorded in the manifest.

## Repeatability requirement

Always run analysis twice before treating outputs as interpretation-ready. The first run writes the primary artifacts; the second run writes to `_repeatability_run/` and compares completed artifacts byte-for-byte.

If `repeatability_check.status != "passed"`:

- do not interpret the results
- report the mismatched artifact names
- explain that the analysis is not reproducible yet
- inspect whether nondeterministic codebook behavior, package drift, input mutation, or environment differences caused the mismatch

Only use `--skip-repeatability-check` for the internal second pass or an explicit debugging request. Never use it for normal user-facing analysis.

## Interpretation boundaries

This skill may summarize execution status and obvious data warnings. It should not produce final People Science interpretation. After successful execution, suggest:

1. `analysis-qa` to check validity and safety.
2. `interpret-analysis` to synthesize findings.
3. `manager-action-taking` only after QA passes.

## Privacy

Do not paste raw employee-level rows into chat. Keep outputs local. Use minimum group-size suppression for by-attribute and attrition analyses.
