# People Science Knowledge Vault references

This folder defines the source hierarchy for `people-science-knowledge-vault`.

Start with `source-priority.md`. It is the authoritative retrieval contract: it
identifies the published Viva Blog corpus and curated externally facing resources
(first priority), Microsoft Learn and Adoption Center documentation (second
priority), the external-only workbook worksheet (third priority), exclusions, and
refresh rules.

Other files in this folder are generated or curated views of that same contract,
not replacements for it:

- `catalog.json` - a canonical, structured catalog of already-known resources
  (id/title/url/tier/theme/description), tagged by priority tier. It is kept in
  sync with `skills/analyze-survey/references/people-science-source-index.json`
  by `scripts/build_knowledge_vault_resources.py`, which fails if the two drift.
- `prioritized-resources.md` - a generated, human-readable ranked table built from
  `catalog.json`. Regenerate it with
  `python scripts/build_knowledge_vault_resources.py` after editing `catalog.json`;
  do not hand-edit it.
- `workbook-schema.json` - a machine-readable description of the People Science
  content workbook (worksheet name, expected columns, exclusions, observed date and
  record count, staleness rule), so workbook drift can be checked mechanically
  instead of only in prose.

Do not add internal or unpublished material to this folder. See
`tests/test_knowledge_vault_catalog.py` for the checks that enforce catalog
integrity and consistency with the workbook schema and `analyze-survey`'s index.
