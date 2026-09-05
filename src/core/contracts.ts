export type LogicalOwner =
  | "workstation"
  | "forge"
  | "ray"
  | "global";

export type StateOwner =
  | "workstation.state"
  | "forge.state"
  | "ray.state"
  | "component.local";

export type ServiceOwner =
  | "workstation.runtime"
  | "forge.service"
  | "ray.service"
  | "none";

export type StyleOwner =
  | "workstation.shell"
  | "workstation.presentation"
  | "forge.presentation"
  | "ray.presentation";

export type ComponentLifecycle =
  | "persistent"
  | "workspace"
  | "ephemeral";

export interface ComponentContract {
  readonly componentId: string;
  readonly logicalOwner: LogicalOwner;
  readonly stateOwner: StateOwner;
  readonly serviceOwner: ServiceOwner;
  readonly styleOwner: StyleOwner;
  readonly lifecycle: ComponentLifecycle;
  readonly dependencies: readonly string[];
  readonly deletePolicy: "deny-while-referenced" | "safe";
}
