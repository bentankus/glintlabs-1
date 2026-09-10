# Action Planning Taxonomy

This workbook is the primary source for Manager Action Taking recommendations.

## Source

```text
Action Planning Taxonomy.xlsx
```

SharePoint source:

```text
https://microsoft.sharepoint-df.com/:x:/r/teams/EVE/_layouts/15/Doc.aspx?sourcedoc=%7B0F15DEAC-2FD9-4324-9CDC-DADF01AED66C%7D&file=Action%20Planning%20Taxonomy.xlsx&action=default&mobileredirect=true&share=cQqs3hUP2S8kQ5zc2t8BrtZsEgUC16tQCPV2ZNTnlKYSFg7kWQ&CID=D800A8D6-41EE-4F68-AB87-33B90E17CF69
```

Generated runtime artifacts:

```text
gen/catalog.json
gen/question-map.json
gen/c/
gen/a/
gen/validation-report.json
```

Regenerate them with:

```bash
python plugins/eve-people-science/scripts/build_action_plan_taxonomy_index.py
```

Verify that the generated index is current with:

```bash
python plugins/eve-people-science/scripts/build_action_plan_taxonomy_index.py --check
```

## Primary sheet

Use the visible sheet `APTemplate_FocusAreas_Ext`. Header row is row 3.

Core columns:

| Column | Use |
|---|---|
| `question_uuid` | Maps one or more symbolic survey question IDs to eligible action records. |
| `action_plan_template_uuid` | Stable template identifier. |
| `sequence` | Source catalog order and temporary row-level identity within the template. |
| `AP Template` | Human-readable action-plan template name. |
| `Focus Areas Title` | Unique manager focus area represented by this record. |
| `Content Description` | First-class action guidance or concise action description. |
| `Content Text Body` | Additional detailed action content when present. |
| `Video Title` / `Video Link` | LinkedIn Learning or embedded video support. |
| `Ext Link 1` - `Ext Link 11` | External resources that can be provided as supporting links. |

## Data model

Each workbook row is a distinct focus-area action record for the question IDs in that row. Rows that share an action-plan template are eligible alternatives in the same candidate set; they are not mandatory ordered steps in one combined plan.

The generated `action_plan_record_id` currently uses:

```text
<action_plan_template_uuid>:<sequence>
```

This is a temporary stable composite until the source workbook provides a dedicated row-level action-record UUID.

## Matching rule

When a survey analysis identifies a question to action:

1. Normalize the question ID by removing brackets or braces around each identifier, trimming whitespace, and uppercasing.
2. Match it against `questions` in `gen/question-map.json`.
3. Load the distinct action records referenced by that question's `action_plan_record_ids`. Use the candidate-set file for shared template metadata and catalog order.
4. If the workbook cell contains multiple question IDs, each ID retains an explicit relationship to the same action records.
5. If no question-ID match exists, do not invent an action plan. Ask for the canonical question ID or use a clearly labeled fallback only if the user provides one.

## Runtime rule

For a matched question:

1. Treat all referenced action records as the authorized focus-area choices for that question.
2. Use `selection-logic.md` to choose and frame the best-fitting action record.
3. Preserve alternative eligible focus areas without implying every record must be completed.

## Golden examples

Use `golden-examples.json` and `golden-examples.md` to validate selection behavior for representative question IDs. These examples are not a replacement for the taxonomy; they are regression expectations for how to choose among authorized records.

## Keeping the index current

The GitHub Actions workflow `.github/workflows/verify-action-plan-taxonomy.yml` runs the `--check` command on push and pull request. If the workbook changes without regenerating the normalized artifacts, the job fails and tells the contributor to regenerate them.

## Important constraint

Do not generate Manager Action Taking advice from general knowledge when matched action records exist. Select among the records authorized for the question; do not search the whole taxonomy for a more convenient answer.
