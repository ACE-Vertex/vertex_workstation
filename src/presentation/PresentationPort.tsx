import type { CSSProperties, PropsWithChildren } from "react";
import { getComponentContract } from "../core/componentRegistry";
import { LAYOUT_SLOTS, type LayoutSlotId } from "../layout/layoutModel";

interface PresentationPortProps extends PropsWithChildren {
  readonly componentId: string;
  readonly slotId: LayoutSlotId;
}

export function PresentationPort({
  componentId,
  slotId,
  children,
}: PresentationPortProps) {
  const contract = getComponentContract(componentId);
  const slot = LAYOUT_SLOTS[slotId];

  const style: CSSProperties = {
    gridColumn: `${slot.columnStart} / span ${slot.columnSpan}`,
    gridRow: `${slot.rowStart} / span ${slot.rowSpan}`,
  };

  return (
    <section
      className="presentation-port"
      style={style}
      data-component-id={contract.componentId}
      data-logical-owner={contract.logicalOwner}
      data-state-owner={contract.stateOwner}
      data-service-owner={contract.serviceOwner}
      data-style-owner={contract.styleOwner}
      data-layout-slot={slot.id}
    >
      {children}
    </section>
  );
}
