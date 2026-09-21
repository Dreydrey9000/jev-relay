# Verification record

Validated September 21, 2026.

- Copied `jev_relay/` and `blueprints/` into an independent consumer directory outside synced folders.
- Ran the documented practice generator with Python 3. It validated all eight template question definitions against the actual Relay request schema and produced two synthetic requests plus the worksheet.
- Submitted both requests to the Relay CLI with `local_enabled: false`: each returned `status: review`, `provider: frontier`. No inference or paid provider call was made.
- Re-running the generator against the same output directory exited with code 2 and refused to overwrite existing exercises.
- Existing Relay unit suite: 22 tests passed. `git diff --check` passed.

These checks prove request compatibility, offline fallback and packaging behavior. They do not evaluate model accuracy, real source connectors, notifications, dashboard UI, coaching portal access or cost caps. Those remain unimplemented in this package.
