# Vertex Workstation — RAY Project Selection + File Sight 000005

## Mission

Turn RAY NEXT from a fixed Workstation demo target into a real project observer.

000005 adds two foundational capabilities:

1. switchable project roots
2. actual file-content sight through the Tauri/Rust filesystem boundary

## Project selection

RAY now provides a docked Project Root control:

- editable path
- LOAD ROOT
- BROWSE
- recent roots

Successful roots are stored in local browser/WebView storage and offered as
recent choices.

The BROWSE action uses a transient Windows folder selection dialog. Persistent
RAY tools remain docked; the no-floating-window rule is unchanged.

## Real filesystem sight

Rust commands:

- `ray_scan_project`
- `ray_read_project_file`
- `ray_pick_project_root`

RAY scans the selected project and returns actual files and metadata to React.

The active file can be opened in the docked **Source Viewer**, with line numbers
and a bounded text preview.

Safety / performance bounds:

- maximum scan: 20,000 files
- maximum recursion depth: 64
- source preview: 512 KiB
- symlink directories are not followed
- requested source files must canonicalize inside the selected project root
- binary preview is blocked

Heavy generated/vendor roots are intentionally skipped in this pass:

- `.git`
- `node_modules`
- `target`
- `dist`
- `build`
- `builds`
- `versions`
- cache/IDE folders

Skipped path count is reported to the cockpit.

## Precision pass 1

The active source is now inspected deterministically for lexical evidence:

- import / export-from / use / mod clues
- function/class/interface/type/enum/struct/trait/const/fn symbol clues
- TODO/FIXME/HACK markers
- event-binding tokens
- imperative DOM mutation calls
- CSS `position: fixed`
- CSS `z-index`

QUICK RAY and DEEP RAY therefore operate on the actual selected file content,
not hard-coded demo evidence.

This is intentionally labelled lexical/deterministic. It is NOT yet an AST,
call graph, CSS influence graph, or cross-file ownership graph.

Those deeper precision layers are the next RAY passes.

## Layout

Persistent UI remains fixed:

Top:
- Project Tree
- Source Viewer
- Inspector

Bottom:
- Target Set
- Evidence / Findings

No persistent float windows.

No mutation of legacy `vertex_works`.
