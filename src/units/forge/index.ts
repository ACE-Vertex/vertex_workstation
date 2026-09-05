import ForgeUnit from "./ForgeUnit.vue";
import type { VertexUnitDefinition, VertexUnitManifest } from "../../contracts/unit";

export const forgeManifest: VertexUnitManifest = {
  id: "forge",
  version: "0.1.0",
  displayName: "FORGE UNIT",
  authority: "HUMAN_APPLY",
  capabilities: [
    "forge.receive",
    "forge.validate",
    "forge.stage",
    "forge.apply",
    "forge.verify",
    "forge.restore",
    "forge.rollback",
  ],
  hostNeutral: true,
  detachable: true,
};

export const forgeUnit: VertexUnitDefinition = {
  manifest: forgeManifest,
  component: ForgeUnit,
};
