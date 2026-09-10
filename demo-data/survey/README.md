# Demo survey data

Use this dataset when the user wants to analyze a survey but does not provide their own data.

## Intake prompt

Every survey-analysis workflow should start by asking:

> Do you have survey data you would like to reference? If not, you can use demo data.

If the user chooses demo data, use:

```text
plugins/eve-people-science/demo-data/survey/glint_demo_data.csv
plugins/eve-people-science/demo-data/survey/config.json
```

## Source

The demo dataset was registered from the EVE SharePoint source provided by the user:

```text
https://microsoft.sharepoint-df.com/:x:/t/EVE/cQp9diwRxAXGSYk_rMGtyVYaEgUCXqA9ae9jA97SvFtVYBRCGw
```

The local file is stored as CSV because the analysis runner expects tabular survey inputs and this demo source is a wide survey-item dataset.

## Format

This is a `wide_items` dataset:

- `user_id` is the employee/respondent identifier for demo purposes.
- numeric `Q_*` columns are survey item responses.
- `client_uuid`, `survey_cycle_title`, and `survey_cycle_id` are available as context/attribute columns.

Do not treat this as real employee data. It is for demos, smoke tests, and examples.
