# HITs retrieval playbook

This playbook captures observed HITs connector behavior and the safeguards required
for reproducible People Science retrieval.

## Observed connector behavior

- A group URL may be interpreted as a semantic query instead of a membership listing.
- A response may stop at 20 records even when the group contains more.
- Requests for exact IDs or exact body phrases may still return semantic neighbors.
- The record-level `group` field can identify the study's originating research
  organization rather than membership in the curated People Science group.
- Large `hits-view` responses may be written to a temporary file instead of returned
  inline.

## Required corpus checks

1. Establish the current expected member count from the group.
2. Obtain or reconstruct the group member-ID set.
3. Retrieve in batches when the response cap is lower than the member count.
4. Keep only requested member IDs after every batch.
5. Deduplicate by study ID.
6. Confirm that every retained record has a complete body before corpus-wide counting.
7. Stop and report the gap when the expected count, distinct-ID count, or complete-body
   count differs.

Never describe a corpus as complete merely because a tool call reports `COMPLETED`.

## Body normalization

Before counting:

- remove the title line
- remove navigation, subscription, privacy, and standard Research Drop boilerplate
- remove HTML attributes and citation markup while preserving visible prose
- normalize case, punctuation, Unicode hyphens, and whitespace
- merge only documented singular/plural and hyphen variants
- preserve multi-word phrases

Do not count URLs, markup fragments, references, or repeated page furniture as topics.

## Specificity guard

Generic words such as `AI`, `employee`, `manager`, `team`, `use`, `support`, and
`training` are not valid ranking topics by themselves. Use a specific phrase or
validated concept, such as:

- `AI adoption`
- `manager role modeling`
- `organization-sponsored AI tools`
- `role-specific AI training`
- `psychological safety`

This prevents a study from ranking highly merely because it repeats a common actor
word such as `manager`.

## Tested prompt mappings

These mappings are starting points, not fixed query expansions.

| User intent | Primary concepts | Directly relevant adjacent concepts |
|---|---|---|
| Sustainable Copilot adoption | Copilot; AI adoption | AI tools; AI transformation; AI value; training; burnout; psychological safety |
| AI enablement | AI adoption; organization-sponsored AI tools; role-specific AI training | HR-IT collaboration; manager role modeling; psychological safety; AI value |
| Make sure my team uses AI | AI adoption; team AI use | manager role modeling; approved AI tools; role-specific training; use cases; psychological safety; critical evaluation |
| Employee listening | Employee Listening; employee feedback; employee surveys | action taking; Viva Glint; conversational feedback |

Start with the user's exact intent, select the smallest useful mapping, and recount the
current bodies. Do not automatically add every adjacent concept.

## Selection audit

Retain this internal diagnostic for each run:

| Rank | Study ID | Exact phrase count | Weighted topic frequency | Topic coverage | Tag score | Published |
|---|---|---:|---:|---:|---:|---|

Show it only when the user asks how studies were selected or when testing the skill.
