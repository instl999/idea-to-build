# MCP Integration Guide

> Reviewed synthetic fixture decision constrained by frozen core hash `409bf7fe207f8da0d0e50eff1f0c2ff16b1eb70720b89cfdabd2e742281e7b73`.

## Evidence labels

- **User-confirmed fact:** The MVP is a local-only single-user application with no external integrations.
- **User-confirmed fact:** Inputs are user-pasted text or a selected local file; processing must make zero network requests.
- **Immutable constraint:** No accounts, autonomous actions, cloud sync, or runtime network dependency.
- **AI recommendation:** `MCP_NOT_APPLICABLE`.

## Recommendation and evidence

- **AI recommendation:** Do not add an MCP server to this MVP.
- **Rationale:** No AI/agent client needs runtime access to an external tool or resource, the integration boundary is explicitly none, and a server would conflict with the local-only constraint.
- **Rejected alternatives:** Existing and custom MCP servers add no requirement coverage for the accepted workflow.
- **Evidence status:** Based only on this synthetic frozen fixture; not a current market or server-availability claim.

## Applicability

- The confirmed primary workflow runs entirely inside the local application.
- The accepted output is a reviewed Markdown brief, not a capability exposed to an agent host.
- Reassess only through change control if a future confirmed workflow adds an MCP-capable agent client and an external capability.

## Capability mapping

- **Reversible default:** Keep parsing, review, persistence, and export as ordinary application modules.
- No MCP tools, resources, or prompts are required.

## Host and transport

- No MCP host or transport is selected.
- No installation or host-configuration steps apply.

## Authentication and data boundaries

- The MVP retains the operating-system file-permission boundary and makes no network calls.
- No MCP credential, token, remote log, or server retention path is introduced.
- Meeting notes and generated briefs remain untrusted local content and must not become executable instructions.

## Verification

- Assert zero network requests in the end-to-end acceptance path.
- Verify import, extraction, review, export, deletion, and offline operation with synthetic notes.
- Add a regression test that no MCP process, configuration, or dependency is started or required.

## Fallback and removal

- The fallback is the accepted local application workflow; no server is needed.
- If an experimental server is later proposed, keep it disabled by default and route the architecture change through `docs/live/CHANGE_REQUESTS.md` and a human-reviewed new core baseline.
