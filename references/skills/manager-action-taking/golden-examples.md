# Golden examples

These examples define expected selection behavior for representative question IDs. Use them as regression expectations when changing the taxonomy builder or Manager Action Taking skill.

| Question ID | Scenario | Expected behavior |
|---|---|---|
| `Q_JOB_RESOURCES` | Employees lack tools, support, or ways to remove blockers. | Prefer resources/support or team-conversation records such as "Ask for support" or "Develop a support network." Frame with ACT: acknowledge blockers, collaborate on one barrier, take one support step. |
| `Q_TEAM_INCLUSION` | Team members do not feel heard, included, or able to contribute. | Prefer inclusion and communication-pattern records such as "Be Inclusive by Changing Communication Patterns." Frame with ACT: acknowledge participation gaps, collaborate on one behavior, check whether participation improves. |
| `Q_MANAGER_SUPPORT` | Manager support is low or unclear. | Choose among support resources, communication bridge, or trust-building records based on evidence. Frame with ACT: clarify what support means and choose one visible support action. |
| `Q_LEADERSHIP_CONFIDENCE` | Employees lack confidence in senior leadership decisions. | Prefer communication bridge records that explain decisions and connect leadership context to team needs. Frame with ACT: gather team questions and take one communication step. |
| `Q_ACCEPTS_FEEDBACK_360` | Leader needs to improve openness to feedback. | Prefer visible listening, trust-building, or self-assessment records. Frame with ACT: acknowledge feedback and take one visible follow-up action. |
| `Q_ACCEPTANCE` | Belonging/acceptance concern. | Use the narrow matched candidate directly: "Build an Inclusive Environment." Frame with ACT: define what acceptance looks like and pick one practice to try. |
| `Q_GPS_VOICE` | People may not feel safe speaking up, asking questions, or admitting mistakes. | Prefer psychological-safety/trust-building records such as "Build psychological safety for your team" or "Build a High Trust Culture." Frame with ACT: acknowledge voice barriers, collaborate on what would make speaking up safer, and practice one manager behavior. |

Use the secondary evidence context to explain why the manager should act: employees' belief that action will be taken is strongly tied to disengagement risk, and manager action planning has been associated with score gains within a quarter.

## Secondary and tertiary context expectations

- Use `collaborative-action-taking-act.md` to add ACT framing, one-step action taking, shared ownership, and check-in cadence.
- Use `psychological-safety-techcommunity.md` for voice, trust, inclusion, acceptance, and feedback-safety scenarios.
- Use `tertiary/action-taking-presentation-template.md` only when the user asks for slides or a deck. It should package the recommendation, not change the selected action.

Golden examples include `secondary_context_to_use`, `why_action_matters`, and `presentation_packaging` fields so selection behavior and presentation behavior can be tested separately.
