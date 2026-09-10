# Manager Action Taking selection logic

Use this logic after a low-scoring survey question has been matched to authorized action records through `gen/question-map.json`.

## Core rule

Only choose among action records explicitly authorized for the matched question ID. Do not search the broader taxonomy for a better-sounding action.

## Selection inputs

Use the available evidence in this order:

1. Matched question ID and question wording.
2. Survey evidence from `analysis-manifest.json` and artifacts: score, response distribution, comments/themes if available, segment/cycle context if privacy-safe.
3. Manager context from the user: team situation, constraints, desired artifact, time horizon.
4. Action record metadata: `action_type`, `content_type`, `selection_signals`, title, description, body, resources.
5. Secondary context from `secondary/collaborative-action-taking-act.md`, especially collaboration, small action, and check-in principles.
6. Psychological safety context from `secondary/psychological-safety-techcommunity.md` when the matched question is about voice, trust, inclusion, speaking up, or psychological safety.

## Recommendation logic

| Evidence pattern | Prefer action type |
|---|---|
| People do not know what is happening, why decisions were made, or what priorities mean | `communication` |
| Team needs to discuss survey results, surface barriers, or co-create the plan | `team_conversation` |
| People lack tools, staffing, access, process support, or cross-team help | `resources_and_support` |
| Low trust, belonging, fairness, inclusion, empathy, or psychological safety | `trust_and_inclusion` |
| Career, learning, feedback, coaching, strengths, or skill-building issue | `growth_and_development` |
| Appreciation, energy, morale, celebration, or motivation issue | `recognition_and_motivation` |
| Too much work, unclear priorities, deadlines, time pressure, or focus problems | `workload_and_prioritization` |
| Decision quality, accountability, follow-through, process clarity, or operating rhythm issue | `process_and_accountability` |
| Manager needs to understand their own behavior before acting | `reflection_and_self_assessment` |
| User asks for learning resources or lightweight support material | `resource_learning` |

## Decision phases

Use the available context to decide which phase the manager is in:

| Manager/team state | Best recommendation shape |
|---|---|
| Results are new, unclear, or emotionally charged | Start with an ACT conversation and a `team_conversation` or `trust_and_inclusion` record. |
| The team agrees on the issue but not the solution | Present 2-3 authorized candidates and ask the team to choose one. |
| The problem is concrete and controllable | Recommend one best-fit record with one immediate next step. |
| The issue is systemic or outside the manager's control | Prefer `connector`, `roadblock_remover`, communication, or escalation-oriented records; avoid implying the manager can fix the system alone. |
| The user asks for education or enablement | Prefer `resource_learning` only after naming the behavior the resource should support. |
| The user asks for a deck or presentation | Keep action selection unchanged; use tertiary presentation context only to package the story. |

## Psychological safety secondary lens

For matched voice, speaking-up, inclusion, or psychological-safety questions, prefer authorized records that help managers:

1. check defensive or negative reactivity
2. listen without agenda
3. model vulnerability and normalize mistakes
4. create explicit permission for questions, concerns, and dissent

Use the Tech Community source as supporting evidence and manager behavior guidance. Do not use it to bypass the primary taxonomy match.

## ACT secondary lens

When taxonomy records are otherwise similarly strong, prefer records that support the ACT pattern:

1. **Acknowledge** - helps the manager and team discuss what the feedback is saying.
2. **Collaborate** - invites the team to choose or shape the focus area.
3. **Take one step** - produces a small, visible, near-term action.

This lens should not override question authorization. It only helps choose among records already authorized for the matched question.

## Manager-role lens

Use the secondary action-taking context to identify the manager role implied by the recommendation:

| Role | Prefer when evidence suggests... | Strong record types |
|---|---|---|
| Coach | The team needs confidence, focus, modeling, recognition, or behavior reinforcement. | `team_conversation`, `growth_and_development`, `recognition_and_motivation` |
| Facilitator | The team needs shared interpretation, psychological safety, inclusion, or differing voices heard. | `team_conversation`, `trust_and_inclusion`, `communication` |
| Roadblock remover | The team lacks resources, support, capacity, tools, or escalation paths. | `resources_and_support`, `workload_and_prioritization`, `process_and_accountability` |
| Connector | The team needs leadership context, cross-team coordination, or links to other groups. | `communication`, `resources_and_support`, `process_and_accountability` |

State the manager role when it clarifies why a record fits, especially in manager-facing outputs.

## Tie-breakers

When multiple records fit:

1. Prefer records that create a manager-team conversation or shared interpretation when the user needs action-taking guidance.
2. Prefer records that can become one small next step with a near-term check-in.
3. Prefer records that can fit into existing team meetings, 1:1s, stand-ups, business reviews, or project routines rather than requiring a separate process.
4. Prefer records aligned to what the team needs to accomplish in the next 3-6 months.
5. Prefer records with direct content guidance (`content_type` of `guide` or `mixed`) over resource-only records.
6. Prefer `quick_start` records when the user needs a short manager prompt or immediate team conversation.
7. Prefer records with `has_detailed_guidance` when the user asks for a complete action plan.
8. Prefer records without `has_unresolved_internal_references` when sharing links/resources.
9. Preserve catalog order as a secondary tie-breaker, not as proof of priority.

## Anti-selection rules

Do not choose a record just because it has more content, more links, or a more polished title. Choose based on fit to evidence and authorized question mapping.

Avoid:

- recommending many records at once
- choosing resource-only records when the manager needs behavior change
- choosing manager-only work when the issue requires shared team ownership
- choosing a psychological-safety framing for unrelated questions
- treating a systemic issue as if the manager alone can solve it
- using the presentation template to alter the selected action
- presenting unresolved internal references as usable resources

## Output behavior

- Recommend one best-fit focus area when evidence clearly points to it.
- Present 2-3 eligible candidates when evidence is insufficient to choose confidently.
- Include full `content_text_body` when the manager needs actionable guidance.
- Use `content_description` as valid guidance when `content_text_body` is empty.
- Present resources as titled links when possible; do not render unresolved internal references as working links.
- When producing manager-facing guidance, include an ACT conversation flow and a single next-step/check-in cadence when relevant.
- If explaining why action matters, cite the secondary evidence: belief that action will be taken relates to disengagement risk, and manager action planning is associated with score gains within a quarter.
- If explaining psychological safety specifically, cite the secondary evidence that lower psychological safety is associated with higher intent to quit and lower motivation, and that the video links psychological safety with lower turnover/stress and higher productivity.

## Presentation packaging behavior

When the user asks for slides or a deck:

1. Keep the selected action record(s) unchanged.
2. Use the tertiary presentation template only for story structure and visual packaging.
3. Recommended slide flow:
   - survey signal and why it matters
   - matched question and authorized action choice
   - selected focus area and manager role
   - ACT conversation guide
   - one next step and check-in cadence
   - optional supporting resources
4. Do not include all eligible records unless the user asks for a menu of options.

## Failure mode

If the question ID is missing or ambiguous, ask the user for the canonical question ID or show possible question-ID candidates for confirmation.
