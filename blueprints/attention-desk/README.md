# Attention Desk

**Your messages, reduced to the decisions that need you.** A Jev Relay blueprint for DreyOS and an independently reusable coaching exercise.

Status: blueprint plus working offline request generator. This package does not connect to an inbox, monitor texts, send notifications, or install a DreyOS dashboard. Local model quality remains unverified. No paid AI account is required for the exercise; no savings or accuracy is promised.

## Start here

1. Read [the blueprint](BLUEPRINT.md) and [DreyOS dashboard contract](DREYOS.md).
2. Copy `templates.json`; change the labels and rules to fit your work.
3. Run the synthetic exercise from the repository root using Python 3.10+:

```sh
python3 blueprints/attention-desk/practice.py --output /tmp/attention-desk-practice
python3 -m jev_relay.cli --input /tmp/attention-desk-practice/inbox-request.json --config blueprints/attention-desk/offline.json
```

The first command writes two validated Relay requests and a practice worksheet. It makes no network requests and runs no model. The second explicitly disables local inference and returns a review handoff, with no paid fallback. Read the worksheet and make your own decisions; do not mistake request validation for model evaluation. Once you have a verified model and passing resource safeguards, omit `--config blueprints/attention-desk/offline.json` to try your own Relay configuration.

4. Use [the coaching lesson](COACHING.md) to teach the exercise. The portal receives this lesson and the template files, never a copy of your personal DreyOS database.
5. Before real inbox use, implement and verify the connector, profile isolation, source links, evaluation and delivery gates in the blueprint.

Files are MIT licensed under the repository license. Model licenses and hardware requirements are separate. There are no bundled credentials, model weights, private messages or subscriptions.

## What is reusable today

- Eight editable workflow definitions; the first two have synthetic practice inputs.
- A working generator that validates the two requests against Relay's own schema.
- A dashboard specification, architecture diagram, rollout checklist and teaching script.
- A manual scoring worksheet. Live classification, dashboard integration and notification delivery are still implementation work.
