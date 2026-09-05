import type {
  VertexRelayAction,
  VertexRelayEnvelope,
  VertexRelayType,
} from "./types";

export function createVertexRelay<TPayload>(args: {
  readonly type: VertexRelayType;
  readonly action?: VertexRelayAction;
  readonly subjectId: string;
  readonly subjectName: string;
  readonly payload: TPayload;
}): VertexRelayEnvelope<TPayload> {
  return {
    schema: "vertex-relay/1",
    type: args.type,
    action: args.action ?? "SHARE",
    source: "VERTEX_WORKSTATION",
    target: "VERA",
    subject: {
      id: args.subjectId,
      name: args.subjectName,
    },
    timestamp: new Date().toISOString(),
    payload: args.payload,
  };
}

export function serializeVertexRelay(
  envelope: VertexRelayEnvelope,
): string {
  return JSON.stringify(envelope, null, 2);
}

export function parseVertexRelay(
  raw: string,
): VertexRelayEnvelope {
  const value = JSON.parse(raw) as Partial<VertexRelayEnvelope>;

  if (value.schema !== "vertex-relay/1") {
    throw new Error("VERTEX_RELAY_SCHEMA_INVALID");
  }

  if (
    value.type !== "CANONICAL" &&
    value.type !== "ARCHITECTURE_CONTRACT"
  ) {
    throw new Error("VERTEX_RELAY_TYPE_INVALID");
  }

  if (
    value.action !== "SHARE" &&
    value.action !== "DRAFT" &&
    value.action !== "AMEND"
  ) {
    throw new Error("VERTEX_RELAY_ACTION_INVALID");
  }

  if (
    value.source !== "VERTEX_WORKSTATION" &&
    value.source !== "VERA"
  ) {
    throw new Error("VERTEX_RELAY_SOURCE_INVALID");
  }

  if (
    value.target !== "VERA" &&
    value.target !== "VERTEX_WORKSTATION"
  ) {
    throw new Error("VERTEX_RELAY_TARGET_INVALID");
  }

  if (
    !value.subject ||
    typeof value.subject.id !== "string" ||
    typeof value.subject.name !== "string"
  ) {
    throw new Error("VERTEX_RELAY_SUBJECT_INVALID");
  }

  if (!("payload" in value)) {
    throw new Error("VERTEX_RELAY_PAYLOAD_MISSING");
  }

  return value as VertexRelayEnvelope;
}
