# Attention Desk dashboard starter

Run a synthetic, local-only version with Bun 1.4.0 (the verified runtime):

```sh
cd blueprints/attention-desk/dashboard
bun test engine/attention.test.ts
node attention-ui-check.mjs
bun run preview.ts
```

Open http://127.0.0.1:5779. Choose Refresh email to load the synthetic workshop message, mark it Important and save, then try Ignored and its filter. Reload to verify the label is retained for this running practice session. Stopping the server clears its in-memory practice database.

This preview **never connects to a real account**. It has no login because all data is synthetic and its server binds only to loopback. Do not expose it publicly or replace its fixtures with private data. For a real installation, mount `attentionRoutes` behind your application's existing authenticated, single-owner boundary and provide its read-only Gmail adapter. The standalone practice server is not the production server.

## Real DreyOS integration

The owner installation mounts `/attention` as a DreyOS tab and `/api/attention/*` after its existing login/origin gates. It uses a separate private SQLite file. Gmail connection credentials stay in the existing adapter; no model is invoked. Only thread metadata/snippets are read. The query excludes spam/trash but includes read and archived conversations; Load older email follows Gmail pagination, 30 threads per page.

An incoming latest message is a **possible unanswered conversation**, not a proven obligation. Replies in other threads, alternate accounts, phone calls, newsletters and group chats need human review. Drafts are not treated as sent replies. Each new message version resets its label to Needs review. Saving an old version fails rather than labelling a newer message unseen.

Important stays in the attention queue. Not important and Ignored are separate reversible filters. All imported includes outgoing latest messages too. Labels do not change the original inbox. Lists paginate at 50 records; this starter displays at most 5,000 stored conversations and discloses that cap. Search applies to the current page.

## Optional Mac text snapshot

`export-texts.py --output /private/new-snapshot.json` reads the macOS Messages database in read-only mode when the operating system already permits access. It exports the latest available non-reaction message for up to 1,000 conversations. Unavailable text and missing source links are explicitly labelled. Do not bypass OS permissions or grant broader access through an automated script.

The snapshot contains private message data: keep it outside Git, mode 0600, and import it only into your own authenticated instance through `createAttention(...).importTexts(payload)`. Delete temporary exports according to your own retention policy after import. This is a dated snapshot, not a background text watcher. It does not guarantee all iCloud messages are available locally.

## VARK learning options

- **Visual:** [rendered flow diagram](../../../docs/diagrams/attention-desk.svg) and [editable Mermaid](../../../docs/diagrams/attention-desk.mmd).
- **Aural:** [111-second narrated walkthrough](engine/public/attention-walkthrough.mp3), also playable inside the dashboard.
- **Read/write:** [exact narration transcript](../walkthrough-transcript.txt), [blueprint](../BLUEPRINT.md) and [coaching worksheet](../COACHING.md).
- **Kinesthetic:** Start practice inside the dashboard, or run the two offline JSON exercises in the parent README.

These are alternative ways to access the same material, not a claim about the effectiveness of fixed learning styles. No video is required to understand these controls; the narrated guide and interactive practice cover the sequence.

## Limits

No automatic monitoring, notifications, paid checks or AI classification. No hosted multi-user isolation layer is included; use separate owner installations. Source snapshots retain minimal excerpts but this starter has no automatic retention cleanup. Follow the blueprint's retention requirements before expanding collection.

Public API references: [Gmail threads.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads/list) and [threads.get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.threads/get).
