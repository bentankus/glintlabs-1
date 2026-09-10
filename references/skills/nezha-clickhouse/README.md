# Nezha ClickHouse references

First-priority reference folder for the `nezha-clickhouse` skill.

## Source knowledge captured

This skill packages working knowledge from recurring Viva Glint Nezha / ClickHouse
query work:

- primary table: `vivasuite.viva_glint_usage`
- event-time grain patterns for Superset time series
- rolling 180-day SAU patterns using `uniqExactState` and `uniqExactMerge`
- common user-behavior filters:
  - `tenant_lookup_IsTestTenant = 0`
  - `EventType NOT IN ('serverMetric')`
- schema behavior for flattened `EventMetaData_*` and `EventPropertyBag_*`
  columns
- Copilot/Glint event sets used in prompt, highlights, copy, thumb, and sidecar
  usage queries

## Schema cautions

- Nezha only exposes nested properties as flattened queryable columns after the
  property path is declared in schema configuration.
- Property extraction is case-sensitive and exact-path-sensitive.
- Sparse property bag columns are normal. Validate field population before using a
  column as a numerator, denominator, or segment.
- `OMSTenantId` is an AAD tenant GUID, not a human-readable Glint client name.
- `EventPropertyBag_clientId`, when available, can help disambiguate Glint clients
  that share a SAMI/AAD tenant.

## Query cautions

- For inclusive 180-day rolling daily windows, prefer `86400 * 179 PRECEDING AND
  CURRENT ROW`; `86400 * 180` can include 181 days.
- Make the scan window longer than the displayed output window when calculating
  rolling metrics, otherwise early rows have incomplete history.
- Define numerator and denominator populations explicitly, preferably as separate
  CTEs.
- Use `nullIf(denominator, 0)` for rates.
- Use `LEFT JOIN` from denominator to numerator when computing rates constrained
  to an exposure or eligible population.
- Treat `SubmitCopilotPrompt` carefully when a metric distinguishes light use from
  high-confidence use; threshold rules such as 3+ prompts by user/day should be
  isolated in their own CTE.
