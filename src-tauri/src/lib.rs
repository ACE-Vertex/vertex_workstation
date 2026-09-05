use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct HostHealth {
    host_id: &'static str,
    status: &'static str,
    architecture: &'static str,
    welded_dependency: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct UnitDescriptor {
    id: &'static str,
    authority: &'static str,
    detachable: bool,
    host_neutral: bool,
}

#[tauri::command]
fn host_health() -> HostHealth {
    HostHealth {
        host_id: "vertex-workstation",
        status: "FOUNDATION",
        architecture: "UNIT_METHOD",
        welded_dependency: false,
    }
}

#[tauri::command]
fn list_units() -> Vec<UnitDescriptor> {
    vec![
        UnitDescriptor {
            id: "ray",
            authority: "READ_ONLY",
            detachable: true,
            host_neutral: true,
        },
        UnitDescriptor {
            id: "forge",
            authority: "HUMAN_APPLY",
            detachable: true,
            host_neutral: true,
        },
    ]
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![host_health, list_units])
        .run(tauri::generate_context!())
        .expect("error while running Vertex Workstation");
}
