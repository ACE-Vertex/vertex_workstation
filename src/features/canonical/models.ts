export type CanonicalStatus =
  | "ADOPTED"
  | "STABLE"
  | "DRAFT";

export type CanonicalImportance =
  | "CRITICAL"
  | "IMPORTANT"
  | "NORMAL";

export interface CanonicalConcept {
  readonly id: string;
  readonly formalName: string;
  readonly abbreviation: string;
  readonly status: CanonicalStatus;
  readonly importance: CanonicalImportance;
  readonly scope: string;
  readonly category: string;
  readonly summary: string;
  readonly functionText: string;
  readonly description: string;
  readonly origin: string;
  readonly aliases: string;
  readonly related: string;
  readonly flavorBadge: string;
  readonly adoptedBy: string;
  readonly notes: string;
}
