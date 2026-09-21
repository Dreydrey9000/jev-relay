# Coaching portal lesson: Build your Attention Desk

**Outcome:** learn to turn messages into a reviewable attention queue without requiring a paid AI API.

**Current level:** blueprint and offline practice. Email/text connectors, DreyOS dashboard and automatic alerts are not bundled. Local inference requires compatible hardware, a fully installed supported model and passing safeguards.

## Portal resource card

- Title: Attention Desk — Your Inbox, Sorted
- Subtitle: A local-first blueprint for noticing important messages and tracking follow-ups.
- Includes: architecture, DreyOS dashboard specification, eight editable templates, two synthetic exercises, review worksheet and rollout checklist.
- Prerequisites: Python 3.10+ for practice; model/runtime requirements are separate.
- Price: open-source templates; no required paid AI API for practice. Hardware, service access and optional providers may cost money.
- Resource path in the Jev Relay repository: `blueprints/attention-desk/README.md`.
- Distribution: share this package or a reviewed repository revision. Never upload a personal database, real inbox export, model checkpoint or credentials.

## Teach it in 25 minutes

1. **5 minutes — identify the interruption.** Which messages deserved your attention yesterday? Which ones only felt urgent? Write your own sorting rules.
2. **5 minutes — follow one message.** Walk through the blueprint diagram. Explain that a proposed label cannot grant permission to send, delete or spend.
3. **10 minutes — run the practice.** Follow README commands. Independently label each synthetic message, then optionally compare local advice. Review any disagreement and the real provider/failure reason. A review fallback is an expected result without a working model.
4. **5 minutes — choose one first workflow.** Start with Attention Inbox or Waiting on Someone. Define a useful digest, choose acceptable evaluation criteria and leave automatic delivery disabled.

## Student worksheet

- The interruption I want to reduce:
- What counts as important, and what evidence proves it:
- What should always go to review:
- Which source/account belongs to this installation:
- What stays local and whether any sanitized cloud use is enabled:
- Notification destination, time zone, quiet hours and cadence:
- How I will catch missed important messages:
- What would make me pause or disable the workflow:

## Completion evidence

Submit only synthetic or deliberately redacted examples: your rules, practice results, a proposed digest and the limitations you found. Never ask students to post private conversations or keys in the group. Passing the exercise proves understanding and request compatibility; it does not prove the model is accurate or that a connector is live.

## Instructor publication checklist

Confirm the intended portal/course, publish the lesson and a versioned download there, test access as an enrolled member and verify every download/link. Mark the lesson “Blueprint + practice” until working integrations are released. The portal is a teaching/distribution surface, not a collector of students' inbox data.
