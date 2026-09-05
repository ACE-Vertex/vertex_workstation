export type Provenance =
  | "ACTIVE"
  | "HISTORY"
  | "BACKUP"
  | "GENERATED"
  | "VENDOR"
  | "BUILD";

export interface RayFile {
  readonly id: string;
  readonly path: string;
  readonly relativePath: string;
  readonly name: string;
  readonly extension: string;
  readonly sizeBytes: number;
  readonly modifiedUnixMs: number;
  readonly provenance: Provenance;
  readonly kind: string;
  readonly textCandidate: boolean;
}

export interface RayScanResult {
  readonly root: string;
  readonly files: readonly RayFile[];
  readonly scannedCount: number;
  readonly skippedCount: number;
  readonly skippedPaths: readonly string[];
}

export interface RayFileContent {
  readonly path: string;
  readonly relativePath: string;
  readonly encoding: string;
  readonly truncated: boolean;
  readonly sizeBytes: number;
  readonly lineCount: number;
  readonly content: string;
}

export interface RayLineFact {
  readonly name: string;
  readonly kind: string;
  readonly line: number;
  readonly column: number;
  readonly evidence: string;
}

export interface RayLexicalFacts {
  readonly imports: readonly string[];
  readonly symbols: readonly string[];
  readonly importFacts: readonly RayLineFact[];
  readonly symbolFacts: readonly RayLineFact[];
  readonly todoLines: readonly number[];
  readonly eventLines: readonly number[];
  readonly directDomMutationLines: readonly number[];
  readonly cssFixedLines: readonly number[];
  readonly cssZIndexLines: readonly number[];
  readonly todoCount: number;
  readonly eventBindingCount: number;
  readonly directDomMutationCount: number;
  readonly cssFixedCount: number;
  readonly cssZIndexCount: number;
}

export interface RayFinding {
  readonly id: string;
  readonly severity: "INFO" | "ATTENTION" | "PASS";
  readonly title: string;
  readonly evidence: string;
  readonly source: string;
  readonly confidence: number;
  readonly lineStart?: number;
  readonly lineEnd?: number;
  readonly factKind?: string;
}

export type RayMode = "IDLE" | "QUICK" | "DEEP";
export type RayRuntimeState = "READY" | "SCANNING" | "READING" | "ERROR";
