import { invoke } from "@tauri-apps/api/core";
import type { RayFileContent, RayScanResult } from "./models";

export function isTauriRuntime(): boolean {
  return "__TAURI_INTERNALS__" in window;
}

export async function pickProjectRoot(currentRoot: string): Promise<string | null> {
  if (!isTauriRuntime()) {
    throw new Error("RAY FILESYSTEM REQUIRES TAURI RUNTIME");
  }

  return invoke<string | null>("ray_pick_project_root", {
    currentRoot,
  });
}

export async function scanProject(root: string): Promise<RayScanResult> {
  if (!isTauriRuntime()) {
    throw new Error("RAY FILESYSTEM REQUIRES TAURI RUNTIME");
  }

  return invoke<RayScanResult>("ray_scan_project", { root });
}

export async function readProjectFile(
  root: string,
  path: string,
): Promise<RayFileContent> {
  if (!isTauriRuntime()) {
    throw new Error("RAY FILESYSTEM REQUIRES TAURI RUNTIME");
  }

  return invoke<RayFileContent>("ray_read_project_file", {
    root,
    path,
  });
}
