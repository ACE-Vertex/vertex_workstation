import type { ComponentContract } from "./contracts";

const contracts = [
  {
    componentId: "forge.seed",
    logicalOwner: "forge",
    stateOwner: "component.local",
    serviceOwner: "none",
    styleOwner: "forge.presentation",
    lifecycle: "workspace",
    dependencies: [],
    deletePolicy: "deny-while-referenced",
  },
] as const satisfies readonly ComponentContract[];

const registry = new Map<string, ComponentContract>(
  contracts.map((contract) => [contract.componentId, contract]),
);

export function getComponentContract(componentId: string): ComponentContract {
  const contract = registry.get(componentId);
  if (!contract) {
    throw new Error(`Unknown component contract: ${componentId}`);
  }
  return contract;
}

export function listComponentContracts(): readonly ComponentContract[] {
  return Object.freeze([...registry.values()]);
}
