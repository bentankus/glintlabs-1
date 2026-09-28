# Interactive survey report contract

Every successful `analyze-survey` run must produce an interactive HTML report
in this format. This contract is required, not an optional example.

The exact golden example is:

```text
golden-report.html
```

Its SHA-256 at adoption, calculated from canonical LF-normalized bytes, is
`5bb0a7f68687b8b6be6dc0460c6caa0adbdb7059694a48a17999facd01af8c5a`.
Generated reports in `required` mode must match its static HTML shell exactly.
The intended substitution is the JSON value assigned to `const D`. In `off`
mode, the six empty AI summary containers are also removed from the generated
report.

## AI-generated People Science summary modes

The shared report builder supports three explicit modes:

- `off`: render no AI summary cards, ignore any stale summary file, and exclude
  that file from the share ZIP. This is the default for `analyze-survey`.
- `optional`: render summaries only when a valid summary file exists; otherwise
  render no summary cards.
- `required`: fail report generation unless a valid summary file exists. This
  is required by `analyze-survey-ai-preview`.

Always create `people-science-summary-context.json` from aggregate results so a
completed analysis can be reused by the preview workflow without rerunning the
codebooks. When summaries are enabled:

- Require six summary objects for schema stability: Scores change,
  Correlation (`relationships`), Attrition alerts (`alerts`), Factors,
  Attrition analysis, and Downloads. Render only summaries for tabs present in
  the report.
- Each summary must contain a headline, observed evidence, professional
  interpretation, recommended next step, caveat, and published-source links.
- Generate narratives from `people-science-summary-context.json`, never raw
  respondent rows, and conform to `people-science-summaries.schema.json`.
- Use `interpret-analysis` guardrails and
  `people-science-knowledge-vault` source priority. Do not present correlation,
  factors, alerts, or attrition associations as causal.
- Recalculate summaries when the report attribute or value changes. Authored
  segment narratives take precedence over live aggregate summaries.
- Select three public references for each rendered summary using
  `people-science-source-index.json`.

The deterministic implementation is
`scripts/build_interactive_report.py`. The analysis runner invokes it
automatically after repeatability passes. Do not rely on an agent to recreate
the dashboard from prose or maintain a second handwritten template.

## Required package

Create:

```text
<analysis-name>-report.html
<analysis-name>-share.zip
```

The ZIP must contain:

```text
OPEN_REPORT.html
SHARING_README.txt
analysis-manifest.json
completed aggregate CSV/JSON artifacts
```

`OPEN_REPORT.html` is the report renamed as the obvious entry point. Exclude
raw respondent data, employee-property files, comments, and repeatability
staging data from the ZIP.

## Visual contract

- Load and follow `references/design/glint-ui-system.md`, which points to the
  published `glint-ui-system` skill and canonical upstream reference.
- Adapt the visual hierarchy of the Glint Labs Figma Home frame: a rounded
  masthead, editorial report hero, pill navigation, generous whitespace,
  resource-style cards and downloads, and a high-contrast closing section.
  Preserve the Glint UI system as the token and accessibility authority.
- Use the hero for a deterministic **current survey summary**, not generic
  marketing copy. It must update with the shared report filter and show:
  latest privacy-eligible cycle and response count, average item score, the
  three high-scoring items, the three low-scoring items, privacy-safe aggregate
  comment themes for each item when available, and average/leading movement
  from the prior cycle when available.
- Prefer score-ranked items with sufficient linked comment coverage when at
  least six are available. Otherwise retain the full score ranking and state
  when an item has no privacy-eligible linked themes. Describe all results as
  relative positions within the current survey. Do not imply an external
  benchmark, root cause, or causal interpretation. Keep the summary available
  in summary mode `off`.
- Derive comment themes locally using deterministic keyword coding. Count a
  theme at most once per comment, require at least five comments and roughly
  2% recurrence in the applicable item/cut, and show no more than three theme
  labels per item. Raw comments must never enter HTML, AI prompts or context,
  the share ZIP, or chat.
- Force the light Glint report theme; do not follow operating-system dark mode.
- Use a white canvas, `#FAFAFA` supporting surfaces, `#335CCC` as the primary
  Glint blue, `#E5EEFF` for blue tint, Glint status colors, and the approved
  favorable/unfavorable treatments.
- Use Segoe UI typography, approved Glint radii, subtle
  borders and shadows, accessible focus states, and responsive layouts.
- Keep analytical tables and charts dense enough for comparison; apply the
  editorial treatment around them rather than weakening statistical encodings.
- Do not substitute a generic dashboard theme.

## Required navigation

Keep this tab order and naming:

1. **Scores change**
2. **Correlation**
3. **Factors**
4. **Attrition analysis** (only when attrition completes)
5. **Attrition alerts** (only when attrition completes)
6. **Downloads**

If attrition cannot run, omit both attrition tabs. Never fabricate attrition
data. For other analyses, keep the tab and explain why results are unavailable.

## Shared report filter

Place one report-level attribute/value filter above the tabs.

- Apply it to Scores change, Correlation, Attrition analysis, and Attrition
  alerts.
- Treat it as a parent filter. Attrition alerts must select their displayed
  dimensions within the selected segment.
- Use saved aggregate values in the browser. Do not embed or recalculate from
  respondent-level rows.
- Suppress unavailable intersections explicitly instead of silently reverting
  to company results.
- Preserve categorical attributes as categories. For genuinely numeric
  attributes with more than 10 distinct values, create about five
  non-overlapping, clearly labeled buckets.

## Tab behavior

### Scores change

- Follow `scores-change-format.png`.
- Let the user select old and new cycles when more than two are available.
- Add a **Respondent population** sub-heading with **All respondents** and
  **Repeat respondents** options.
- Define repeat respondents as employees represented in both selected cycles.
  Precompute these matched populations locally; do not derive them from
  aggregate counts in the browser.
- Use grouped cycle headers with Mean, Stddev, and n subcolumns.
- Show a P-Value column with a visible significance indicator.
- Show Score Difference (New - Old) with a proportional horizontal data bar
  and the signed numeric difference.
- Keep questions in survey order and use alternating row shading.
- Apply the shared report filter only when both cycles meet minimum N.

### Correlation

- Run the full Pearson correlation analysis and show the complete item-by-item
  matrix.
- Classify absolute relationship strength as Low (`|r| < .30`), Medium
  (`.30-.49`), High (`.50-.69`), or Very high (`>= .70`) and give each band a
  distinct, labeled matrix color.
- Include a control to turn strength colors on or off without changing the
  displayed values.
- Include a minimum-strength filter for All, Medium or higher, High or higher,
  and Very high only.
- Include a control to show or hide statistical-significance markers.
- Keep significance markers off by default to reduce visual noise.
- Let users add and individually remove multiple highlighted questions. Dim
  unrelated cells and emphasize selected row/column headers and cells.
- Show full question names on both axes. Use compact regular-weight text, with
  vertical column labels and horizontal row labels.
- Cluster questions with deterministic average-linkage hierarchical clustering
  using positive-correlation distance (`1 - r`).
- Recommend the cluster count with the highest average silhouette score among
  3 through 15 clusters, capped below the number of questions. Treat ties as a
  reason to prefer the smaller cluster count.
- Show the recommendation in a short blurb above the matrix.
- Provide every cluster-count option from 3 through 10. If the recommendation
  is greater than 10, extend the dropdown through the recommended count.
- Default the dropdown to the recommendation. Reorder both axes by cluster and
  show labeled cluster boundaries without replacing relationship-strength
  colors.
- Treat clusters as exploratory groupings, not validated survey constructs.
- Keep the legend and summary compact, hide empty highlight/detail regions, and
  reveal relationship details only after a cell is selected.
- Clicking a cell shows `r`, p-value, N, and significance status.
- State how many unique relationships are significant and nonsignificant.
- Emphasize practical magnitude when large N makes most results significant.
- Save segment matrices only where there are at least 30 response rows.

### Attrition alerts

- For each report attribute and outcome window, calculate each item's median
  attrition multiplier across privacy-eligible attribute values.
- Rank items by that median and retain the top five per attribute.
- Show Attribute, Group, Attrition item, Group score, Company score, Gap,
  Attrition multiplier, and N.
- At company level, show the lowest-scoring privacy-eligible group for each top
  item and attribute. Sort the table by the largest negative score gap first.
- When an attribute/value filter is selected, show that group's results for the
  selected attribute's top five items.
- Exclude an attrition row when either its favorable or unfavorable category N
  is below the configured minimum. Continue applying normal report minimum-N
  suppression to the displayed group score.
- Provide 90-, 180-, and 365-day controls when those outcome windows exist.
  Default to 180 days when it has eligible alerts; otherwise default to the
  first outcome window with eligible alerts.
- Describe alerts as aggregate screening signals. Do not present multipliers as
  individual predictions or group score gaps as causal explanations.

### Factors

- Re-estimate the rotated factor loadings whenever the report attribute or
  value changes, using the company solution's factor count and the same
  extraction method and rotation.
- Require at least the greater of 100 complete responses or five complete
  responses per survey item. Show an explicit suppression or estimation
  failure reason when a cut is not eligible.
- Show the selected cut, complete-response N, factor count, rotation, leading
  item loadings, and clustered horizontal loading bars. Use one small-multiple
  panel per loading dimension, repeat the horizontal loading axis in every
  panel, and show the shared vertical question labels only once.
- Plot loading magnitudes on a positive `0` to `1` axis. Apply the same
  strength bands and colors as Correlation: Low (`< .30`), Medium
  (`.30-.49`), High (`.50-.69`), and Very high (`>= .70`).
- Sort the shared question axis from high to low by each item's MR1 loading
  only; do not combine loading values across dimensions for sorting. Give
  every bar a high-contrast outline and
  every two-decimal loading label a contrasting outline for readability.
- Explain that factor labels are working hypotheses, factor numbers can rotate
  or reorder across cuts, and filtered solutions do not establish measurement
  invariance.

### Attrition analysis

- When valid outcome and date inputs exist, show overall, tenure, and
  organization views first.
- Rank eligible items by multiplier and display each item text with a
  horizontal bar and labeled multiplier. Mark 1.00x as the reference point.
- Do not display favorable or unfavorable counts or percentages in the report.
  Retain them only in the privacy-safe aggregate artifact for auditability and
  suppression enforcement.
- If attrition cannot run, omit both Attrition analysis and Attrition alerts.
- Never generate synthetic attrition outcomes.

### Downloads

Link the manifest and every completed aggregate artifact, including derived
correlation matrices, score-change, and alert outputs when available.

## Privacy and performance

- Default minimum displayed group size is 5.
- Keep respondent-level data local and outside the shareable package.
- Exclude identifier-like employee, respondent, manager, team, client, UUID,
  and GUID columns from report filters and aggregate downloads.
- Precompute score, distribution, change, correlation, and attrition-alert
  aggregates. Browser interactions must select saved values rather than rerun
  analysis over employee rows.
- Validate all download links and JavaScript syntax before sharing.
- Require the standard two-run repeatability check before generating a
  user-facing report.

## Sharing guidance

The default shareable artifact is the ZIP. Recipients extract it and open
`OPEN_REPORT.html`. A normal SharePoint document-library URL may download or
sandbox HTML and block JavaScript. For browser-only hosting, use an approved
static web host or an SPFx implementation.
