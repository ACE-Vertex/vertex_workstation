export interface ArchitectureContractItem {
  readonly id: string;
  readonly index: string;
  readonly title: string;
  readonly summary: string;
  readonly status: "ACTIVE" | "DRAFT";
  readonly principles: readonly string[];
  readonly rules: readonly string[];
  readonly notes: readonly string[];
}

export const ARCHITECTURE_CONTRACTS: readonly ArchitectureContractItem[] = [
  {
    id: "folder-architecture",
    index: "01",
    title: "Folder Architecture",
    summary: "Feature-first structure. Domain intent must be visible before framework detail.",
    status: "ACTIVE",
    principles: [
      "Top-level structure should communicate what Vertex Workstation does.",
      "Files that change together should live close together.",
      "Feature folders may not become hidden dependency containers.",
    ],
    rules: [
      "src/features/forge owns FORGE presentation and feature-local logic.",
      "src/features/ray owns RAY presentation and feature-local logic.",
      "src/features/contracts owns Architecture Contract presentation.",
      "Shared contracts belong outside feature folders when multiple features depend on them.",
      "Avoid generic dumping grounds such as misc, helpers, or common without a clear responsibility.",
    ],
    notes: [
      "Feature-first is preferred over type-only folders.",
      "Framework names should not dominate domain structure.",
    ],
  },
  {
    id: "component-ownership",
    index: "02",
    title: "Component Ownership",
    summary: "One component, one owner, one stable identity.",
    status: "ACTIVE",
    principles: [
      "Visual placement must not define logical ownership.",
      "Replacing a component means retiring the previous implementation.",
    ],
    rules: [
      "1 Component = 1 Owner = 1 ID.",
      "No duplicate production owners for the same responsibility.",
      "Retired components must not survive as active source, selector, or event owners.",
      "History belongs in Git, backup, Evidence, or migration archives.",
    ],
    notes: [
      "A presentation surface may move without transferring core ownership.",
    ],
  },
  {
    id: "layout-ownership",
    index: "03",
    title: "Layout Ownership",
    summary: "Geometry and presentation layering must have explicit owners.",
    status: "ACTIVE",
    principles: [
      "Layout is architecture, not decoration.",
      "Processing effects may decorate layout but must not own geometry.",
    ],
    rules: [
      "1 Layout Layer = 1 Geometry Owner.",
      "Background effects must use pointer-events: none.",
      "Persistent tools use dock, grid, or split; no default floating windows.",
      "Conditional UI must not steal the primary workspace track.",
    ],
    notes: [
      "RAY lane ownership is isolated in its layout contract.",
      "CSS stacking context is treated as an architectural concern.",
    ],
  },
  {
    id: "feature-boundary",
    index: "04",
    title: "Feature Boundary",
    summary: "FORGE and RAY may cooperate without directly owning each other.",
    status: "ACTIVE",
    principles: [
      "Feature collaboration must not create hidden bidirectional dependency.",
      "Shared behavior should cross an explicit contract or service boundary.",
    ],
    rules: [
      "FORGE must not directly own RAY internals.",
      "RAY must not directly own FORGE internals.",
      "Cross-feature data must use explicit shared models, services, or contracts.",
      "UI adjacency is never proof of dependency ownership.",
    ],
    notes: [
      "This protects Workstation from the hidden coupling that accumulated in the old Works prototype.",
    ],
  },
  {
    id: "verification-ownership",
    index: "05",
    title: "Verification Ownership",
    summary: "Verifier contracts must evolve with implementation ownership.",
    status: "ACTIVE",
    principles: [
      "Verification must inspect the actual owner of the capability.",
      "Historical invariants may be retired when the implementation intentionally advances.",
    ],
    rules: [
      "Verifier scope must include the files that actually own the feature.",
      "Do not preserve obsolete assertions after a feature becomes real.",
      "Static GREEN is not runtime visual acceptance.",
      "Evidence must identify whether failure belongs to implementation or verification.",
    ],
    notes: [
      "Verifier code is part of architecture, not an afterthought.",
    ],
  },
  {
    id: "runtime-safety",
    index: "06",
    title: "Runtime Safety",
    summary: "Mutating workflows advance only after explicit gates.",
    status: "ACTIVE",
    principles: [
      "Read, inspect, stage, apply, verify, and rollback are separate responsibilities.",
      "Target mutation must never occur during read-side inspection or Stage.",
    ],
    rules: [
      "HUMAN_APPLY remains an explicit authority gate.",
      "Immutable build and staging identities are mandatory.",
      "Stage must verify payload hashes before any target mutation.",
      "Rollback material must exist before destructive apply behavior is armed.",
    ],
    notes: [
      "FORGE is intentionally advanced one gate at a time.",
    ],
  },
  {
    id: "vertex-relay",
    index: "07",
    title: "Vertex Relay",
    summary: "Human and Vera exchange structured intent through a shared Workstation relay contract.",
    status: "ACTIVE",
    principles: [
      "Conversation-born concepts must be transferable into formal Vertex assets.",
      "Relay transport and domain payload must remain separable.",
      "Human acceptance remains the final gate for imported drafts and amendments.",
    ],
    rules: [
      "Vertex Relay envelope uses schema vertex-relay/1.",
      "CANONICAL and ARCHITECTURE_CONTRACT share the same relay envelope.",
      "Clipboard remains the fallback transport; DIRECT sends vertex-relay/1 to a configured Relay Bridge endpoint.",
      "Hyper Agent / Vertex Core may own the Relay Bridge that forwards payloads to Vera.",
      "RECEIVE must never auto-apply a draft without Human ACCEPT.",
      "Relay UI remains docked inside the owning page; no floating relay windows.",
    ],
    notes: [
      "Vertex Relay = HumanとVeraの意思を正式なVertex資産へ変換する共通路。",
    ],
  },
{
  id: "adapter-boundary",
  index: "08",
  title: "Adapter Boundary",
  summary: "External service gates belong in replaceable adapters, never in Vertex Core ownership.",
  status: "ACTIVE",
  principles: [
    "Core completion must not depend on one provider accepting a connection.",
    "External service policy, credentials, and product gates are adapter concerns.",
    "A blocked provider must be replaceable without rewriting Relay, Brain, or Workstation ownership.",
  ],
  rules: [
    "Vertex Adapter Port is the single provider-facing boundary for Relay transport selection.",
    "Adapter IDs are stable and registry-owned; duplicate adapter ownership is rejected.",
    "Unavailable adapters must expose EXTERNAL_GATE or UNCONFIGURED instead of pretending to be connected.",
    "Presentation must ask Adapter Port for route truth; provider gate semantics must not be reimplemented in UI code.",
    "No provider credential may be embedded in source, manifest, Relay payload, localStorage, or logs.",
    "OpenAI API credentials are read only by the Tauri/Rust backend from the user-owned OPENAI_API_KEY environment and raw credential values never cross into Presentation.",
    "OPENAI_API route readiness is evaluated by Adapter Port from backend runtime status; Presentation may display the result but must not own the provider rule.",
    "Provider responses remain review-only until a Human explicitly promotes them into a Vertex Relay DRAFT / AMEND flow.",
    "ChatGPT MCP, OpenAI API, Local LLM, and Hyper Agent remain separate adapters behind the same port.",
    "Human Gate remains authoritative for imported DRAFT / AMEND mutations.",
  ],
  notes: [
    "門番はCoreの停止理由ではなく、Adapter交換理由として扱う。",
    "Current real outbound implementations are Vertex Relay HTTP and OpenAI API; ChatGPT MCP remains an EXTERNAL_GATE until the external product connection is available.",
  ],
},
];
