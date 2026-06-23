---
name: build-a-chatbot
description: Building a full-stack, Claude-powered Meta messaging bot (WhatsApp or Instagram) end-to-end — from a vague idea to a deployed webhook. Specializes the SDD pipeline with the chatbot-toolkit skills.
tags: [feature-dev, planning]
skills: [grill-me, to-prd, to-issues, bot-brain-basics, bot-brain-agent, meta-messaging, bot-session-state, scaffold-bot, testing-bots, bot-safety, deploy-bot, tdd, code-review, commit-conventions]
---

# Build a chatbot

The full path for a Claude-powered WhatsApp/Instagram bot. It's the standard
spec-driven pipeline (`feature-dev`) with the `chatbot-toolkit` skills slotted in
for the domain work. The bundled reference app at
`plugins/chatbot-toolkit/reference-app/` is the single source of truth — every
skill below adapts from it rather than reinventing.

```mermaid
flowchart TD
    A[Vague bot idea] --> B[grill-me<br/>resolve channel, brain, persistence decisions]
    B --> C[to-prd<br/>PRD → GitHub issue]
    C --> D[to-issues<br/>tracer-bullet vertical slices]
    D --> E[bot-brain-basics<br/>raw Anthropic SDK behind Brain.respond]
    E --> F[bot-brain-agent<br/>layer the Claude Agent SDK, same interface]
    F --> G[meta-messaging<br/>Meta App, webhook verify + X-Hub-Signature-256, Graph send]
    G --> H[bot-session-state<br/>Postgres-backed conversation history]
    H --> I[scaffold-bot<br/>assemble the FastAPI webhook + seams into a running app]
    I --> J[bot-safety<br/>guardrails: injection screening + PII redaction]
    J --> K[deploy-bot<br/>Dockerize → PaaS, or tunnel for dev]
    K --> L[code-review<br/>house gates]
    L --> M{blocking findings?}
    M -- yes --> I
    M -- no --> N[commit-conventions → merge]

    T[testing-bots<br/>offline tests throughout] -.-> E
    T -.-> G
    T -.-> H
    T -.-> I
```

## The path

| Step | Skill | What you get |
|------|-------|--------------|
| 1. Interview | `grill-me` | Channel, brain, and persistence decisions resolved — no code yet |
| 2. Spec | `to-prd` | A PRD as the contract, in the working repo's issues |
| 3. Slice | `to-issues` | Independently-grabbable tracer-bullet tickets |
| 4. Brain | `bot-brain-basics` | A `Brain.respond()` on the raw Anthropic Messages API |
| 5. Agent | `bot-brain-agent` | The Claude Agent SDK layered behind the same interface |
| 6. Channel | `meta-messaging` | Meta App setup, webhook verify + signature check, Graph send |
| 7. Sessions | `bot-session-state` | Durable per-conversation history in Postgres |
| 8. Assemble | `scaffold-bot` | The FastAPI webhook gluing the seams into a running app |
| 9. Safety | `bot-safety` | Prompt-injection screening + PII redaction |
| 10. Ship | `deploy-bot` | A public HTTPS webhook Meta accepts (PaaS or dev tunnel) |
| —. Test | `testing-bots` | Offline tests at every step (fixtures, mocked Graph + Anthropic) |
| —. Review | `code-review` | House quality gates before merge |
| —. Commit | `commit-conventions` | Clean history |

`testing-bots` isn't a phase — it runs *throughout*: every brain, channel, session,
and webhook change lands with an offline test (captured webhook fixtures, mocked
Graph and Anthropic) before review.

## Gates

- Plan and build are separate — accept the spec before any code.
- The brain interface is fixed early (`Brain.respond()`); `bot-brain-agent` swaps
  the implementation without changing callers.
- Forced verification — the reference-app test suite green *with evidence* before
  "done". Verify the deploy with the webhook handshake before pointing Meta at it.
- Loop review → assemble until `code-review` has no blocking findings.
