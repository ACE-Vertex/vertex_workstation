mod forge_apply;
mod openai_api;

use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    env,
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Component, Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};
use zip::ZipArchive;

const MAX_SCAN_FILES: usize = 20_000;
const MAX_SCAN_DEPTH: usize = 64;
const MAX_READ_BYTES: usize = 512 * 1024;
const MAX_VRA_MANIFEST_BYTES: u64 = 256 * 1024;
const MAX_STAGE_FILE_BYTES: u64 = 64 * 1024 * 1024;
const MAX_STAGE_TOTAL_BYTES: u64 = 512 * 1024 * 1024;

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct RayFile {
    id: String,
    path: String,
    relative_path: String,
    name: String,
    extension: String,
    size_bytes: u64,
    modified_unix_ms: u64,
    provenance: String,
    kind: String,
    text_candidate: bool,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct RayScanResult {
    root: String,
    files: Vec<RayFile>,
    scanned_count: usize,
    skipped_count: usize,
    skipped_paths: Vec<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct RayFileContent {
    path: String,
    relative_path: String,
    encoding: String,
    truncated: bool,
    size_bytes: u64,
    line_count: usize,
    content: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ForgeArtifact {
    id: String,
    file_name: String,
    file_path: String,
    title: String,
    schema_version: String,
    source: String,
    target: String,
    authority: String,
    payload_count: usize,
    verification_count: usize,
    status: String,
    manifest_valid: bool,
    target_authorized: bool,
    size_bytes: u64,
    modified_unix_ms: u64,
    artifact_sha256: String,
    stage_history: String,
    operation_preview: Vec<String>,
    errors: Vec<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ForgeScanResult {
    receiving_bay: String,
    production_root: String,
    artifacts: Vec<ForgeArtifact>,
    ignored_count: usize,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ForgeStageOperation {
    source: String,
    destination: String,
    sha256: String,
    verified_sha256: String,
    existed_before: bool,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ForgeStageResult {
    stage_id: String,
    artifact_id: String,
    artifact_sha256: String,
    staging_root: String,
    staged_files_root: String,
    target_root: String,
    backup_plan_root: String,
    payload_count: usize,
    verified_count: usize,
    operations: Vec<ForgeStageOperation>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct ForgeHistoryEvent {
    schema: &'static str,
    timestamp_unix_ms: u64,
    artifact_id: String,
    artifact_sha256: String,
    outcome: String,
    detail: String,
}

fn normalize_display(path: &Path) -> String {
    let raw = path.to_string_lossy().to_string();

    if let Some(rest) = raw.strip_prefix("\\\\?\\UNC\\") {
        return format!("\\\\{}", rest);
    }

    if let Some(rest) = raw.strip_prefix("\\\\?\\") {
        return rest.to_string();
    }

    raw
}

fn stable_id(relative: &Path) -> String {
    relative.to_string_lossy().replace('\\', "/").to_lowercase()
}

fn classify_provenance(relative: &Path) -> &'static str {
    let lowered = relative.to_string_lossy().replace('\\', "/").to_lowercase();

    if lowered.contains("/node_modules/")
        || lowered.starts_with("node_modules/")
        || lowered.contains("/vendor/")
        || lowered.starts_with("vendor/")
    {
        return "VENDOR";
    }

    if lowered.contains("/target/")
        || lowered.starts_with("target/")
        || lowered.contains("/dist/")
        || lowered.starts_with("dist/")
        || lowered.contains("/build/")
        || lowered.starts_with("build/")
        || lowered.contains("/builds/")
        || lowered.starts_with("builds/")
    {
        return "BUILD";
    }

    if lowered.contains("/backup/")
        || lowered.starts_with("backup/")
        || lowered.contains("/backups/")
        || lowered.starts_with("backups/")
    {
        return "BACKUP";
    }

    if lowered.contains("/versions/")
        || lowered.starts_with("versions/")
        || lowered.contains("/history/")
        || lowered.starts_with("history/")
        || lowered.contains("/.history/")
        || lowered.starts_with(".history/")
    {
        return "HISTORY";
    }

    if lowered.contains("/generated/")
        || lowered.starts_with("generated/")
        || lowered.contains("/runtime/")
        || lowered.starts_with("runtime/")
    {
        return "GENERATED";
    }

    "ACTIVE"
}

fn kind_for(path: &Path) -> String {
    let ext = path
        .extension()
        .and_then(|value| value.to_str())
        .unwrap_or("")
        .to_lowercase();

    if ext.is_empty() {
        "file".to_string()
    } else {
        ext
    }
}

fn is_text_candidate(path: &Path) -> bool {
    let ext = path
        .extension()
        .and_then(|value| value.to_str())
        .unwrap_or("")
        .to_lowercase();

    matches!(
        ext.as_str(),
        "" | "txt"
            | "md"
            | "json"
            | "jsonc"
            | "toml"
            | "yaml"
            | "yml"
            | "xml"
            | "html"
            | "htm"
            | "css"
            | "scss"
            | "sass"
            | "less"
            | "js"
            | "jsx"
            | "mjs"
            | "cjs"
            | "ts"
            | "tsx"
            | "vue"
            | "rs"
            | "c"
            | "h"
            | "cpp"
            | "hpp"
            | "cs"
            | "java"
            | "kt"
            | "kts"
            | "py"
            | "rb"
            | "php"
            | "go"
            | "swift"
            | "sql"
            | "ps1"
            | "cmd"
            | "bat"
            | "sh"
            | "ini"
            | "conf"
            | "cfg"
            | "env"
            | "gitignore"
            | "gitattributes"
            | "lock"
    )
}

fn should_skip_dir(name: &str) -> bool {
    matches!(
        name.to_lowercase().as_str(),
        ".git"
            | "node_modules"
            | "target"
            | "dist"
            | "build"
            | "builds"
            | "versions"
            | ".cache"
            | ".idea"
            | ".vscode"
    )
}

fn scan_dir(
    root: &Path,
    dir: &Path,
    depth: usize,
    files: &mut Vec<RayFile>,
    skipped_count: &mut usize,
    skipped_paths: &mut Vec<String>,
) -> Result<(), String> {
    if depth > MAX_SCAN_DEPTH || files.len() >= MAX_SCAN_FILES {
        *skipped_count += 1;
        if skipped_paths.len() < 64 {
            skipped_paths.push(normalize_display(dir));
        }
        return Ok(());
    }

    let entries = fs::read_dir(dir)
        .map_err(|error| format!("READ_DIR_FAILED {}: {}", normalize_display(dir), error))?;

    for entry in entries {
        if files.len() >= MAX_SCAN_FILES {
            *skipped_count += 1;
            if skipped_paths.len() < 64 {
                skipped_paths.push("MAX_SCAN_FILES_REACHED".to_string());
            }
            break;
        }

        let entry = match entry {
            Ok(value) => value,
            Err(_) => {
                *skipped_count += 1;
                continue;
            }
        };

        let path = entry.path();
        let metadata = match fs::symlink_metadata(&path) {
            Ok(value) => value,
            Err(_) => {
                *skipped_count += 1;
                continue;
            }
        };

        if metadata.file_type().is_symlink() {
            *skipped_count += 1;
            if skipped_paths.len() < 64 {
                skipped_paths.push(normalize_display(&path));
            }
            continue;
        }

        if metadata.is_dir() {
            let name = path
                .file_name()
                .and_then(|value| value.to_str())
                .unwrap_or("");

            if should_skip_dir(name) {
                *skipped_count += 1;
                if skipped_paths.len() < 64 {
                    skipped_paths.push(normalize_display(&path));
                }
                continue;
            }

            scan_dir(root, &path, depth + 1, files, skipped_count, skipped_paths)?;
            continue;
        }

        if !metadata.is_file() {
            continue;
        }

        let relative = path.strip_prefix(root).unwrap_or(&path);
        let modified_unix_ms = metadata
            .modified()
            .ok()
            .and_then(|value| value.duration_since(UNIX_EPOCH).ok())
            .map(|value| value.as_millis() as u64)
            .unwrap_or(0);

        files.push(RayFile {
            id: stable_id(relative),
            path: normalize_display(&path),
            relative_path: normalize_display(relative),
            name: path
                .file_name()
                .and_then(|value| value.to_str())
                .unwrap_or("")
                .to_string(),
            extension: path
                .extension()
                .and_then(|value| value.to_str())
                .unwrap_or("")
                .to_lowercase(),
            size_bytes: metadata.len(),
            modified_unix_ms,
            provenance: classify_provenance(relative).to_string(),
            kind: kind_for(&path),
            text_candidate: is_text_candidate(&path),
        });
    }

    Ok(())
}

fn canonical_root(root: &str) -> Result<PathBuf, String> {
    let path = PathBuf::from(root);

    if !path.exists() {
        return Err(format!("PROJECT_ROOT_NOT_FOUND: {}", root));
    }

    if !path.is_dir() {
        return Err(format!("PROJECT_ROOT_NOT_DIRECTORY: {}", root));
    }

    path.canonicalize()
        .map_err(|error| format!("PROJECT_ROOT_CANONICALIZE_FAILED: {}", error))
}

fn guarded_file(root: &str, path: &str) -> Result<(PathBuf, PathBuf), String> {
    let root = canonical_root(root)?;
    let file = PathBuf::from(path)
        .canonicalize()
        .map_err(|error| format!("FILE_CANONICALIZE_FAILED: {}", error))?;

    if !file.starts_with(&root) {
        return Err("FILE_OUTSIDE_PROJECT_ROOT".to_string());
    }

    if !file.is_file() {
        return Err("TARGET_IS_NOT_FILE".to_string());
    }

    Ok((root, file))
}

fn json_string(value: &Value, pointer: &str) -> String {
    value
        .pointer(pointer)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string()
}

fn target_is_authorized(target: &str, production_root: &Path) -> bool {
    if target.is_empty() {
        return false;
    }

    let root = normalize_display(production_root)
        .replace('/', "\\")
        .trim_end_matches('\\')
        .to_lowercase();
    let candidate = target
        .replace('/', "\\")
        .trim_end_matches('\\')
        .to_lowercase();

    candidate == root || candidate.starts_with(&(root + "\\"))
}

fn sha256_bytes(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

fn sha256_file(path: &Path) -> Result<String, String> {
    let bytes = fs::read(path).map_err(|error| format!("ARTIFACT_READ_FAILED: {}", error))?;
    Ok(sha256_bytes(&bytes))
}

fn safe_relative_path(raw: &str, label: &str) -> Result<PathBuf, String> {
    if raw.trim().is_empty() {
        return Err(format!("{}_EMPTY", label));
    }

    let path = PathBuf::from(raw);

    if path.is_absolute() {
        return Err(format!("{}_ABSOLUTE_BLOCKED: {}", label, raw));
    }

    for component in path.components() {
        match component {
            Component::Normal(_) | Component::CurDir => {}
            Component::ParentDir | Component::RootDir | Component::Prefix(_) => {
                return Err(format!("{}_TRAVERSAL_BLOCKED: {}", label, raw));
            }
        }
    }

    Ok(path)
}

fn safe_stage_component(raw: &str) -> String {
    let cleaned: String = raw
        .chars()
        .map(|ch| {
            if ch.is_ascii_alphanumeric() || ch == '-' || ch == '_' || ch == '.' {
                ch
            } else {
                '_'
            }
        })
        .collect();

    let trimmed = cleaned.trim_matches('_');
    if trimmed.is_empty() {
        "artifact".to_string()
    } else {
        trimmed.chars().take(80).collect()
    }
}

fn stage_base_root() -> Result<PathBuf, String> {
    let local =
        env::var_os("LOCALAPPDATA").ok_or_else(|| "LOCALAPPDATA_UNAVAILABLE".to_string())?;

    Ok(PathBuf::from(local)
        .join("VertexWorkstation")
        .join("staging"))
}

fn backup_base_root() -> Result<PathBuf, String> {
    let local =
        env::var_os("LOCALAPPDATA").ok_or_else(|| "LOCALAPPDATA_UNAVAILABLE".to_string())?;

    Ok(PathBuf::from(local)
        .join("VertexWorkstation")
        .join("backups"))
}

fn forge_history_file() -> Result<PathBuf, String> {
    let local =
        env::var_os("LOCALAPPDATA").ok_or_else(|| "LOCALAPPDATA_UNAVAILABLE".to_string())?;

    Ok(PathBuf::from(local)
        .join("VertexWorkstation")
        .join("forge_history")
        .join("events.jsonl"))
}

fn append_forge_history_event(
    artifact_id: &str,
    artifact_sha256: &str,
    outcome: &str,
    detail: &str,
) -> Result<(), String> {
    if artifact_sha256.is_empty() {
        return Ok(());
    }

    let path = forge_history_file()?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("FORGE_HISTORY_CREATE_FAILED: {}", error))?;
    }

    let timestamp_unix_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|value| value.as_millis() as u64)
        .map_err(|error| format!("CLOCK_ERROR: {}", error))?;

    let event = ForgeHistoryEvent {
        schema: "forge-history/1",
        timestamp_unix_ms,
        artifact_id: artifact_id.to_string(),
        artifact_sha256: artifact_sha256.to_string(),
        outcome: outcome.to_string(),
        detail: detail.to_string(),
    };

    let line = serde_json::to_string(&event)
        .map_err(|error| format!("FORGE_HISTORY_SERIALIZE_FAILED: {}", error))?;

    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .map_err(|error| format!("FORGE_HISTORY_OPEN_FAILED: {}", error))?;

    writeln!(file, "{}", line).map_err(|error| format!("FORGE_HISTORY_WRITE_FAILED: {}", error))?;
    file.sync_all()
        .map_err(|error| format!("FORGE_HISTORY_SYNC_FAILED: {}", error))?;

    Ok(())
}

fn promote_history_state(
    index: &mut HashMap<String, String>,
    artifact_sha256: &str,
    outcome: &str,
) {
    if artifact_sha256.is_empty() {
        return;
    }

    let current = index
        .entry(artifact_sha256.to_string())
        .or_insert_with(|| "NONE".to_string());

    if outcome == "STAGE_VERIFIED" {
        *current = "VERIFIED".to_string();
    } else if outcome == "STAGE_ERROR" && current != "VERIFIED" {
        *current = "ERROR".to_string();
    }
}

fn load_forge_history_index() -> HashMap<String, String> {
    let mut index = HashMap::new();

    if let Ok(path) = forge_history_file() {
        if let Ok(text) = fs::read_to_string(path) {
            for line in text.lines() {
                let value: Value = match serde_json::from_str(line) {
                    Ok(value) => value,
                    Err(_) => continue,
                };

                let schema = value.get("schema").and_then(Value::as_str).unwrap_or("");
                if schema != "forge-history/1" {
                    continue;
                }

                let artifact_sha256 = value
                    .get("artifactSha256")
                    .and_then(Value::as_str)
                    .unwrap_or("");
                let outcome = value.get("outcome").and_then(Value::as_str).unwrap_or("");

                promote_history_state(&mut index, artifact_sha256, outcome);
            }
        }
    }

    // Backfill successful history from immutable Stage snapshots created
    // before the persistent history ledger existed.
    if let Ok(stage_root) = stage_base_root() {
        if let Ok(entries) = fs::read_dir(stage_root) {
            for entry in entries.flatten() {
                let report_path = entry.path().join("stage_report.json");
                let text = match fs::read_to_string(report_path) {
                    Ok(value) => value,
                    Err(_) => continue,
                };
                let value: Value = match serde_json::from_str(&text) {
                    Ok(value) => value,
                    Err(_) => continue,
                };
                let artifact_sha256 = value
                    .get("artifactSha256")
                    .and_then(Value::as_str)
                    .unwrap_or("");

                promote_history_state(&mut index, artifact_sha256, "STAGE_VERIFIED");
            }
        }
    }

    index
}

fn unix_millis() -> Result<u128, String> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|value| value.as_millis())
        .map_err(|error| format!("CLOCK_ERROR: {}", error))
}

fn inspect_vra(
    path: &Path,
    production_root: &Path,
    history: &HashMap<String, String>,
) -> ForgeArtifact {
    let metadata = fs::metadata(path).ok();
    let size_bytes = metadata.as_ref().map(|value| value.len()).unwrap_or(0);
    let modified_unix_ms = metadata
        .and_then(|value| value.modified().ok())
        .and_then(|value| value.duration_since(UNIX_EPOCH).ok())
        .map(|value| value.as_millis() as u64)
        .unwrap_or(0);

    let artifact_sha256 = sha256_file(path).unwrap_or_default();

    let file_name = path
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or("unknown.vra")
        .to_string();

    let fallback_id = path
        .file_stem()
        .and_then(|value| value.to_str())
        .unwrap_or("unknown")
        .to_string();

    let mut artifact = ForgeArtifact {
        id: fallback_id.clone(),
        file_name: file_name.clone(),
        file_path: normalize_display(path),
        title: file_name,
        schema_version: String::new(),
        source: String::new(),
        target: String::new(),
        authority: String::new(),
        payload_count: 0,
        verification_count: 0,
        status: "ATTENTION".to_string(),
        manifest_valid: false,
        target_authorized: false,
        size_bytes,
        modified_unix_ms,
        artifact_sha256,
        stage_history: "NONE".to_string(),
        operation_preview: Vec::new(),
        errors: Vec::new(),
    };

    let file = match File::open(path) {
        Ok(value) => value,
        Err(error) => {
            artifact.errors.push(format!("VRA_OPEN_FAILED: {}", error));
            return artifact;
        }
    };

    let mut archive = match ZipArchive::new(file) {
        Ok(value) => value,
        Err(error) => {
            artifact.errors.push(format!("VRA_ZIP_INVALID: {}", error));
            return artifact;
        }
    };

    let mut manifest_file = match archive.by_name("manifest.json") {
        Ok(value) => value,
        Err(_) => {
            artifact.errors.push("MANIFEST_ROOT_MISSING".to_string());
            return artifact;
        }
    };

    if manifest_file.size() > MAX_VRA_MANIFEST_BYTES {
        artifact
            .errors
            .push("MANIFEST_TOO_LARGE_GT_256K".to_string());
        return artifact;
    }

    let mut manifest_text = String::new();
    if let Err(error) = manifest_file.read_to_string(&mut manifest_text) {
        artifact
            .errors
            .push(format!("MANIFEST_READ_FAILED: {}", error));
        return artifact;
    }

    let manifest: Value = match serde_json::from_str(&manifest_text) {
        Ok(value) => value,
        Err(error) => {
            artifact
                .errors
                .push(format!("MANIFEST_JSON_INVALID: {}", error));
            return artifact;
        }
    };

    artifact.schema_version = json_string(&manifest, "/schema_version");
    artifact.id = json_string(&manifest, "/artifact_id");
    if artifact.id.is_empty() {
        artifact.id = fallback_id;
        artifact.errors.push("ARTIFACT_ID_MISSING".to_string());
    }

    artifact.title = json_string(&manifest, "/title");
    if artifact.title.is_empty() {
        artifact.title = artifact.file_name.clone();
        artifact.errors.push("TITLE_MISSING".to_string());
    }

    let actor = json_string(&manifest, "/source/actor");
    let model = json_string(&manifest, "/source/model");
    artifact.source = match (actor.is_empty(), model.is_empty()) {
        (false, false) => format!("{} / {}", actor, model),
        (false, true) => actor,
        (true, false) => model,
        (true, true) => "UNKNOWN".to_string(),
    };

    artifact.target = json_string(&manifest, "/target/project_root");
    artifact.authority = json_string(&manifest, "/authority");

    let operations = manifest
        .get("operations")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    artifact.payload_count = operations.len();
    artifact.operation_preview = operations
        .iter()
        .take(12)
        .enumerate()
        .map(|(index, operation)| {
            let op = operation
                .get("op")
                .and_then(Value::as_str)
                .unwrap_or("unknown");
            let destination = operation
                .get("destination")
                .and_then(Value::as_str)
                .unwrap_or("destination?");
            format!("{:02} {} -> {}", index + 1, op, destination)
        })
        .collect();

    artifact.verification_count = manifest
        .get("verification")
        .and_then(Value::as_array)
        .map(|value| value.len())
        .unwrap_or(0);

    if artifact.schema_version != "vra/1" {
        artifact.errors.push(format!(
            "SCHEMA_UNSUPPORTED: {}",
            if artifact.schema_version.is_empty() {
                "missing"
            } else {
                &artifact.schema_version
            }
        ));
    }

    if artifact.authority != "HUMAN_APPLY" {
        artifact.errors.push(format!(
            "AUTHORITY_INVALID: {}",
            if artifact.authority.is_empty() {
                "missing"
            } else {
                &artifact.authority
            }
        ));
    }

    if artifact.target.is_empty() {
        artifact
            .errors
            .push("TARGET_PROJECT_ROOT_MISSING".to_string());
    }

    if operations.is_empty() {
        artifact.errors.push("OPERATIONS_EMPTY".to_string());
    }

    artifact.target_authorized = target_is_authorized(&artifact.target, production_root);
    if !artifact.target_authorized {
        artifact
            .errors
            .push("TARGET_OUTSIDE_AUTHORIZED_PRODUCTION_ROOT".to_string());
    }

    artifact.manifest_valid = artifact.errors.is_empty();
    artifact.status = if artifact.manifest_valid {
        "READY".to_string()
    } else {
        "ATTENTION".to_string()
    };

    artifact.stage_history = history
        .get(&artifact.artifact_sha256)
        .cloned()
        .unwrap_or_else(|| "NONE".to_string());

    artifact
}

#[tauri::command]
fn ray_scan_project(root: String) -> Result<RayScanResult, String> {
    let root = canonical_root(&root)?;
    let mut files = Vec::new();
    let mut skipped_count = 0usize;
    let mut skipped_paths = Vec::new();

    scan_dir(
        &root,
        &root,
        0,
        &mut files,
        &mut skipped_count,
        &mut skipped_paths,
    )?;

    files.sort_by(|a, b| {
        a.relative_path
            .to_lowercase()
            .cmp(&b.relative_path.to_lowercase())
    });

    let scanned_count = files.len();

    Ok(RayScanResult {
        root: normalize_display(&root),
        files,
        scanned_count,
        skipped_count,
        skipped_paths,
    })
}

#[tauri::command]
fn ray_read_project_file(root: String, path: String) -> Result<RayFileContent, String> {
    let (root, file) = guarded_file(&root, &path)?;
    let metadata =
        fs::metadata(&file).map_err(|error| format!("FILE_METADATA_FAILED: {}", error))?;

    let bytes = fs::read(&file).map_err(|error| format!("FILE_READ_FAILED: {}", error))?;

    let truncated = bytes.len() > MAX_READ_BYTES;
    let preview = &bytes[..bytes.len().min(MAX_READ_BYTES)];

    if preview.iter().take(8192).any(|byte| *byte == 0) {
        return Err("BINARY_FILE_PREVIEW_BLOCKED".to_string());
    }

    let (content, encoding) = match std::str::from_utf8(preview) {
        Ok(value) => (value.to_string(), "utf-8".to_string()),
        Err(_) => (
            String::from_utf8_lossy(preview).to_string(),
            "utf-8-lossy".to_string(),
        ),
    };

    let relative = file.strip_prefix(&root).unwrap_or(&file);
    let line_count = content.lines().count();

    Ok(RayFileContent {
        path: normalize_display(&file),
        relative_path: normalize_display(relative),
        encoding,
        truncated,
        size_bytes: metadata.len(),
        line_count,
        content,
    })
}

#[tauri::command]
fn forge_receiving_bay_fingerprint(receiving_bay: String) -> Result<String, String> {
    let receiving = canonical_root(&receiving_bay)?;

    let entries = fs::read_dir(&receiving).map_err(|error| {
        format!(
            "RECEIVING_BAY_READ_FAILED {}: {}",
            normalize_display(&receiving),
            error
        )
    })?;

    let mut fingerprints = Vec::new();

    for entry in entries {
        let entry = match entry {
            Ok(value) => value,
            Err(_) => continue,
        };

        let path = entry.path();
        let metadata = match fs::symlink_metadata(&path) {
            Ok(value) => value,
            Err(_) => continue,
        };

        if !metadata.is_file() || metadata.file_type().is_symlink() {
            continue;
        }

        let is_vra = path
            .extension()
            .and_then(|value| value.to_str())
            .map(|value| value.eq_ignore_ascii_case("vra"))
            .unwrap_or(false);

        if !is_vra {
            continue;
        }

        let modified_unix_ms = metadata
            .modified()
            .ok()
            .and_then(|value| value.duration_since(UNIX_EPOCH).ok())
            .map(|value| value.as_millis() as u64)
            .unwrap_or(0);

        let file_name = path
            .file_name()
            .and_then(|value| value.to_str())
            .unwrap_or_default()
            .to_lowercase();

        fingerprints.push(format!(
            "{}\u{0}{}\u{0}{}",
            file_name,
            metadata.len(),
            modified_unix_ms
        ));
    }

    fingerprints.sort();
    Ok(sha256_bytes(fingerprints.join("\n").as_bytes()))
}

#[tauri::command]
fn forge_scan_receiving_bay(
    receiving_bay: String,
    production_root: String,
) -> Result<ForgeScanResult, String> {
    let receiving = canonical_root(&receiving_bay)?;
    let production = canonical_root(&production_root)?;
    let history = load_forge_history_index();

    let entries = fs::read_dir(&receiving).map_err(|error| {
        format!(
            "RECEIVING_BAY_READ_FAILED {}: {}",
            normalize_display(&receiving),
            error
        )
    })?;

    let mut artifacts = Vec::new();
    let mut ignored_count = 0usize;

    for entry in entries {
        let entry = match entry {
            Ok(value) => value,
            Err(_) => {
                ignored_count += 1;
                continue;
            }
        };

        let path = entry.path();
        let metadata = match fs::symlink_metadata(&path) {
            Ok(value) => value,
            Err(_) => {
                ignored_count += 1;
                continue;
            }
        };

        if !metadata.is_file() || metadata.file_type().is_symlink() {
            ignored_count += 1;
            continue;
        }

        let is_vra = path
            .extension()
            .and_then(|value| value.to_str())
            .map(|value| value.eq_ignore_ascii_case("vra"))
            .unwrap_or(false);

        if !is_vra {
            ignored_count += 1;
            continue;
        }

        artifacts.push(inspect_vra(&path, &production, &history));
    }

    artifacts.sort_by(|a, b| {
        b.modified_unix_ms
            .cmp(&a.modified_unix_ms)
            .then_with(|| a.file_name.to_lowercase().cmp(&b.file_name.to_lowercase()))
    });

    Ok(ForgeScanResult {
        receiving_bay: normalize_display(&receiving),
        production_root: normalize_display(&production),
        artifacts,
        ignored_count,
    })
}

#[tauri::command]
fn forge_stage_artifact(
    vra_path: String,
    production_root: String,
) -> Result<ForgeStageResult, String> {
    let production = canonical_root(&production_root)?;

    let vra = PathBuf::from(&vra_path)
        .canonicalize()
        .map_err(|error| format!("VRA_CANONICALIZE_FAILED: {}", error))?;

    if !vra.is_file() {
        return Err("VRA_NOT_FILE".to_string());
    }

    let is_vra = vra
        .extension()
        .and_then(|value| value.to_str())
        .map(|value| value.eq_ignore_ascii_case("vra"))
        .unwrap_or(false);

    if !is_vra {
        return Err("VRA_EXTENSION_REQUIRED".to_string());
    }

    let history = load_forge_history_index();
    let inspected = inspect_vra(&vra, &production, &history);
    if !inspected.manifest_valid || inspected.status != "READY" {
        return Err(format!(
            "STAGE_GATE_FAILED: {}",
            inspected.errors.join(" | ")
        ));
    }

    if inspected.authority != "HUMAN_APPLY" {
        return Err("STAGE_AUTHORITY_NOT_HUMAN_APPLY".to_string());
    }

    let target = canonical_root(&inspected.target)?;
    if !target.starts_with(&production) {
        return Err("STAGE_TARGET_OUTSIDE_AUTHORIZED_ROOT".to_string());
    }

    let artifact_sha256 = if inspected.artifact_sha256.is_empty() {
        sha256_file(&vra)?
    } else {
        inspected.artifact_sha256.clone()
    };
    let stage_id = format!("{}-{}", safe_stage_component(&inspected.id), unix_millis()?);

    let staging_root = stage_base_root()?.join(&stage_id);
    if staging_root.exists() {
        let message = "STAGE_ID_COLLISION".to_string();
        let _ =
            append_forge_history_event(&inspected.id, &artifact_sha256, "STAGE_ERROR", &message);
        return Err(message);
    }

    let staged_files_root = staging_root.join("files");
    let backup_plan_root = backup_base_root()?.join(&stage_id);

    if let Err(error) = fs::create_dir_all(&staged_files_root) {
        let message = format!("STAGE_CREATE_FAILED: {}", error);
        let _ =
            append_forge_history_event(&inspected.id, &artifact_sha256, "STAGE_ERROR", &message);
        return Err(message);
    }

    let result = (|| -> Result<ForgeStageResult, String> {
        fs::copy(&vra, staging_root.join("artifact.vra"))
            .map_err(|error| format!("STAGE_ARTIFACT_COPY_FAILED: {}", error))?;

        let file = File::open(&vra).map_err(|error| format!("VRA_OPEN_FAILED: {}", error))?;
        let mut archive =
            ZipArchive::new(file).map_err(|error| format!("VRA_ZIP_INVALID: {}", error))?;

        let mut manifest_file = archive
            .by_name("manifest.json")
            .map_err(|_| "MANIFEST_ROOT_MISSING".to_string())?;

        if manifest_file.size() > MAX_VRA_MANIFEST_BYTES {
            return Err("MANIFEST_TOO_LARGE_GT_256K".to_string());
        }

        let mut manifest_text = String::new();
        manifest_file
            .read_to_string(&mut manifest_text)
            .map_err(|error| format!("MANIFEST_READ_FAILED: {}", error))?;
        drop(manifest_file);

        fs::write(staging_root.join("manifest.json"), manifest_text.as_bytes())
            .map_err(|error| format!("STAGE_MANIFEST_WRITE_FAILED: {}", error))?;

        let manifest: Value = serde_json::from_str(&manifest_text)
            .map_err(|error| format!("MANIFEST_JSON_INVALID: {}", error))?;

        let operations = manifest
            .get("operations")
            .and_then(Value::as_array)
            .ok_or_else(|| "OPERATIONS_MISSING".to_string())?;

        let mut staged_operations = Vec::new();
        let mut total_bytes = 0u64;

        for (index, operation) in operations.iter().enumerate() {
            let op = operation.get("op").and_then(Value::as_str).unwrap_or("");

            if op != "copy" {
                return Err(format!("STAGE_UNSUPPORTED_OP[{}]: {}", index, op));
            }

            let source = operation
                .get("source")
                .and_then(Value::as_str)
                .ok_or_else(|| format!("STAGE_SOURCE_MISSING[{}]", index))?;

            let destination = operation
                .get("destination")
                .and_then(Value::as_str)
                .ok_or_else(|| format!("STAGE_DESTINATION_MISSING[{}]", index))?;

            let expected_sha = operation
                .get("sha256")
                .and_then(Value::as_str)
                .ok_or_else(|| format!("STAGE_SHA256_MISSING[{}]", index))?
                .to_lowercase();

            let source_relative = safe_relative_path(source, "STAGE_SOURCE")?;
            let destination_relative = safe_relative_path(destination, "STAGE_DESTINATION")?;

            let source_zip_name = source_relative.to_string_lossy().replace('\\', "/");

            if !source_zip_name.starts_with("payload/") {
                return Err(format!(
                    "STAGE_SOURCE_OUTSIDE_PAYLOAD[{}]: {}",
                    index, source
                ));
            }

            let mut zip_file = archive
                .by_name(&source_zip_name)
                .map_err(|_| format!("STAGE_SOURCE_NOT_FOUND[{}]: {}", index, source_zip_name))?;

            if zip_file.size() > MAX_STAGE_FILE_BYTES {
                return Err(format!(
                    "STAGE_FILE_TOO_LARGE[{}]: {}",
                    index,
                    zip_file.size()
                ));
            }

            total_bytes = total_bytes
                .checked_add(zip_file.size())
                .ok_or_else(|| "STAGE_TOTAL_BYTES_OVERFLOW".to_string())?;

            if total_bytes > MAX_STAGE_TOTAL_BYTES {
                return Err("STAGE_TOTAL_PAYLOAD_GT_512M".to_string());
            }

            let mut bytes = Vec::with_capacity(zip_file.size() as usize);
            zip_file
                .read_to_end(&mut bytes)
                .map_err(|error| format!("STAGE_SOURCE_READ_FAILED[{}]: {}", index, error))?;

            let verified_sha = sha256_bytes(&bytes);
            if verified_sha != expected_sha {
                return Err(format!(
                    "STAGE_SHA256_MISMATCH[{}]: expected={} actual={}",
                    index, expected_sha, verified_sha
                ));
            }

            let staged_path = staged_files_root.join(&destination_relative);
            if let Some(parent) = staged_path.parent() {
                fs::create_dir_all(parent)
                    .map_err(|error| format!("STAGE_PARENT_CREATE_FAILED[{}]: {}", index, error))?;
            }

            let mut staged_file = File::create(&staged_path)
                .map_err(|error| format!("STAGE_FILE_CREATE_FAILED[{}]: {}", index, error))?;
            staged_file
                .write_all(&bytes)
                .map_err(|error| format!("STAGE_FILE_WRITE_FAILED[{}]: {}", index, error))?;
            staged_file
                .sync_all()
                .map_err(|error| format!("STAGE_FILE_SYNC_FAILED[{}]: {}", index, error))?;

            let target_path = target.join(&destination_relative);

            staged_operations.push(ForgeStageOperation {
                source: source.to_string(),
                destination: destination.to_string(),
                sha256: expected_sha,
                verified_sha256: verified_sha,
                existed_before: target_path.exists(),
            });
        }

        let result = ForgeStageResult {
            stage_id: stage_id.clone(),
            artifact_id: inspected.id.clone(),
            artifact_sha256: artifact_sha256.clone(),
            staging_root: normalize_display(&staging_root),
            staged_files_root: normalize_display(&staged_files_root),
            target_root: normalize_display(&target),
            backup_plan_root: normalize_display(&backup_plan_root),
            payload_count: staged_operations.len(),
            verified_count: staged_operations.len(),
            operations: staged_operations,
        };

        let report = serde_json::to_vec_pretty(&result)
            .map_err(|error| format!("STAGE_REPORT_SERIALIZE_FAILED: {}", error))?;
        fs::write(staging_root.join("stage_report.json"), report)
            .map_err(|error| format!("STAGE_REPORT_WRITE_FAILED: {}", error))?;

        fs::write(
            staging_root.join("STAGE_LOCK"),
            format!(
                "stage_id={}\nartifact_id={}\nartifact_sha256={}\ntarget={}\nauthority=HUMAN_APPLY\ntarget_mutation=NO\n",
                stage_id,
                inspected.id,
                artifact_sha256,
                normalize_display(&target)
            ),
        )
        .map_err(|error| {
            format!("STAGE_LOCK_WRITE_FAILED: {}", error)
        })?;

        Ok(result)
    })();

    match &result {
        Ok(_) => {
            let _ = append_forge_history_event(
                &inspected.id,
                &artifact_sha256,
                "STAGE_VERIFIED",
                "STAGE PASS",
            );
        }
        Err(error) => {
            let _ =
                append_forge_history_event(&inspected.id, &artifact_sha256, "STAGE_ERROR", error);
            let _ = fs::remove_dir_all(&staging_root);
        }
    }

    result
}

#[cfg(windows)]
fn pick_folder_windows(current_root: &str, description: &str) -> Result<Option<String>, String> {
    use std::os::windows::process::CommandExt;
    use std::process::Command;

    const CREATE_NO_WINDOW: u32 = 0x08000000;

    let safe_root = current_root.replace('\'', "''");
    let safe_description = description.replace('\'', "''");
    let script = format!(
        "$ErrorActionPreference='Stop'; \
         Add-Type -AssemblyName System.Windows.Forms; \
         $d = New-Object System.Windows.Forms.FolderBrowserDialog; \
         $d.Description = '{}'; \
         $d.ShowNewFolderButton = $false; \
         if (Test-Path '{}') {{ $d.SelectedPath = '{}'; }}; \
         if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {{ \
           [Console]::Out.Write($d.SelectedPath) \
         }}",
        safe_description, safe_root, safe_root
    );

    let output = Command::new("powershell.exe")
        .args([
            "-NoLogo",
            "-NoProfile",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            &script,
        ])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .map_err(|error| format!("FOLDER_PICKER_LAUNCH_FAILED: {}", error))?;

    if !output.status.success() {
        return Err(format!(
            "FOLDER_PICKER_FAILED: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let selected = String::from_utf8_lossy(&output.stdout).trim().to_string();

    if selected.is_empty() {
        Ok(None)
    } else {
        Ok(Some(selected))
    }
}

#[cfg(not(windows))]
fn pick_folder_windows(_current_root: &str, _description: &str) -> Result<Option<String>, String> {
    Err("FOLDER_PICKER_WINDOWS_ONLY".to_string())
}

#[tauri::command]
fn ray_pick_project_root(current_root: String) -> Result<Option<String>, String> {
    pick_folder_windows(&current_root, "Select RAY project root")
}

#[tauri::command]
fn forge_pick_folder(current_path: String, label: String) -> Result<Option<String>, String> {
    pick_folder_windows(&current_path, &label)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            ray_scan_project,
            ray_read_project_file,
            ray_pick_project_root,
            forge_apply::forge_apply_stage,
            forge_apply::forge_rollback_stage,
            forge_receiving_bay_fingerprint,
            forge_scan_receiving_bay,
            forge_stage_artifact,
            forge_pick_folder,
            openai_api::openai_api_status,
            openai_api::openai_api_send_relay
        ])
        .run(tauri::generate_context!())
        .expect("error while running Vertex Workstation");
}
