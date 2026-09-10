# eve-people-science

People Science analytics plugin suite for Viva Glint survey data.

## What it does

This plugin provides a set of focused skills that share a common analysis contract:

1. `analyze-survey` runs a standard set of `vivaglint` codebooks and writes an `analysis-manifest.json`.
2. `analysis-qa` reviews output validity, privacy thresholds, and interpretation readiness.
3. `interpret-analysis` turns codebook outputs into People Science findings and caveats.
4. `manager-action-taking` converts results into manager-facing guidance and action planning support.
5. `hits-study-insights` ranks HITs body-text keyword commonality and corroborates evidence from the five strongest studies.
6. `nezha-clickhouse` writes, reviews, and troubleshoots ClickHouse SQL for Viva Glint telemetry in Nezha.
7. `people-science-skill-maker` creates and evolves additional skills in this plugin suite.

The plugin deliberately does not duplicate the `vivaglint` analysis package. It calls a pinned package version and treats the output manifest as the stable interface between execution and interpretation.

## Prerequisites

- Python 3.10 or later for local survey-analysis scripts.
- `vivaglint[all]==0.1.1` for the `analyze-survey` workflow.
- Agency for the bundled HITs MCP connection used by `hits-study-insights`.
- Access to the relevant Viva Glint survey exports, analysis outputs, or internal
  research sources for the workflow being used.

## Install

Add the EVE marketplace, then install the plugin:

```text
/plugin marketplace add https://github.com/employee-experience/EVE-Plugin-Marketplace.git
/plugin install eve-people-science@eve-plugin-marketplace
```

## Usage

Ask for the People Science job directly; the host routes the request to the
appropriate skill. Examples:

- "Run the standard People Science analysis on this Viva Glint export."
- "Check whether this analysis manifest is safe to interpret."
- "Turn these survey findings into a manager conversation guide."
- "What does HITs research say about sustaining Copilot adoption?"
- "Help me write a Nezha ClickHouse query for Viva Glint usage."

## Reference priority

Each skill has a first-priority reference collection at:

```text
references/skills/<skill-name>/
```

Shared, second-priority context lives at:

```text
references/general/
```

When a skill runs, inspect its own reference folder first, then inspect `references/general/`. Skill-specific references take precedence for that skill unless they violate privacy, safety, or the manifest contract.

## Shared contract

All downstream skills should start with:

```text
analysis-manifest.json
```

The manifest records:

- input files and non-sensitive profiles
- `vivaglint` version and package source
- analyses requested, completed, skipped, or failed
- artifact paths
- warnings and privacy notes
- downstream interpretation readiness

Schema: `schemas/analysis-manifest.schema.json`

## Skills

| Skill | Use when |
|---|---|
| `analyze-survey` | The user has survey data and wants the standard analysis package run. |
| `analysis-qa` | The user needs to know whether outputs are valid and safe to interpret. |
| `interpret-analysis` | The user has output files/manifests and wants People Science interpretation. |
| `manager-action-taking` | The user wants manager-facing interpretation, conversation guidance, or action planning. |
| `hits-study-insights` | The user asks a People Science question that should be answered from HITs research. |
| `nezha-clickhouse` | The user needs Viva Glint Nezha / ClickHouse schema help, query authoring, query review, or telemetry best practices. |
| `people-science-skill-maker` | The user wants to add or evolve skills inside this plugin suite. |

## Shareable HITs bundle

Build the portable `hits-study-insights` skill and HITs MCP bundle:

```bash
python plugins/eve-people-science/scripts/build_hits_insights_bundle.py
```

The output is written to `dist/hits-study-insights-mcp.zip`. Recipients can give the
ZIP to an agent with this instruction:

> Extract and load this folder as a skill and MCP.

The bundle contains installation instructions, the complete skill and references, and
a merge-safe MCP configuration. It contains no credentials or user-specific paths.

## MCP servers

The HITs MCP server is declared in the plugin manifest:

```text
.claude-plugin/plugin.json
```

The portable HITs bundle builder derives its `mcp.json` from this declaration so
the marketplace and standalone bundle cannot drift.

## Manager Action Taking source

`manager-action-taking` uses the user-provided Action Planning Taxonomy workbook as its primary source:

```text
references/skills/manager-action-taking/Action Planning Taxonomy.xlsx
```

The generated runtime catalog maps canonical question IDs to distinct focus-area action records:

```text
references/skills/manager-action-taking/gen/question-map.json
references/skills/manager-action-taking/gen/c/
references/skills/manager-action-taking/gen/a/
```

Regenerate all artifacts after replacing the workbook:

```bash
python plugins/eve-people-science/scripts/build_action_plan_taxonomy_index.py
```

CI verifies the transformed index is current with:

```bash
python plugins/eve-people-science/scripts/build_action_plan_taxonomy_index.py --check
```

## Demo data

Survey-analysis workflows should begin by asking:

> Do you have survey data you would like to reference? If not, you can use demo data.

If the user chooses demo data, use:

```text
demo-data/survey/config.json
demo-data/survey/glint_demo_data.csv
```

The demo source is registered in `demo-data/survey/source.json`.

## Analysis engine

Default package:

```bash
pip install "vivaglint[all]==0.1.1"
```

Development pin:

```bash
pip install "git+https://github.com/microsoft/vivaglint_py.git@761d847a8c8d38ff42c78b4501d761350c9fd03f#egg=vivaglint[all]"
```

## Local smoke test

```bash
python plugins/eve-people-science/scripts/run_vivaglint_analysis.py --config plugins/eve-people-science/examples/sample-survey/config.json --output-dir outputs/sample-survey
```

## Privacy stance

Employee survey data is sensitive. This plugin should:

- process files locally unless the user explicitly chooses another route
- suppress small groups before interpretation
- avoid copying raw employee-level rows into narrative outputs
- surface caveats when benchmarks, comparison groups, or statistical power are missing
- require user confirmation before producing customer-facing or manager-facing artifacts
