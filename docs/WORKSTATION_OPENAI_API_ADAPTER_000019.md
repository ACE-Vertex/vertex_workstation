# Vertex Workstation — OpenAI API Adapter Foundation 000019

## Mission

Keep `CHATGPT_MCP` truthfully frozen at `EXTERNAL_GATE` and activate the
separate `OPENAI_API` adapter behind the existing Vertex Adapter Port.

This is an API-side model route. It does **not** claim to inject into the
current ChatGPT web conversation.

## Architecture

`Vertex Relay Bar`
→ `Vertex Adapter Port`
→ `OPENAI_API`
→ Tauri invoke
→ Rust backend
→ OpenAI Responses API
→ docked provider response
→ Human review

## Credential boundary

The raw API key is never accepted by React and is never stored in:

- source
- VRA manifest
- Relay payload
- localStorage
- UI state
- Evidence output

The Rust backend reads the user-owned `OPENAI_API_KEY` environment variable.
The optional `OPENAI_MODEL` environment variable selects the model.
When absent, the adapter defaults to `gpt-5.6`.

The frontend receives only:

- available
- configured
- model
- credential source label
- endpoint label

It never receives the secret value.

## Route truth

`OPENAI_API` means the adapter implementation exists.

Actual sendability still belongs to Adapter Port:

- Tauri unavailable → `UNCONFIGURED`
- API credential absent → `LINK_REQUIRED`
- backend + credential available → `READY`

Presentation displays that result but does not own the provider rule.

## Response boundary

A successful Responses API call is rendered in a docked
`OPENAI RESPONSE · HUMAN REVIEW` panel.

The response is **not** automatically applied to Canonical Registry or
Architecture Contract.

This preserves the Human Gate and leaves reverse `DRAFT / AMEND` promotion
for a later explicit pass.

## Processing

Every provider send displays a visible animated `PROCESSING` indicator.
Reduced-motion preference disables the animation without removing the state.

## External gate

`CHATGPT_MCP` remains unchanged as `EXTERNAL_GATE`.

000019 is intentionally the replaceable-adapter path:

**External service gate != Core failure.**
**External service gate = Adapter exchange reason.**
