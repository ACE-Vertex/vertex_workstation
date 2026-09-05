export type ArtifactStatus = "READY" | "ATTENTION";
export type ArtifactStageHistory = "NONE" | "ERROR" | "VERIFIED";

export interface ForgeArtifact {
  readonly id: string;
  readonly fileName: string;
  readonly filePath: string;
  readonly title: string;
  readonly schemaVersion: string;
  readonly source: string;
  readonly target: string;
  readonly authority: string;
  readonly payloadCount: number;
  readonly verificationCount: number;
  readonly status: ArtifactStatus;
  readonly manifestValid: boolean;
  readonly targetAuthorized: boolean;
  readonly sizeBytes: number;
  readonly modifiedUnixMs: number;
  readonly artifactSha256: string;
  readonly stageHistory: ArtifactStageHistory;
  readonly operationPreview: readonly string[];
  readonly errors: readonly string[];
}

export interface ForgeScanResult {
  readonly receivingBay: string;
  readonly productionRoot: string;
  readonly artifacts: readonly ForgeArtifact[];
  readonly ignoredCount: number;
}

export interface ForgePathState {
  readonly receivingBay: string;
  readonly productionRoot: string;
}

export interface ForgeStageOperation {
  readonly source: string;
  readonly destination: string;
  readonly sha256: string;
  readonly verifiedSha256: string;
  readonly existedBefore: boolean;
}

export interface ForgeStageResult {
  readonly stageId: string;
  readonly artifactId: string;
  readonly artifactSha256: string;
  readonly stagingRoot: string;
  readonly stagedFilesRoot: string;
  readonly targetRoot: string;
  readonly backupPlanRoot: string;
  readonly payloadCount: number;
  readonly verifiedCount: number;
  readonly operations: readonly ForgeStageOperation[];
}

export interface ForgeApplyOperation {
  readonly destination: string;
  readonly existedBefore: boolean;
  readonly backupPath: string | null;
  readonly appliedSha256: string;
}

export interface ForgeApplyResult {
  readonly stageId: string;
  readonly artifactId: string;
  readonly artifactSha256: string;
  readonly targetRoot: string;
  readonly backupRoot: string;
  readonly appliedCount: number;
  readonly operations: readonly ForgeApplyOperation[];
}

export interface ForgeRollbackResult {
  readonly stageId: string;
  readonly targetRoot: string;
  readonly restoredCount: number;
  readonly removedCount: number;
}

export type ForgeRuntimeState =
  | "READY"
  | "SCANNING"
  | "STAGING"
  | "APPLYING"
  | "ROLLING_BACK"
  | "ERROR";
