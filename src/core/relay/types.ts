export type VertexRelayType =
  | "CANONICAL"
  | "ARCHITECTURE_CONTRACT";

export type VertexRelayAction =
  | "SHARE"
  | "DRAFT"
  | "AMEND";

export interface VertexRelayEnvelope<TPayload = unknown> {
  readonly schema: "vertex-relay/1";
  readonly type: VertexRelayType;
  readonly action: VertexRelayAction;
  readonly source: "VERTEX_WORKSTATION" | "VERA";
  readonly target: "VERA" | "VERTEX_WORKSTATION";
  readonly subject: {
    readonly id: string;
    readonly name: string;
  };
  readonly timestamp: string;
  readonly payload: TPayload;
}
