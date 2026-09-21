# DreyOS Attention Desk dashboard

Implementation contract, not an installed dashboard. Fit the existing DreyOS Bun/SQLite engine and lightweight UI; avoid creating another agent framework or standalone hosted inbox.

## Dashboard layout

```text
DreyOS / Attention Desk          [Preview digest] [Settings]
Connections: email unconnected · texts unconnected
Local model: unavailable · automatic alerts: off · hosted: disabled

Needs attention | Waiting on someone | Review | All processed
------------------------------------------------------------
Message title                      Received / due
Why it matters · short source evidence
Source account · actual provider · reviewed/unreviewed
[Open original] [Correct category] [Snooze] [Resolve]
------------------------------------------------------------
Templates     Processing health     Delivery history
```

Start with meaningful empty states: “Connect a source to begin” and “Local inference unavailable; review items directly.” Counts come from stored records; do not display fabricated savings, decisions or activity. Keep a clearly labelled synthetic practice mode separate from personal data.

Use the DreyOS bone/charcoal/gold theme, existing navigation and shared UI standard. At mobile widths use cards without horizontal scrolling. Provide labelled controls, keyboard focus, readable contrast, reduced motion, loading/error/empty/disabled states and 200% zoom support. Connection and inference failures remain visible. Add a once-after-login product update only when the feature actually ships.

Follow the shared signature UI defaults when implementing: branded liquid-metal controls through a reusable semantic wrapper, thinking-orb status only during real pending operations, static/reduced-motion fallbacks, and existing accessible account surfaces. No fake activity or timer-based success.

## Proposed API and storage

The following routes do not exist yet. Mount through the existing engine's authenticated router and reuse its profile context and approval mechanisms.

| Proposed route | Purpose |
| --- | --- |
| GET /api/attention/status | Connection freshness, actual model readiness, mode, errors and cost policy |
| GET /api/attention/items?cursor=... | Bounded, profile-scoped pagination and category filters |
| PATCH /api/attention/items/:id | Validated reviewed category, snooze or resolution; audit old/new state |
| POST /api/attention/digest/preview | Assemble a digest without sending |
| POST /api/attention/digest/send | Existing approval flow, chosen owner destination, idempotency key |
| GET /api/attention/templates | Versioned definitions with compatibility and installation status |

Store connectors/cursors, message metadata, minimal evidence, classification attempts, reviewed decisions, waiting commitments and delivery ledger in profile-owned storage. Keep credentials in the existing secure credential mechanism. Don't add tokens to browser state or export bundles. Host-level authentication does not replace item/profile authorization.

Reuse DreyOS's existing settings and action approval paths rather than introducing a parallel permission system. Verify current production source and active checkout before implementation; do not edit the running runtime as the source of truth.

## Template card

Show purpose, supported sources, required model/runtime, data leaving the device, paid features, tested version, limitations and a practice button. Installation first creates disabled settings; the owner connects their own account and chooses any notification destination. Never inherit Drey's identities or notification targets.

## Implementation checks

Add repo UI/UX checks and scoped server tests for profile isolation, mutation validation and duplicate delivery. Verify desktop/mobile authenticated journeys. Keep local preview, source commit, production deployment and coaching publication as distinct release states.
