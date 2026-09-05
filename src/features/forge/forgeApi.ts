import { invoke } from "@tauri-apps/api/core";
import type {
  ForgeApplyResult,
  ForgeRollbackResult,
  ForgeScanResult,
  ForgeStageResult,
} from "./models";

export function isForgeTauriRuntime(): boolean {
  return "__TAURI_INTERNALS__" in window;
}

export async function scanReceivingBay(
  receivingBay: string,
  productionRoot: string,
): Promise<ForgeScanResult> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE FILESYSTEM REQUIRES TAURI RUNTIME");
  }

  return invoke<ForgeScanResult>("forge_scan_receiving_bay", {
    receivingBay,
    productionRoot,
  });
}

export async function readReceivingBayFingerprint(
  receivingBay: string,
): Promise<string> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE RECEIVING WATCH REQUIRES TAURI RUNTIME");
  }

  return invoke<string>("forge_receiving_bay_fingerprint", {
    receivingBay,
  });
}

export async function stageForgeArtifact(
  vraPath: string,
  productionRoot: string,
): Promise<ForgeStageResult> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE STAGE REQUIRES TAURI RUNTIME");
  }

  return invoke<ForgeStageResult>("forge_stage_artifact", {
    vraPath,
    productionRoot,
  });
}

export async function applyForgeStage(
  stageId: string,
  productionRoot: string,
): Promise<ForgeApplyResult> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE APPLY REQUIRES TAURI RUNTIME");
  }

  return invoke<ForgeApplyResult>("forge_apply_stage", {
    stageId,
    productionRoot,
  });
}

export async function rollbackForgeStage(
  stageId: string,
  productionRoot: string,
): Promise<ForgeRollbackResult> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE ROLLBACK REQUIRES TAURI RUNTIME");
  }

  return invoke<ForgeRollbackResult>("forge_rollback_stage", {
    stageId,
    productionRoot,
  });
}

export async function pickForgeFolder(
  currentPath: string,
  label: string,
): Promise<string | null> {
  if (!isForgeTauriRuntime()) {
    throw new Error("FORGE FOLDER PICKER REQUIRES TAURI RUNTIME");
  }

  return invoke<string | null>("forge_pick_folder", {
    currentPath,
    label,
  });
}
