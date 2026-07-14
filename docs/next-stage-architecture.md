# Next-stage architecture

## Purpose

This document turns the repository review into a sequenced architecture backlog.
It intentionally excludes local reliability and maintenance fixes that can ship
without changing system boundaries.

The current system is a single-process aiogram polling bot. Handlers call a
process-global Airtable adapter, which runs the synchronous pyairtable client in
a one-worker thread pool and caches full-table reads in process memory.

The next stage should improve trust boundaries and failure isolation before
adding features or scaling traffic. It should be delivered as small,
rollback-safe slices rather than a rewrite.

## P0: Stop exporting Telegram credentials through attachment URLs

### Evidence and failure mode

- `common.tg.create_sensitive_url_from_file_id` creates a Telegram file URL that
  contains the bot token.
- `handlers.kek.kek_add` passes that URL to the storage layer.
- `airtable.kek_storage.KekStorage._create_row` sends it to Airtable as an
  attachment URL.

The credential-bearing URL therefore leaves the bot process. Even if Airtable
immediately imports the file and later returns its own URL, the Telegram token
has crossed a third-party boundary and may be retained in request history,
provider logs, or audit records.

### Target decision

Keep Telegram `file_id` as the delivery identifier. If durable media ownership
is required, ingest bytes server-side into storage we control, or use an
attachment-upload mechanism that does not disclose the Telegram URL. Airtable
must never receive a URL containing a bot token.

### Migration slices

1. Inventory attachment records and establish whether Airtable retained source
   URLs anywhere accessible.
2. Add explicit media metadata: Telegram `file_id`, file type, filename, and an
   owned durable-object identifier when applicable.
3. Dual-read the old and new representations while backfilling existing media.
4. Stop writing Telegram URLs, verify all attachment paths, then rotate the bot
   token.

### Done when

- No outbound request or persisted field contains the Telegram bot token.
- Existing media still sends successfully after token rotation.
- Tests assert token absence at the storage boundary.

## P1: Establish an application boundary and owned lifecycle

### Evidence and failure mode

- `app/__main__.py` relies on top-level imports that only work when the `app`
  directory is on `sys.path`.
- `settings.config` and `airtable.kek_storage.kek_storage` are created during
  import.
- Tests use both `app.*` and top-level module paths, allowing the same source
  file and singleton to be loaded under different module names.
- Executor and client shutdown are not owned by application startup/shutdown.

This couples packaging, working directory, network-client construction, and
handler registration. It makes graceful shutdown, isolated tests, alternate
storage adapters, and deployment entry points harder than necessary.

### Target decision

Adopt one import namespace and a composition root:

```text
Telegram transport -> application use cases -> domain models
                                      |
                                      v
                              repository contract
                                      |
                                      v
                               Airtable adapter
```

An application factory should receive validated settings, construct the bot,
repository, caches, and dispatcher, and close owned resources in a `finally`
block or lifespan context. Handlers should depend on injected use cases or a
repository protocol, not module-level clients.

### Migration slices

1. Make the package runnable through one canonical module entry point.
2. Introduce repository protocols around the current Airtable behavior.
3. Move client and executor creation into the composition root.
4. Inject fakes in tests and remove mixed import paths.
5. Add explicit graceful shutdown for polling, bot sessions, caches, and
   executors.

### Done when

- Importing a module performs no network-client construction.
- The app starts from any working directory through one documented command.
- Unit tests replace repositories without patching module globals.
- `SIGTERM` stops polling and closes every owned resource within a bounded time.

## P1: Put a typed domain model at the Airtable boundary

### Evidence and failure mode

Handlers directly index provider dictionaries such as `record["fields"]` and
assume field names, types, attachment shapes, and relationships. Airtable is
also editable by humans, so malformed or partially migrated rows can turn into
runtime handler failures. Display names have historically been used as
identities in statistics even though they are not unique.

### Target decision

The Airtable adapter should translate provider records into typed domain
objects. At minimum, define `Kek`, `Attachment`, `User`, and statistics models
with stable identities, constrained attachment types, content limits, and an
explicit schema version. Provider dictionaries must not escape the adapter.

Choose and document a malformed-record policy: skip and report, quarantine, or
fail the refresh while serving the last known-good snapshot.

### Migration slices

1. Capture representative Airtable fixtures, including missing and malformed
   fields.
2. Add parsing and serialization contract tests.
3. Return domain models from reads while keeping writes compatible.
4. Move presentation and statistics logic off provider field names.
5. Add a versioned migration path for future Airtable schema changes.

### Done when

- No handler reads an Airtable field dictionary.
- Invalid records produce a metric and deterministic policy outcome.
- Identity and ranking use record IDs or Telegram IDs, never display names.
- Schema changes are tested before deployment.

## P1: Replace request-time full-table I/O with a resilient read model

### Evidence and failure mode

- `KekStorage.all` and `all_users` fetch complete Airtable tables.
- A single worker serializes every Airtable operation.
- The executor timeout returns while the underlying thread can continue
  running; subsequent work can queue behind that call.
- Five-minute in-process caches have no explicit write invalidation and are not
  shared between replicas.
- Search is a linear scan over the full result set.

This is acceptable only while the dataset and traffic remain small and Airtable
is healthy. Under latency or rate limiting, unrelated users experience
head-of-line blocking, timed-out work can accumulate, and recent writes may not
be visible.

### Target decision

Build an explicit read snapshot with:

- one controlled refresh path with single-flight behavior;
- a bounded queue and end-to-end timeout budget;
- stale-while-revalidate behavior during provider incidents;
- write-through or explicit invalidation after mutations;
- a precomputed random-access collection and normalized search index;
- metrics for refresh age, provider latency, failures, queue depth, and stale
  responses.

Keep Airtable initially. Reconsider the source of truth only after measuring
dataset size, write frequency, rate-limit pressure, and recovery objectives.

### Done when

- Handler latency is not directly coupled to a cold full-table request.
- Provider failure serves a bounded-age snapshot with a clear user response.
- Work queues and retry budgets are bounded.
- Successful writes become visible according to a documented consistency SLO.
- Load and outage tests cover slow, failed, and rate-limited provider calls.

## P1: Define observability, privacy, and real health semantics

### Evidence and failure mode

- Update logs include message text, names, usernames, IDs, language, and chat
  metadata.
- The custom logger defaults to `DEBUG` in every environment.
- Failed handlers bypass the normal completion/timing log.
- `events_chat_id` and `health_check_url` settings are present but unused.
- Container health currently proves process identity, not polling progress or
  storage readiness.

The current logs are useful for debugging but lack an explicit data-retention
and redaction policy. A live process can be operationally stuck while still
passing a process check.

### Target decision

Use structured event logs with update ID, route, outcome, duration, and a
correlation ID. Do not log message content or direct identifiers by default;
make narrowly scoped diagnostic logging explicit and time-bounded. Add metrics
and error reporting around handler failures, polling progress, storage refresh,
cache age, and outbound API latency.

Define separately:

- **liveness**: the event loop and polling task are running;
- **readiness**: configuration is valid and an acceptable storage snapshot is
  available;
- **heartbeat**: the deployed instance is making polling progress.

### Done when

- Production log level and redaction are configuration-driven.
- A privacy review defines fields, retention, and operator access.
- Exceptions retain correlation and duration without exposing message bodies.
- Alerts distinguish process death, polling stalls, and Airtable degradation.

## P2: Centralize authorization and audit privileged actions

### Evidence and failure mode

Telegram user and chat IDs are embedded in settings defaults. `/kek_push` uses
one hard-coded maintainer identity while other admin behavior uses a separate
set. Privileged mutations have no durable audit event.

### Target decision

Introduce a small authorization policy with named roles and environment-owned
configuration. Keep authorization separate from routing filters so it can be
unit-tested and audited. Record who performed each privileged mutation, the
target record, the outcome, and a correlation ID without copying message
content into logs.

### Done when

- No personal user IDs are committed as authorization policy.
- Every privileged command has an explicit role requirement.
- Denied and successful mutations are test-covered and auditable.

## P2: Make content rendering an explicit trust boundary

### Evidence and failure mode

Suggested messages are stored as Telegram HTML and replayed under a global HTML
parse mode. Airtable editors can also modify this content. Attachment dispatch
accepts string values from provider data and has no explicit unknown-type
policy.

### Target decision

Define a content model that separates plain text, supported formatting, and
attachment metadata. Normalize and validate content on ingestion, escape at the
output boundary, enforce Telegram size limits, and reject or quarantine unknown
attachment types. Document whether Airtable editors are trusted content
authors.

### Done when

- Rendering tests cover malformed tags, links, oversized content, and unknown
  media types.
- Stored representation is independent from Telegram-specific HTML where
  practical.
- Untrusted content cannot alter rendering outside the supported policy.

## P2: Harden delivery and supply-chain controls

The maintenance baseline builds the container in CI, uses a locked dependency
sync, continuously audits Python dependencies, and runs as a non-root user. The
next stage should pin build inputs by digest, scan the image, publish an
immutable image, and deploy that exact artifact with a rollback path. Define
whether polling permits only one active replica; if horizontal availability is
required, choose leader election or move to a webhook architecture before
adding replicas.

### Done when

- CI emits an immutable, scanned image and deployment consumes that digest.
- A smoke test verifies startup and readiness before promotion.
- Rollback is documented and rehearsed.
- The single-writer/single-poller constraint is explicit and enforced.

## Recommended sequence

1. **Credential containment:** settle media ownership, stop token-bearing URL
   writes, migrate records, and rotate the token.
2. **Seams without behavior change:** canonical package entry point, composition
   root, repository protocols, typed records, and contract fixtures.
3. **Resilience:** snapshot refresh, bounded concurrency, invalidation, stale
   behavior, and provider outage tests.
4. **Operations:** structured/redacted telemetry, real health semantics,
   immutable image delivery, smoke test, and rollback.
5. **Policy and scale:** centralized authorization, content trust policy, then
   decide Airtable retention and polling versus webhooks from measured data.

## Decisions required before implementation

- Is Airtable the long-term source of truth or an editorial interface over
  owned storage?
- Must media survive Telegram token rotation and provider outages?
- What freshness, availability, and recovery objectives does the bot need?
- What user and message data may be logged, where, and for how long?
- Is one polling replica acceptable, or is multi-instance availability a goal?
- Which Airtable edits are trusted, and what moderation/audit trail is needed?

Each decision should become a short ADR before the corresponding migration
starts. None of these decisions blocks the credential-containment work.
