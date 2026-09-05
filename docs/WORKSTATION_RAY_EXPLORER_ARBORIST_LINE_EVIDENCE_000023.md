# Vertex Workstation — RAY Explorer / Arborist Line Evidence 000023

## Mission

Raise RAY precision before Workstation operational use.

This pass replaces the flat file list presentation with a real hierarchical
RAY Explorer while keeping filesystem authority outside the tree component.

## Architecture

`Tauri/Rust filesystem facts`
→ `RayFile[]`
→ `Ray Project Model`
→ `RayTreeNode[]`
→ `react-arborist`
→ `RAY Explorer Presentation Port`

`react-arborist` does not own filesystem state and cannot mutate files.

Tree editing, drag and drop, and rename are explicitly disabled.

## Explorer structure

RAY now derives:

`Project`
→ `Folder`
→ `File`
→ `Symbol`

Folders are reconstructed deterministically from the real relative paths
returned by the existing Tauri/Rust scan.

The active source file exposes line-aware symbol children.

## Precision pass

The lexical layer now preserves deterministic source coordinates:

- symbol name / kind / line / column / evidence text
- import/use/mod clue / line / evidence text
- TODO/FIXME/HACK lines
- event-binding lines
- imperative DOM mutation lines
- CSS fixed/z-index lines

Findings carry source line coordinates.

Evidence can REVEAL the supporting line directly in Source Viewer.

The selected line is highlighted and scrolled into view.

This does not pretend to be AST truth yet. It is a higher-precision,
line-addressable deterministic lexical layer that becomes Evidence for later
AST / dependency / ownership passes.

## react-arborist

Pinned dependency: `react-arborist 3.16.0`.

Used only for:
- virtualized tree rendering
- open/close hierarchy
- keyboard navigation
- filtering
- selection synchronization
- node activation

No runtime network dependency is introduced.

The dependency apply helper creates package-file backups before one-time npm
installation and restores package files if installation fails.

## Runtime acceptance

1. Launch the immutable candidate.
2. Open RAY.
3. Confirm folders/files display as a hierarchy rather than a flat list.
4. Filter by a nested file name; parents must remain visible.
5. Select a file; Source Viewer must load it.
6. Run QUICK RAY or DEEP RAY.
7. Expand the active source file; symbol children with line numbers must appear.
8. Activate a symbol; Source Viewer must reveal/highlight its exact line.
9. Use REVEAL Lxx on an Evidence row; Source Viewer must reveal the evidence line.
10. Keyboard navigation must work inside the tree.
11. No rename/drag/drop filesystem mutation is allowed.

Do not call RAY Runtime GREEN until these are visually observed.
