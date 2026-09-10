---
name: nezha-clickhouse
description: "Write, review, and troubleshoot ClickHouse SQL for Viva Glint telemetry in Nezha, especially `vivasuite.viva_glint_usage`, with schema guidance and query best practices."
allowed-tools: Bash, Read, Glob, Grep
---

# Nezha ClickHouse

Write, review, and troubleshoot ClickHouse SQL for Viva Glint telemetry in Nezha,
especially `vivasuite.viva_glint_usage`.

## Use when

- The user asks for help querying Nezha, ClickHouse, or Superset telemetry.
- The user asks about Viva Glint usage schema, event names, or flattened telemetry
  fields.
- The user wants to build or review rolling SAU, active-user, event-rate, funnel,
  Copilot usage, or report-section telemetry queries.
- The user asks why two ClickHouse queries return different outputs.
- The user needs schema interpretation or best practices for `EventMetaData_*` or
  `EventPropertyBag_*` fields.

Do not use this skill to interpret survey-result files or vivaglint analysis
manifests. Use `analyze-survey`, `analysis-qa`, or `interpret-analysis` for those
jobs.

## Required grounding

Inspect references in this order:

1. `references/skills/nezha-clickhouse/`
2. `references/general/`

Use the reference folder for schema provenance, recurring query caveats, and
ClickHouse idioms. Treat embedded field definitions as durable working knowledge,
but still validate event names and sparsely populated fields with discovery queries
when the answer depends on current telemetry.

## Core stance

Act as a senior analytics engineer for Viva Glint telemetry in Nezha. Optimize for:

- correct metric semantics
- privacy-safe aggregation
- reproducible ClickHouse SQL
- clear caveats around event definitions, lookback windows, and denominator choice

Prefer concrete SQL over vague guidance when the user is asking for a query.

If the user provides a query, first identify what it measures:

- numerator
- denominator
- grain
- date scan window
- output window
- tenant filters
- whether it is daily, monthly, point-in-time, cumulative, or rolling
- whether `serverMetric` events are intentionally included

Then explain or revise it.

If the user asks for a new query, ask only for missing essentials that materially
change the metric: event names, grain, date window, denominator, numerator,
test-tenant handling, and whether server metrics should be included.

## Privacy and data handling

- Treat employee and tenant telemetry as sensitive.
- Do not expose raw user-level rows unless the user explicitly asks and it is
  necessary.
- Prefer aggregate outputs using `uniqExact(AADObjectId)`, `uniqExactIf`, grouped
  counts, or rates.
- Avoid copying raw `AADObjectId`, `OMSTenantId`, `SessionId`, survey UUIDs, or
  client IDs into narrative output unless necessary for debugging.
- For shareable or customer-facing outputs, report aggregated counts/rates and
  include caveats about minimum group size and missing denominator context.

## Main table

Primary table used frequently:

```sql
vivasuite.viva_glint_usage
```

This table stores Viva Glint telemetry flattened by Nezha from nested event
payloads. Glint telemetry starts with nested structures such as `eventSchema`,
`eventMetaData`, `eventPropertyBag`, device info, session info, and tenant/user
identifiers. Nezha exposes declared nested properties as flattened columns.

## Essential columns

| Column | Meaning / usage |
|---|---|
| `EventTime` | Event timestamp. Cast with `toDateTime(EventTime)` and bucket with `toStartOfDay`, `toStartOfWeek`, or `toStartOfMonth`. |
| `EventName` | Specific Glint telemetry event name. Primary filter for behavior definitions. |
| `EventType` | Event category/type such as `click`, `view`, `scroll`, or `serverMetric`. Exclude `serverMetric` for user-behavior metrics unless intentionally analyzing server-side metrics. |
| `AADObjectId` | User identifier for distinct user counts. Use only in aggregate outputs. |
| `OMSTenantId` | AAD tenant GUID. Not a human-readable Glint client name. |
| `tenant_lookup_IsTestTenant` | Tenant lookup flag. Usually filter with `tenant_lookup_IsTestTenant IN (0)` or `tenant_lookup_IsTestTenant = 0` for production/customer usage. |
| `Product` | Product name. For Glint, usually `VivaGlint`. |
| `Feature` | Feature area. Useful for broad grouping, but event definitions should normally use `EventName`. |
| `SessionId` | Session identifier. Useful for session-level behavior but not a stable person count. |
| `BuildNumber` | App build number. Useful for release validation. |
| `BuildEnvironment` | Environment such as dev/test/prod. Filter if needed. |
| `HtmlElement` | UI element involved in a browser event; useful for debugging but often sparse. |
| `Geo` | Geographic location field; use cautiously because semantics may be broad or sparse. |

## Device columns

Common flattened device fields:

- `DeviceInfo_BrowserName`
- `DeviceInfo_BrowserVersion`
- `DeviceInfo_Id`
- `DeviceInfo_Make`
- `DeviceInfo_Model`
- `DeviceInfo_OsName`
- `DeviceInfo_OsVersion`

Use these for browser/OS diagnostics, not for core business metrics unless
explicitly requested.

## Event metadata columns

Common page/feature metadata:

- `EventMetaData_pageName`
- `EventMetaData_sectionName`
- `EventMetaData_featureName`
- `EventMetaData_subSectionOrTabName`

Use these to validate that an event occurred in the expected page or section. Do
not rely on metadata alone when `EventName` is available and stable.

## Event property bag columns

Frequently seen Glint-specific flattened `EventPropertyBag_*` fields:

| Column | Meaning / usage |
|---|---|
| `EventPropertyBag_fromPage` | Source page for navigation-style events. |
| `EventPropertyBag_toPage` | Destination page for navigation-style events. |
| `EventPropertyBag_surveyType` | Survey program type/context. |
| `EventPropertyBag_surveyUuid` | Survey UUID. Watch for zero/default UUID caveats. |
| `EventPropertyBag_surveyCycleUuid` | Survey cycle UUID. Useful for tying telemetry to a cycle. |
| `EventPropertyBag_surveyProgramUuid` | Survey program UUID. |
| `EventPropertyBag_surveyProgramTemplateUuid` | Program template UUID despite some notes calling it a template name. |
| `EventPropertyBag_fileType` | Export/download file type. |
| `EventPropertyBag_reportSectionType` | Report section type such as heatmap or pulse overview. |
| `EventPropertyBag_subsection` | Team Conversation / Act subsection. |
| `EventPropertyBag_navigationTabLabel` | Primary navigation tab label. |
| `EventPropertyBag_adminSectionId` | Admin section ID; not necessarily an admin-exclusive behavior signal. |
| `EventPropertyBag_suggestedArticleTitle` | Suggested content article title. |
| `EventPropertyBag_suggestedVideoTitle` | Suggested video title. |
| `EventPropertyBag_status` | Status such as success/failure. |
| `EventPropertyBag_viAttributeName` | Viva Insights attribute name. |
| `EventPropertyBag_viProgramsCount_recurring` | Count of recurring programs in VI integration context. |
| `EventPropertyBag_viProgramsCount_adHoc` | Count of ad hoc programs in VI integration context. |
| `EventPropertyBag_viProgramsCount_total` | Total program count in VI integration context. |
| `EventPropertyBag_managerConciergeActionType` | Action in Manager Concierge. |
| `EventPropertyBag_externalBenchmarkLabel` | External benchmark label/type. |
| `EventPropertyBag_bookmarkStatus` | Bookmark state/status. |
| `EventPropertyBag_contentResourceName` | System-standard Glint content resource name. |
| `EventPropertyBag_contentResourceUuid` | Content resource system ID. |
| `EventPropertyBag_relationshipStrengthViewAction` | Action in Relationship Strength view of Work Patterns. |
| `EventPropertyBag_workplacePatternsHeatmapViewAction` | Action in Workplace Patterns heatmap. |
| `EventPropertyBag_hasWorkplacePatternsSections` | Whether report has Workplace Patterns sections. |
| `EventPropertyBag_clonedFromTemplateUuid` | Source report template UUID. |
| `EventPropertyBag_reportTemplateName` | Report template name, observed for `ExportReport`. |
| `EventPropertyBag_colorThemingSet` | Custom branding color setting flag. |
| `EventPropertyBag_customLogoUsage` | Custom logo usage flag. |
| `EventPropertyBag_logoUpload` | Custom logo upload flag. |
| `EventPropertyBag_resetColors` | Reset colors flag. |
| `EventPropertyBag_toggleCustomBranding` | Custom branding toggle flag. |
| `EventPropertyBag_urlUploaded` | Custom logo URL upload/set flag. |

Additional related fields seen in telemetry notes:

- `EventPropertyBag_clientId`: numeric Glint client identifier, useful with
  `OMSTenantId` to disambiguate SAMI tenants sharing one AAD tenant.
- `EventPropertyBag_jobName`: server-side subsystem/job name.
- `EventPropertyBag_aggregationDate`: server-side metric aggregation date; may
  default to current UTC date when omitted.
- `EventPropertyBag_metricType`: server-side metric wire-name/category.
- `EventPropertyBag_metricValue`: server-side metric value.
- `BaseTypeIsExportable`, `BaseTypeIsIntentional`, `BaseTypeIsPremium`: server
  event base-type flags.
- `EventLoggedFrom`: logging origin; server-side examples may use `BE`.

## Schema behavior and pitfalls

- Nezha flattens nested telemetry properties into columns. Example: nested
  `eventPropertyBag.toggleValue` can become `EventPropertyBag_toggleValue` or a
  similarly named configured flattened column.
- Logging a property is not enough. Nested properties must be declared in Nezha
  schema configuration before they become queryable flattened columns.
- Field extraction is case-sensitive and path-sensitive. Watch for casing drift
  such as `region` vs `Region` and for dot-path mismatches.
- If a declared column is always empty, check both sides: whether the source event
  actually populates the property and whether the Nezha declaration uses the exact
  path and casing.
- Treat `OMSTenantId` as a tenant GUID, not a Glint client name. For client-level
  analysis, use available tenant/client lookup fields or `EventPropertyBag_clientId`
  when present.
- Do not assume every event has every metadata/property field. Sparse columns are
  normal.
- Distinguish user behavior events from server metrics. `EventType = 'serverMetric'`
  changes the meaning of counts.

## Standard filters

For production user-behavior metrics, usually start with:

```sql
WHERE EventTime >= now() - INTERVAL 180 DAY
  AND EventTime < now()
  AND tenant_lookup_IsTestTenant IN (0)
  AND EventType NOT IN ('serverMetric')
```

Add event filters with `EventName IN (...)` or `has(event_array, EventName)`.

Use quoted column names only when needed. The table generally works with unquoted
identifiers such as `EventTime`, `EventName`, and `AADObjectId`.

## Date and grain patterns

Daily grain:

```sql
toStartOfDay(toDateTime(EventTime)) AS __timestamp
```

Monthly grain:

```sql
toStartOfMonth(toDateTime(EventTime)) AS __timestamp
```

For Superset charts, use `__timestamp` as the time column alias when returning
time series.

Prefer parameter-like constants at the top of the query:

```sql
WITH
  365 AS date_window_start,
  180 AS rolling_avg_days
```

## Distinct user counting

Simple distinct users:

```sql
uniqExact(AADObjectId) AS users
```

Conditional distinct users:

```sql
uniqExactIf(AADObjectId, EventName IN ('SubmitCopilotPrompt')) AS prompt_users
```

When `WHERE` already restricts to the event set, `uniqExactStateIf(AADObjectId,
1=1)` is equivalent to unconditional counting inside that filtered population.
Keep conditions in one place when possible.

## Rolling 180-day SAU pattern

For rolling distinct users by day, the common Nezha/Superset pattern uses
aggregate states plus a window merge:

```sql
WITH
  365 AS date_window_start,
  180 AS rolling_days
SELECT
  __timestamp,
  uniqExactMerge(user_state) OVER (
    ORDER BY __timestamp ASC
    RANGE BETWEEN 86400 * (rolling_days - 1) PRECEDING AND CURRENT ROW
  ) AS rolling_users
FROM (
  SELECT
    toStartOfDay(toDateTime(EventTime)) AS __timestamp,
    uniqExactState(AADObjectId) AS user_state
  FROM vivasuite.viva_glint_usage
  WHERE EventTime >= addDays(toStartOfDay(now()), -date_window_start)
    AND EventTime < now()
    AND tenant_lookup_IsTestTenant IN (0)
    AND EventType NOT IN ('serverMetric')
    AND EventName IN ('SubmitCopilotPrompt')
  GROUP BY __timestamp
)
ORDER BY __timestamp;
```

Important: `RANGE` is in seconds for timestamps. `86400 * 179 PRECEDING AND
CURRENT ROW` gives an inclusive 180-day window when the current day is included.
`86400 * 180` can behave like a 181-day inclusive range. Call out this off-by-one
risk when comparing queries.

For early rows, make sure the source date filter starts far enough back to cover
the rolling lookback. If the output date range starts today minus 180 days but the
scan also starts there, early output rows have incomplete rolling windows.

## Denominator / numerator best practices

Always define denominator and numerator populations explicitly.

Example: monthly high-confidence Copilot users among users who saw Copilot
Highlights impressions:

```sql
WITH
  [
    'ClickCopyCopilotHighlights',
    'ClickCopyCopilotSummaryInCommentsPanel',
    'ClickCopilotCopyResponseInSidecar',
    'ClickCopilotResponseThumbUp',
    'ClickCopilotSummaryThumbUpInCommentsPanel'
  ] AS high_confidence_events,

impression_users AS (
  SELECT DISTINCT
    toStartOfMonth(toDateTime(EventTime)) AS month,
    AADObjectId
  FROM vivasuite.viva_glint_usage
  WHERE EventTime >= now() - INTERVAL 180 DAY
    AND EventTime < now()
    AND tenant_lookup_IsTestTenant = 0
    AND EventType NOT IN ('serverMetric')
    AND EventName = 'ImpressionCopilotHighlights'
),

fixed_high_confidence_users AS (
  SELECT DISTINCT
    toStartOfMonth(toDateTime(EventTime)) AS month,
    AADObjectId
  FROM vivasuite.viva_glint_usage
  WHERE EventTime >= now() - INTERVAL 180 DAY
    AND EventTime < now()
    AND tenant_lookup_IsTestTenant = 0
    AND EventType NOT IN ('serverMetric')
    AND has(high_confidence_events, EventName)
),

prompt_high_confidence_users AS (
  SELECT DISTINCT
    month,
    AADObjectId
  FROM (
    SELECT
      toStartOfMonth(toDateTime(EventTime)) AS month,
      toDate(toDateTime(EventTime)) AS event_date,
      AADObjectId
    FROM vivasuite.viva_glint_usage
    WHERE EventTime >= now() - INTERVAL 180 DAY
      AND EventTime < now()
      AND tenant_lookup_IsTestTenant = 0
      AND EventType NOT IN ('serverMetric')
      AND EventName = 'SubmitCopilotPrompt'
    GROUP BY month, event_date, AADObjectId
    HAVING count() >= 3
  )
),

high_confidence_users AS (
  SELECT month, AADObjectId
  FROM (
    SELECT month, AADObjectId FROM fixed_high_confidence_users
    UNION DISTINCT
    SELECT month, AADObjectId FROM prompt_high_confidence_users
  )
)

SELECT
  i.month AS __timestamp,
  uniqExact(i.AADObjectId) AS impression_users,
  uniqExact(h.AADObjectId) AS high_confidence_users,
  high_confidence_users / nullIf(impression_users, 0) AS high_confidence_rate
FROM impression_users i
LEFT JOIN high_confidence_users h
  ON i.month = h.month
 AND i.AADObjectId = h.AADObjectId
GROUP BY __timestamp
ORDER BY __timestamp;
```

Use `nullIf(denominator, 0)` to avoid divide-by-zero. Prefer `LEFT JOIN` from
denominator to numerator when computing rates constrained to a population.

## Event-set practices

- Define event arrays at the top of the query for readability.
- Use `has(array_name, EventName)` for membership checks.
- Keep special event logic separate. Example: `SubmitCopilotPrompt` may require a
  threshold rule such as 3+ prompts by a user in one day = high confidence; 1-2
  prompts = lower confidence.
- Do not mix impression, open, click, submit, copy, thumbs-up, and
  generated/sidecar events without labeling behavioral confidence.
- Common Copilot/Glint events seen in prior queries include:
  - `SubmitCopilotPrompt`
  - `SelectCopilotFirstLoadPromptGuide`
  - `SelectCopilotPromptGuide`
  - `ClickCopilotSummarizeInCommentsPanel`
  - `ImpressionCopilotHighlights`
  - `ClickCopyCopilotHighlights`
  - `ClickCopyCopilotSummaryInCommentsPanel`
  - `ClickCopilotCopyResponseInSidecar`
  - `ClickCopilotResponseThumbUp`
  - `ClickCopilotSummaryThumbUpInCommentsPanel`
  - `OpenCopilotFromReport`
  - `OpenCopilotFromDashboard`
  - `ClickRewriteCopilotRewrite`
  - `ClickDismissSuggestionCopilotRewrite`
  - `ClickReplaceCopilotRewrite`
  - `ClickViewMoreCopilotHighlights`
  - `ClickTryAgainCopilotHighlights`
  - `OpenCopilotPromptGuide`
  - `ClickCopilotSummaryThumbDownInCommentsPanel`
  - `ClickCopilotResponseThumbDown`
  - `ClickRegenerateCopilotHighlights`
  - `CloseCopilotSidecar`
  - `ClickCollapseCopilotHighlights`
  - `StopCopilotGenerating`
  - `ClickCopilotSidecarWidthExpand`
  - `ClickCopilotSidecarWidthStandard`

## Query review checklist

When reviewing or comparing queries, check:

1. Same date scan window and same output window?
2. Enough historical lookback for rolling metrics?
3. Same grain (`day`, `week`, `month`) and same timezone assumptions?
4. Same denominator population?
5. Same numerator event set and special rules?
6. Same test tenant filter (`tenant_lookup_IsTestTenant = 0`)?
7. Same `EventType` handling, especially `serverMetric` exclusion?
8. Same distinct ID (`AADObjectId`, not session ID unless session metric)?
9. Same rolling-window width (`86400*179` vs `86400*180`)?
10. Same join direction and deduping approach?
11. Is alias reuse valid in the query context, or should expressions be
    repeated/subqueried?
12. Are property bag columns sparse or newly declared, requiring null diagnostics?

## Troubleshooting patterns

Find recent values for a field/event:

```sql
SELECT
  EventName,
  EventType,
  count() AS events,
  uniqExact(AADObjectId) AS users,
  min(EventTime) AS first_seen,
  max(EventTime) AS last_seen
FROM vivasuite.viva_glint_usage
WHERE EventTime >= now() - INTERVAL 30 DAY
  AND tenant_lookup_IsTestTenant = 0
  AND EventName ILIKE '%Copilot%'
GROUP BY EventName, EventType
ORDER BY events DESC
LIMIT 100;
```

Check whether a property bag column is populated:

```sql
SELECT
  EventName,
  count() AS events,
  countIf(isNotNull(EventPropertyBag_reportSectionType) AND EventPropertyBag_reportSectionType != '') AS populated,
  anyHeavy(EventPropertyBag_reportSectionType) AS example_value
FROM vivasuite.viva_glint_usage
WHERE EventTime >= now() - INTERVAL 30 DAY
  AND tenant_lookup_IsTestTenant = 0
GROUP BY EventName
HAVING populated > 0
ORDER BY populated DESC
LIMIT 100;
```

Find event examples by page/section:

```sql
SELECT
  EventMetaData_pageName,
  EventMetaData_sectionName,
  EventName,
  count() AS events,
  uniqExact(AADObjectId) AS users
FROM vivasuite.viva_glint_usage
WHERE EventTime >= now() - INTERVAL 30 DAY
  AND tenant_lookup_IsTestTenant = 0
  AND EventType NOT IN ('serverMetric')
GROUP BY
  EventMetaData_pageName,
  EventMetaData_sectionName,
  EventName
ORDER BY users DESC
LIMIT 200;
```

## Output style

When producing SQL, include short comments that explain metric intent,
denominator, numerator, and caveats. For explanations, lead with the metric
meaning and likely output differences, then list only the important technical
differences.

When uncertain about event names or field availability, say so explicitly and
provide a discovery query instead of inventing names.
