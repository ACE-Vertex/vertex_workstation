use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    env,
    fs::{self, File},
    io::Read,
    path::{Component, Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct StageOperation {
    destination: String,
    sha256: String,
    verified_sha256: String,
    existed_before: bool,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct StageReport {
    stage_id: String,
    artifact_id: String,
    artifact_sha256: String,
    target_root: String,
    payload_count: usize,
    verified_count: usize,
    operations: Vec<StageOperation>,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ForgeApplyOperation {
    destination: String,
    existed_before: bool,
    backup_path: Option<String>,
    applied_sha256: String,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ForgeApplyResult {
    stage_id: String,
    artifact_id: String,
    artifact_sha256: String,
    target_root: String,
    backup_root: String,
    applied_count: usize,
    operations: Vec<ForgeApplyOperation>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct ForgeRollbackResult {
    stage_id: String,
    target_root: String,
    restored_count: usize,
    removed_count: usize,
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

fn unix_millis() -> Result<u128, String> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|value| value.as_millis())
        .map_err(|error| format!("CLOCK_ERROR: {}", error))
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

fn canonical_root(raw: &str, label: &str) -> Result<PathBuf, String> {
    let path = PathBuf::from(raw);
    let canonical = fs::canonicalize(&path).map_err(|error| {
        format!(
            "{}_CANONICALIZE_FAILED {}: {}",
            label,
            normalize_display(&path),
            error
        )
    })?;
    if !canonical.is_dir() {
        return Err(format!(
            "{}_NOT_DIRECTORY: {}",
            label,
            normalize_display(&canonical)
        ));
    }
    Ok(canonical)
}

fn safe_relative_path(value: &str, label: &str) -> Result<PathBuf, String> {
    let path = Path::new(value);
    if path.as_os_str().is_empty() {
        return Err(format!("{}_EMPTY", label));
    }
    if path.is_absolute() {
        return Err(format!("{}_ABSOLUTE_BLOCKED: {}", label, value));
    }

    let mut safe = PathBuf::new();
    for component in path.components() {
        match component {
            Component::Normal(value) => safe.push(value),
            Component::CurDir => {}
            Component::ParentDir | Component::RootDir | Component::Prefix(_) => {
                return Err(format!("{}_TRAVERSAL_BLOCKED: {}", label, value));
            }
        }
    }

    if safe.as_os_str().is_empty() {
        return Err(format!("{}_EMPTY", label));
    }
    Ok(safe)
}

fn safe_stage_id(value: &str) -> Result<String, String> {
    let relative = safe_relative_path(value, "APPLY_STAGE_ID")?;
    if relative.components().count() != 1 {
        return Err(format!("APPLY_STAGE_ID_INVALID: {}", value));
    }
    Ok(relative.to_string_lossy().to_string())
}

fn sha256_file(path: &Path) -> Result<String, String> {
    let mut file = File::open(path)
        .map_err(|error| format!("SHA256_OPEN_FAILED {}: {}", normalize_display(path), error))?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 1024 * 1024];
    loop {
        let read = file.read(&mut buffer).map_err(|error| {
            format!("SHA256_READ_FAILED {}: {}", normalize_display(path), error)
        })?;
        if read == 0 {
            break;
        }
        hasher.update(&buffer[..read]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn read_stage_report(stage_root: &Path) -> Result<StageReport, String> {
    let report_path = stage_root.join("stage_report.json");
    let text = fs::read_to_string(&report_path).map_err(|error| {
        format!(
            "APPLY_STAGE_REPORT_READ_FAILED {}: {}",
            normalize_display(&report_path),
            error
        )
    })?;
    serde_json::from_str(&text).map_err(|error| format!("APPLY_STAGE_REPORT_INVALID: {}", error))
}

fn verify_human_gate(stage_root: &Path) -> Result<(), String> {
    let lock_path = stage_root.join("STAGE_LOCK");
    let lock = fs::read_to_string(&lock_path).map_err(|error| {
        format!(
            "APPLY_STAGE_LOCK_READ_FAILED {}: {}",
            normalize_display(&lock_path),
            error
        )
    })?;
    if !lock
        .lines()
        .any(|line| line.trim() == "authority=HUMAN_APPLY")
    {
        return Err("APPLY_HUMAN_GATE_MISSING".to_string());
    }
    if !lock.lines().any(|line| line.trim() == "target_mutation=NO") {
        return Err("APPLY_STAGE_LOCK_INVALID".to_string());
    }
    Ok(())
}

fn ensure_no_symlink_components(root: &Path, relative: &Path, label: &str) -> Result<(), String> {
    let mut current = root.to_path_buf();
    for component in relative.components() {
        let Component::Normal(value) = component else {
            continue;
        };
        current.push(value);
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                return Err(format!(
                    "{}_SYMLINK_BLOCKED: {}",
                    label,
                    normalize_display(&current)
                ));
            }
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => {
                return Err(format!(
                    "{}_METADATA_FAILED {}: {}",
                    label,
                    normalize_display(&current),
                    error
                ));
            }
        }
    }
    Ok(())
}

fn copy_and_sync(source: &Path, destination: &Path, label: &str) -> Result<(), String> {
    if let Some(parent) = destination.parent() {
        fs::create_dir_all(parent).map_err(|error| {
            format!(
                "{}_PARENT_CREATE_FAILED {}: {}",
                label,
                normalize_display(parent),
                error
            )
        })?;
    }

    fs::copy(source, destination).map_err(|error| {
        format!(
            "{}_COPY_FAILED {} -> {}: {}",
            label,
            normalize_display(source),
            normalize_display(destination),
            error
        )
    })?;

    File::open(destination)
        .and_then(|file| file.sync_all())
        .map_err(|error| {
            format!(
                "{}_SYNC_FAILED {}: {}",
                label,
                normalize_display(destination),
                error
            )
        })?;
    Ok(())
}

fn restore_operations(
    target_root: &Path,
    backup_root: &Path,
    operations: &[StageOperation],
) -> Result<(usize, usize), String> {
    let mut restored = 0usize;
    let mut removed = 0usize;

    for operation in operations.iter().rev() {
        let relative = safe_relative_path(&operation.destination, "ROLLBACK_DESTINATION")?;
        ensure_no_symlink_components(target_root, &relative, "ROLLBACK_TARGET")?;

        let target_path = target_root.join(&relative);
        let backup_path = backup_root.join(&relative);

        if operation.existed_before {
            if !backup_path.is_file() {
                return Err(format!(
                    "ROLLBACK_BACKUP_MISSING: {}",
                    normalize_display(&backup_path)
                ));
            }
            copy_and_sync(&backup_path, &target_path, "ROLLBACK_RESTORE")?;
            restored += 1;
        } else if target_path.exists() {
            let metadata = fs::symlink_metadata(&target_path).map_err(|error| {
                format!(
                    "ROLLBACK_TARGET_METADATA_FAILED {}: {}",
                    normalize_display(&target_path),
                    error
                )
            })?;
            if metadata.file_type().is_symlink() || !metadata.is_file() {
                return Err(format!(
                    "ROLLBACK_REMOVE_UNSAFE_TARGET: {}",
                    normalize_display(&target_path)
                ));
            }
            fs::remove_file(&target_path).map_err(|error| {
                format!(
                    "ROLLBACK_REMOVE_NEW_FAILED {}: {}",
                    normalize_display(&target_path),
                    error
                )
            })?;
            removed += 1;
        }
    }

    Ok((restored, removed))
}

#[tauri::command]
pub(crate) fn forge_apply_stage(
    stage_id: String,
    production_root: String,
) -> Result<ForgeApplyResult, String> {
    let stage_id = safe_stage_id(&stage_id)?;
    let production = canonical_root(&production_root, "APPLY_PRODUCTION_ROOT")?;

    let stage_base = stage_base_root()?;
    let stage_root_raw = stage_base.join(&stage_id);
    let stage_root = fs::canonicalize(&stage_root_raw).map_err(|error| {
        format!(
            "APPLY_STAGE_ROOT_MISSING {}: {}",
            normalize_display(&stage_root_raw),
            error
        )
    })?;

    let canonical_stage_base = fs::canonicalize(&stage_base)
        .map_err(|error| format!("APPLY_STAGE_BASE_CANONICALIZE_FAILED: {}", error))?;
    if !stage_root.starts_with(&canonical_stage_base) {
        return Err("APPLY_STAGE_OUTSIDE_STAGE_ROOT".to_string());
    }

    verify_human_gate(&stage_root)?;

    if stage_root.join("APPLY_LOCK").exists() {
        return Err("APPLY_ALREADY_COMPLETED".to_string());
    }
    if stage_root.join("ROLLBACK_LOCK").exists() {
        return Err("APPLY_STAGE_ALREADY_ROLLED_BACK_RESTAGE_REQUIRED".to_string());
    }

    let report = read_stage_report(&stage_root)?;
    if report.stage_id != stage_id {
        return Err("APPLY_STAGE_ID_MISMATCH".to_string());
    }
    if report.payload_count != report.operations.len()
        || report.verified_count != report.operations.len()
    {
        return Err("APPLY_STAGE_REPORT_COUNT_MISMATCH".to_string());
    }

    let target = canonical_root(&report.target_root, "APPLY_TARGET_ROOT")?;
    if !target.starts_with(&production) {
        return Err("APPLY_TARGET_OUTSIDE_AUTHORIZED_ROOT".to_string());
    }

    let artifact_path = stage_root.join("artifact.vra");
    let artifact_sha = sha256_file(&artifact_path)?;
    if artifact_sha != report.artifact_sha256 {
        return Err(format!(
            "APPLY_ARTIFACT_SHA256_MISMATCH expected={} actual={}",
            report.artifact_sha256, artifact_sha
        ));
    }

    let staged_files_root = stage_root.join("files");
    if !staged_files_root.is_dir() {
        return Err("APPLY_STAGED_FILES_ROOT_MISSING".to_string());
    }

    // Preflight all paths and hashes before target mutation.
    for operation in &report.operations {
        let relative = safe_relative_path(&operation.destination, "APPLY_DESTINATION")?;
        ensure_no_symlink_components(&target, &relative, "APPLY_TARGET")?;

        let staged_path = staged_files_root.join(&relative);
        if !staged_path.is_file() {
            return Err(format!(
                "APPLY_STAGED_FILE_MISSING: {}",
                normalize_display(&staged_path)
            ));
        }

        let staged_sha = sha256_file(&staged_path)?;
        let expected = if operation.verified_sha256.is_empty() {
            &operation.sha256
        } else {
            &operation.verified_sha256
        };
        if staged_sha != expected.as_str() {
            return Err(format!(
                "APPLY_STAGED_SHA256_MISMATCH {} expected={} actual={}",
                operation.destination, expected, staged_sha
            ));
        }

        let target_path = target.join(&relative);
        match fs::symlink_metadata(&target_path) {
            Ok(metadata) => {
                if metadata.file_type().is_symlink() || !metadata.is_file() {
                    return Err(format!(
                        "APPLY_TARGET_NOT_REGULAR_FILE: {}",
                        normalize_display(&target_path)
                    ));
                }
                if !operation.existed_before {
                    return Err(format!(
                        "APPLY_TARGET_STATE_DRIFT_NEW_NOW_EXISTS: {}",
                        operation.destination
                    ));
                }
            }
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                if operation.existed_before {
                    return Err(format!(
                        "APPLY_TARGET_STATE_DRIFT_EXISTING_NOW_MISSING: {}",
                        operation.destination
                    ));
                }
            }
            Err(error) => {
                return Err(format!(
                    "APPLY_TARGET_METADATA_FAILED {}: {}",
                    normalize_display(&target_path),
                    error
                ));
            }
        }
    }

    let backup_root = backup_base_root()?.join(&stage_id);
    if backup_root.exists() {
        return Err(format!(
            "APPLY_BACKUP_ROOT_ALREADY_EXISTS: {}",
            normalize_display(&backup_root)
        ));
    }
    fs::create_dir_all(&backup_root)
        .map_err(|error| format!("APPLY_BACKUP_ROOT_CREATE_FAILED: {}", error))?;

    // Backup every pre-existing target before changing any target.
    for operation in &report.operations {
        if !operation.existed_before {
            continue;
        }
        let relative = safe_relative_path(&operation.destination, "APPLY_BACKUP_DESTINATION")?;
        let target_path = target.join(&relative);
        let backup_path = backup_root.join(&relative);
        copy_and_sync(&target_path, &backup_path, "APPLY_BACKUP")?;
    }

    let mut applied: Vec<StageOperation> = Vec::new();
    let mut apply_operations = Vec::new();

    for operation in &report.operations {
        let relative = safe_relative_path(&operation.destination, "APPLY_DESTINATION")?;
        let staged_path = staged_files_root.join(&relative);
        let target_path = target.join(&relative);
        let temp_name = format!(
            ".vertex-apply-{}-{}.tmp",
            target_path
                .file_name()
                .and_then(|value| value.to_str())
                .unwrap_or("payload"),
            unix_millis()?
        );
        let temp_path = target_path.parent().unwrap_or(&target).join(temp_name);

        applied.push(operation.clone());

        let step = (|| -> Result<String, String> {
            copy_and_sync(&staged_path, &temp_path, "APPLY_TEMP")?;
            let temp_sha = sha256_file(&temp_path)?;
            let expected = if operation.verified_sha256.is_empty() {
                &operation.sha256
            } else {
                &operation.verified_sha256
            };
            if temp_sha != expected.as_str() {
                let _ = fs::remove_file(&temp_path);
                return Err(format!(
                    "APPLY_TEMP_SHA256_MISMATCH {} expected={} actual={}",
                    operation.destination, expected, temp_sha
                ));
            }

            if target_path.exists() {
                fs::remove_file(&target_path).map_err(|error| {
                    format!(
                        "APPLY_TARGET_REMOVE_FAILED {}: {}",
                        normalize_display(&target_path),
                        error
                    )
                })?;
            }

            fs::rename(&temp_path, &target_path).map_err(|error| {
                let _ = fs::remove_file(&temp_path);
                format!(
                    "APPLY_TARGET_RENAME_FAILED {}: {}",
                    normalize_display(&target_path),
                    error
                )
            })?;

            let applied_sha = sha256_file(&target_path)?;
            if applied_sha != expected.as_str() {
                return Err(format!(
                    "APPLY_TARGET_SHA256_MISMATCH {} expected={} actual={}",
                    operation.destination, expected, applied_sha
                ));
            }

            Ok(applied_sha)
        })();

        match step {
            Ok(applied_sha) => {
                apply_operations.push(ForgeApplyOperation {
                    destination: operation.destination.clone(),
                    existed_before: operation.existed_before,
                    backup_path: if operation.existed_before {
                        Some(normalize_display(&backup_root.join(&relative)))
                    } else {
                        None
                    },
                    applied_sha256: applied_sha,
                });
            }
            Err(error) => {
                let rollback_result = restore_operations(&target, &backup_root, &applied);
                let rollback_note = match rollback_result {
                    Ok((restored, removed)) => format!(
                        "AUTO_RESTORE_PASS restored={} removed={}",
                        restored, removed
                    ),
                    Err(rollback_error) => format!("AUTO_RESTORE_FAIL {}", rollback_error),
                };
                return Err(format!("{}; {}", error, rollback_note));
            }
        }
    }

    let result = ForgeApplyResult {
        stage_id: stage_id.clone(),
        artifact_id: report.artifact_id,
        artifact_sha256: report.artifact_sha256,
        target_root: normalize_display(&target),
        backup_root: normalize_display(&backup_root),
        applied_count: apply_operations.len(),
        operations: apply_operations,
    };

    let report_bytes = serde_json::to_vec_pretty(&result)
        .map_err(|error| format!("APPLY_REPORT_SERIALIZE_FAILED: {}", error))?;
    fs::write(stage_root.join("apply_report.json"), report_bytes)
        .map_err(|error| format!("APPLY_REPORT_WRITE_FAILED: {}", error))?;
    fs::write(
        stage_root.join("APPLY_LOCK"),
        format!(
            "stage_id={}\napplied_count={}\ntarget={}\nhuman_gate=APPLY_CLICK\n",
            result.stage_id, result.applied_count, result.target_root
        ),
    )
    .map_err(|error| format!("APPLY_LOCK_WRITE_FAILED: {}", error))?;

    Ok(result)
}

#[tauri::command]
pub(crate) fn forge_rollback_stage(
    stage_id: String,
    production_root: String,
) -> Result<ForgeRollbackResult, String> {
    let stage_id = safe_stage_id(&stage_id)?;
    let production = canonical_root(&production_root, "ROLLBACK_PRODUCTION_ROOT")?;
    let stage_base = stage_base_root()?;
    let stage_root_raw = stage_base.join(&stage_id);
    let stage_root = fs::canonicalize(&stage_root_raw).map_err(|error| {
        format!(
            "ROLLBACK_STAGE_ROOT_MISSING {}: {}",
            normalize_display(&stage_root_raw),
            error
        )
    })?;

    let canonical_stage_base = fs::canonicalize(&stage_base)
        .map_err(|error| format!("ROLLBACK_STAGE_BASE_CANONICALIZE_FAILED: {}", error))?;
    if !stage_root.starts_with(&canonical_stage_base) {
        return Err("ROLLBACK_STAGE_OUTSIDE_STAGE_ROOT".to_string());
    }

    if !stage_root.join("APPLY_LOCK").is_file() {
        return Err("ROLLBACK_APPLY_LOCK_MISSING".to_string());
    }
    if stage_root.join("ROLLBACK_LOCK").exists() {
        return Err("ROLLBACK_ALREADY_COMPLETED".to_string());
    }

    let report = read_stage_report(&stage_root)?;
    if report.stage_id != stage_id {
        return Err("ROLLBACK_STAGE_ID_MISMATCH".to_string());
    }

    let apply_report_path = stage_root.join("apply_report.json");
    let apply_report_text = fs::read_to_string(&apply_report_path).map_err(|error| {
        format!(
            "ROLLBACK_APPLY_REPORT_READ_FAILED {}: {}",
            normalize_display(&apply_report_path),
            error
        )
    })?;
    let apply_report: ForgeApplyResult = serde_json::from_str(&apply_report_text)
        .map_err(|error| format!("ROLLBACK_APPLY_REPORT_INVALID: {}", error))?;
    if apply_report.stage_id != stage_id {
        return Err("ROLLBACK_APPLY_REPORT_STAGE_ID_MISMATCH".to_string());
    }

    let target = canonical_root(&report.target_root, "ROLLBACK_TARGET_ROOT")?;
    if !target.starts_with(&production) {
        return Err("ROLLBACK_TARGET_OUTSIDE_AUTHORIZED_ROOT".to_string());
    }

    let backup_root = backup_base_root()?.join(&stage_id);
    if !backup_root.is_dir() {
        return Err("ROLLBACK_BACKUP_ROOT_MISSING".to_string());
    }

    // Do not overwrite post-APPLY edits. Rollback is allowed only while every
    // current target still matches the exact bytes written by this APPLY.
    for operation in &apply_report.operations {
        let relative =
            safe_relative_path(&operation.destination, "ROLLBACK_PREFLIGHT_DESTINATION")?;
        ensure_no_symlink_components(&target, &relative, "ROLLBACK_PREFLIGHT_TARGET")?;
        let target_path = target.join(&relative);
        if !target_path.is_file() {
            return Err(format!(
                "ROLLBACK_TARGET_DRIFT_MISSING: {}",
                normalize_display(&target_path)
            ));
        }
        let current_sha = sha256_file(&target_path)?;
        if current_sha != operation.applied_sha256 {
            return Err(format!(
                "ROLLBACK_TARGET_DRIFT_SHA256: {} expected={} actual={}",
                operation.destination, operation.applied_sha256, current_sha
            ));
        }
    }

    let (restored_count, removed_count) =
        restore_operations(&target, &backup_root, &report.operations)?;

    let result = ForgeRollbackResult {
        stage_id: stage_id.clone(),
        target_root: normalize_display(&target),
        restored_count,
        removed_count,
    };

    let report_bytes = serde_json::to_vec_pretty(&result)
        .map_err(|error| format!("ROLLBACK_REPORT_SERIALIZE_FAILED: {}", error))?;
    fs::write(stage_root.join("rollback_report.json"), report_bytes)
        .map_err(|error| format!("ROLLBACK_REPORT_WRITE_FAILED: {}", error))?;
    fs::write(
        stage_root.join("ROLLBACK_LOCK"),
        format!(
            "stage_id={}\nrestored={}\nremoved={}\n",
            result.stage_id, result.restored_count, result.removed_count
        ),
    )
    .map_err(|error| format!("ROLLBACK_LOCK_WRITE_FAILED: {}", error))?;

    Ok(result)
}
