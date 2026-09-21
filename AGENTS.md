# Jev Relay contribution rules

- Keep routine decisions local or return them to the caller; never add a silent paid fallback.
- Do not commit credentials, private messages, database files, model weights or owner-specific configuration.
- Keep the README-linked diagrams in `docs/diagrams/` accurate when changing an architecture or workflow. Label planned versus implemented paths.
- Coaching resources cover VARK: a diagram, playable narration plus exact transcript, written instructions/worksheet and a runnable synthetic exercise. Verify each format rather than claiming a video or model test that did not run.
- Run `python3 -m unittest discover -s tests -v` for the core and asset gate. For dashboard changes, also run `bun test blueprints/attention-desk/dashboard/engine/attention.test.ts` and `node blueprints/attention-desk/dashboard/attention-ui-check.mjs`, then review the changed browser journey at desktop and mobile widths.
- The public dashboard preview is synthetic and loopback-only. Real message routes belong behind an existing authenticated owner boundary. Do not turn the preview into an unauthenticated inbox server.
