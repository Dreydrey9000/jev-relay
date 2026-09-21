# Verification record

Test date: September 20–21, 2026. These are separate kinds of evidence.

## Router and guards

- 22 automated tests passed on macOS Python 3.12 and Linux Python 3.10.
- Tests cover provider policy, malformed responses, unavailable providers, cloud permission flags, input-secret tripwires, redirects, kill switches, low resources, monitored timeout and mid-flight termination.
- Mocked provider results verify routing behavior; they do not measure model intelligence.
- A clean Python 3.12 virtual environment installed the package using pip-compatible tooling. Running the installed module from outside the source checkout, without model configuration or credentials, returned the documented `local_disabled` review handoff.

## Live hosted checks

The installed command was exercised on macOS and the Jax Linux host using one public synthetic research-routing case each. Both returned valid `research` advice through Jev 1.13.0. Existing credentials were consumed in memory, not copied into this repository.

An earlier 24-case Jev pilot scored 22/24, with median observed round-trip latency 0.503 seconds. This small synthetic baseline used the direct helper before the Relay router. It is not production accuracy, a warm inference benchmark, or a comparison against every catalog entry.

## Integrations

Claude Code and Codex use the shared skill and CLI. Hermes/Jax has the same skill and a tested CLI on Linux. This is an explicit advisory tool, not interception of every agent decision. The Jax host has no local model configured and hands routine cases back to its calling agent without cloud spend. Existing quota and message-delivery systems retain their own routing.

## Ecosystem research

The catalog records 43 related repositories, including trained models, runtimes, wrappers and evaluation tools. They are not 43 equivalent or independently trained models. Source/license metadata review is labeled separately from executed inference. This is a dated research snapshot, not an exhaustive registry or legal license determination.

The Nimble public endpoint returned HTTP 503 during the pilot. Its serialization tests passed; that is not a successful model-quality test. An early jevmlx test process aborted under Python 3.14 before establishing usable inference. Larger local alternatives were not downloaded on the constrained test machine. See each catalog entry for its status.

## Local model evaluation

Pending the guarded Laya-MLX evaluation. Local outputs remain shadow advice requiring review, regardless of confidence. No claim of time savings, cost savings, or equivalence to hosted Jev is made.
