import type { VertexUnitDefinition } from "../contracts/unit";
import { rayUnit } from "../units/ray";
import { forgeUnit } from "../units/forge";

export const workstationUnits: readonly VertexUnitDefinition[] = [
  rayUnit,
  forgeUnit,
];
