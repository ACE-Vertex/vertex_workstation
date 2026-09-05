export type LayoutSlotId = "A1" | "B1" | "C1";

export interface LayoutSlot {
  readonly id: LayoutSlotId;
  readonly columnStart: number;
  readonly columnSpan: number;
  readonly rowStart: number;
  readonly rowSpan: number;
}

export const LAYOUT_SLOTS: Record<LayoutSlotId, LayoutSlot> = {
  A1: { id: "A1", columnStart: 1, columnSpan: 4, rowStart: 1, rowSpan: 2 },
  B1: { id: "B1", columnStart: 5, columnSpan: 4, rowStart: 1, rowSpan: 2 },
  C1: { id: "C1", columnStart: 9, columnSpan: 4, rowStart: 1, rowSpan: 2 },
};
