import type { Component } from "vue";

export type VertexUnitId = "ray" | "forge";

export type VertexUnitAuthority =
  | "READ_ONLY"
  | "HUMAN_APPLY";

export type VertexUnitCapability =
  | "observe.tree"
  | "observe.deep"
  | "observe.file"
  | "observe.evidence"
  | "forge.receive"
  | "forge.validate"
  | "forge.stage"
  | "forge.apply"
  | "forge.verify"
  | "forge.restore"
  | "forge.rollback";

export interface VertexUnitManifest {
  id: VertexUnitId;
  version: string;
  displayName: string;
  authority: VertexUnitAuthority;
  capabilities: readonly VertexUnitCapability[];
  hostNeutral: true;
  detachable: true;
}

export interface VertexHostEvent<TPayload = unknown> {
  source: VertexUnitId | "host";
  topic: string;
  payload: TPayload;
}

export interface VertexHostBus {
  publish<TPayload>(event: VertexHostEvent<TPayload>): void;
  subscribe(topic: string, handler: (event: VertexHostEvent) => void): () => void;
}

export interface VertexUnitHostContext {
  bus: VertexHostBus;
  hostId: string;
}

export interface VertexUnitMountHandle {
  unitId: VertexUnitId;
  disconnect(): void;
}

export interface VertexUnitDefinition {
  manifest: VertexUnitManifest;
  component: Component;
}
