# Verification record

Validated September 21, 2026.

- Copied `jev_relay/` and `blueprints/` into an independent consumer directory outside synced folders.
- Ran the documented practice generator with Python 3. It validated all eight template question definitions against the actual Relay request schema and produced two synthetic requests plus the worksheet.
- Submitted both requests to the Relay CLI with `local_enabled: false`: each returned `status: review`, `provider: frontier`. No inference or paid provider call was made.
- Re-running the generator against the same output directory exited with code 2 and refused to overwrite existing exercises.
- Existing Relay unit suite: 22 tests passed. `git diff --check` passed.

These initial checks prove request compatibility, offline fallback and packaging behavior. They do not evaluate model accuracy or cost caps.

## Dashboard starter and owner install — September 21

- Eight Bun tests passed locally, in a separate consumer directory and on the DreyOS host. They cover reply direction, draft exclusion, duplicate imports, persistent labels, new-message reset, malformed imports, preserved data on sync failure and request-origin protection.
- Focused static UI gate passed. The existing Python CI suite now has 24 tests including the dashboard/VARK asset gate.
- Authenticated DreyOS Attention Desk loaded Gmail pages and a private Mac Messages snapshot. Public access to its API returned 401.
- Live label save and restore succeeded; synthetic Ignored persistence and empty search were verified in the browser.
- The new pane had no horizontal overflow at 320px/390px mobile and 1440px desktop widths; 200% zoom and reduced-motion settings were checked and restored.
- Narration played successfully: 110.832 seconds, no media error.

Live evidence is for the single-owner DreyOS installation. The distributed demo uses synthetic data and an in-memory database. No coaching portal publication, broad DreyOS regression-suite pass, background watcher, automatic notification, paid budget cap or local model-quality result is claimed.

## Queue-refresh fix — September 21

Reproduced a visible bug: saving Ignored persisted the label but left the message and count in the Needs attention view. The client now reloads the selected queue after a confirmed save and announces completion. Verified live that the count dropped from 798 to 797, the item left Needs attention, and it could be restored from Ignored. The original label was restored after testing. The diagram was verified rendering on GitHub and moved above the introductory status text, alongside a direct link to the installed dashboard.
