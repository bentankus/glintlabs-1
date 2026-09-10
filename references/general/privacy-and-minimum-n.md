# Privacy and minimum-N guidance

Employee survey analysis can expose sensitive information even when names are removed. Every skill in this plugin should apply privacy-by-default behavior.

## Default minimum group size

Use `min_group_size >= 5` by default. Use higher thresholds when:

- topics are sensitive
- attributes create many small cells
- results may be shared outside the immediate analyst group
- outputs are manager-facing or customer-facing

## Suppression

Suppress or avoid interpreting results when:

- group size is below threshold
- a segment can be easily re-identified
- attrition data plus attributes creates small cells
- comments or topics point to identifiable events
- manager hierarchy reveals a small team

## Output rules

Do not include raw employee-level rows in narrative outputs.

Do not include:

- employee IDs
- names
- emails
- exact small group counts when sensitive
- raw comments unless explicitly approved and privacy-reviewed

Prefer:

- aggregated patterns
- directional findings
- suppressed-cell notices
- caveats and readiness flags

## Manager-facing caution

Manager-facing outputs should be extra conservative. A manager should not receive data that makes it possible to infer how a specific person responded.
