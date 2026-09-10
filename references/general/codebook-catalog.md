# Codebook catalog

This catalog maps analysis jobs to `vivaglint` functions and downstream interpretation use.

| Codebook | `vivaglint` function | Primary question | Output artifact |
|---|---|---|---|
| Descriptives | `summarize_survey` | What are the central patterns by survey item? | `descriptives.csv` |
| Response distribution | `get_response_dist` | How are responses distributed across scale points? | `response_distribution.csv` |
| Correlations | `get_correlations` | Which survey items move together? | `correlations.csv` |
| Factor analysis | `extract_survey_factors` | What latent constructs may organize the item set? | `factor_analysis_summary.csv` |
| Cycle comparison | `compare_cycles` | What changed across survey cycles? | `cycle_comparisons.csv` |
| By-attribute analysis | `analyze_by_attributes` | Where do patterns differ across groups? | `by_attribute.csv` |
| Attrition analysis | `analyze_attrition` | Which responses are associated with later attrition? | `attrition.csv` |

## Analysis selection rules

- Always run descriptives first. Most interpretation depends on item-level response patterns.
- Run response distribution when favorability or polarization matters.
- Run correlations when prioritizing drivers, redundancy, or potential themes.
- Run factor analysis only when there are enough respondents and items to support stable extraction.
- Run cycle comparison only when ordered cycle inputs are provided.
- Run by-attribute analysis only when attributes are present and minimum group-size suppression is configured.
- Run attrition only when attrition data is present and the termination date column is explicitly named.

## Default guardrails

- Minimum group size should default to 5 or higher.
- Do not interpret small segments as meaningful when suppression removes most rows.
- Do not treat correlation as causation.
- Do not treat factor labels as ground truth; they are hypotheses.
- Do not compare cycles without checking whether item wording, scale, population, or survey program changed.
- Do not create manager recommendations from attrition associations alone.
