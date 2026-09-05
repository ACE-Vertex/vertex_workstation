import type { VertexRelayEnvelope } from "../relay/types";

export type VertexAdapterId =
  | "VERTEX_RELAY_HTTP"
  | "CHATGPT_MCP"
  | "OPENAI_API"
  | "LOCAL_LLM"
  | "HYPER_AGENT";

export type VertexAdapterState =
  | "READY"
  | "LINK_REQUIRED"
  | "EXTERNAL_GATE"
  | "UNCONFIGURED";

export type VertexAdapterCapability =
  | "SEND_RELAY"
  | "RECEIVE_RELAY"
  | "MCP_READ"
  | "MCP_WRITE";

export interface VertexAdapterDescriptor {
  readonly id: VertexAdapterId;
  readonly name: string;
  readonly kind:
    | "RELAY_TRANSPORT"
    | "MODEL_PROVIDER"
    | "AGENT_RUNTIME";
  readonly state: VertexAdapterState;
  readonly capabilities:
    readonly VertexAdapterCapability[];
  readonly gate?: string;
  readonly detail: string;
}

export interface VertexAdapterRuntimeContext {
  readonly openAiApiAvailable?: boolean;
  readonly openAiApiConfigured?: boolean;
}

export interface VertexAdapterSendContext {
  readonly endpoint?: string;
  readonly runtime?:
    VertexAdapterRuntimeContext;
}

export interface VertexAdapterSendResult {
  readonly ok: boolean;
  readonly status: number;
  readonly detail: string;
  readonly responseText?: string;
  readonly providerResponseId?: string;
  readonly model?: string;
}

export interface VertexAdapter {
  readonly descriptor: VertexAdapterDescriptor;
  send?(
    envelope: VertexRelayEnvelope,
    context: VertexAdapterSendContext,
  ): Promise<VertexAdapterSendResult>;
}


export type VertexAdapterRouteState =
  | "READY"
  | "LINK_REQUIRED"
  | "EXTERNAL_GATE"
  | "UNCONFIGURED";

export interface VertexAdapterRouteEvaluation {
  readonly adapterId: VertexAdapterId;
  readonly state: VertexAdapterRouteState;
  readonly sendable: boolean;
  readonly reason?: string;
  readonly detail: string;
}
