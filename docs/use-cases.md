# Where to try Jev Relay

Use bounded choices with explicit options and an abstain/review option. Begin with public or synthetic data and compare against a reviewed answer set.

| Task | Example options | Review requirement |
| --- | --- | --- |
| Skill shortlist | research / writing / coding / unknown | Caller chooses the skill and checks access |
| Public research relevance | relevant / adjacent / irrelevant / unsure | Read the actual source before relying on it |
| Task triage | ready / missing input / blocked / unclear | Keep scheduling and commitments with the caller |
| Evidence checks | supported / contradicted / insufficient | Include source evidence; model confidence is not a citation |
| Draft organization | how-to / announcement / comparison / other | Author approves final copy |
| Documentation cleanup | duplicate / related / unique / unsure | No automatic deletion |
| Test failure grouping | setup / assertion / timeout / unknown | Engineer reproduces and diagnoses the failure |
| Meeting-note sorting | decision / question / action candidate / other | No automated messages or assignments |
| Public FAQ routing | setup / billing information / usage / unknown | No payment or access changes |
| Release-note triage | user-visible / internal / unclear | Author verifies the actual shipped behavior |

Avoid using a model for deterministic arithmetic, credentials, authorization, money movement, hiring eligibility or irreversible action. Never send private notes or source to hosted Jev merely because a local call failed.

For each proposed workflow, collect a small held-out labeled set, include ambiguous and adversarial inputs, measure mistakes and abstentions, and compare total latency with doing the task directly. Keep the model in shadow mode until its practical value is demonstrated for that specific workflow.
