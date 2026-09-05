import RayUnit from "./RayUnit.vue";
import type { VertexUnitDefinition, VertexUnitManifest } from "../../contracts/unit";

export const rayManifest: VertexUnitManifest = {
  id: "ray",
  version: "0.1.0",
  displayName: "RAY UNIT",
  authority: "READ_ONLY",
  capabilities: [
    "observe.tree",
    "observe.deep",
    "observe.file",
    "observe.evidence",
  ],
  hostNeutral: true,
  detachable: true,
};

export const rayUnit: VertexUnitDefinition = {
  manifest: rayManifest,
  component: RayUnit,
};
