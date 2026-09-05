import type { RayFile, RayLineFact } from "./models";

export type RayTreeNodeKind = "folder" | "file" | "symbol";

export interface RayTreeNode {
  readonly id: string;
  readonly name: string;
  readonly kind: RayTreeNodeKind;
  readonly searchText: string;
  readonly relativePath?: string;
  readonly provenance?: RayFile["provenance"];
  readonly fileKind?: string;
  readonly fileId?: string;
  readonly line?: number;
  readonly column?: number;
  readonly symbolKind?: string;
  readonly targetable: boolean;
  readonly children?: readonly RayTreeNode[];
}

interface MutableFolder {
  id: string;
  name: string;
  relativePath: string;
  folders: Map<string, MutableFolder>;
  files: RayFile[];
}

function cleanParts(relativePath: string): string[] {
  return relativePath
    .split(/[\\/]+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function folderId(relativePath: string): string {
  return `dir:${relativePath.replaceAll("\\", "/").toLowerCase()}`;
}

function createFolder(name: string, relativePath: string): MutableFolder {
  return {
    id: folderId(relativePath),
    name,
    relativePath,
    folders: new Map(),
    files: [],
  };
}

function symbolNodes(
  file: RayFile,
  activeFileId: string | null,
  facts: readonly RayLineFact[],
): readonly RayTreeNode[] | undefined {
  if (file.id !== activeFileId || facts.length === 0) return undefined;

  return facts.slice(0, 180).map((fact, index) => ({
    id: `symbol:${file.id}:${fact.line}:${fact.column}:${index}:${fact.name}`,
    name: fact.name,
    kind: "symbol",
    searchText: `${fact.name} ${fact.kind} ${file.relativePath} L${fact.line}`.toLowerCase(),
    relativePath: file.relativePath,
    fileId: file.id,
    line: fact.line,
    column: fact.column,
    symbolKind: fact.kind,
    targetable: false,
  }));
}

function materialize(
  folder: MutableFolder,
  activeFileId: string | null,
  facts: readonly RayLineFact[],
): readonly RayTreeNode[] {
  const folders = [...folder.folders.values()]
    .sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" }))
    .map<RayTreeNode>((child) => ({
      id: child.id,
      name: child.name,
      kind: "folder",
      searchText: `${child.name} ${child.relativePath}`.toLowerCase(),
      relativePath: child.relativePath,
      targetable: false,
      children: materialize(child, activeFileId, facts),
    }));

  const files = [...folder.files]
    .sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" }))
    .map<RayTreeNode>((file) => ({
      id: file.id,
      name: file.name,
      kind: "file",
      searchText: `${file.name} ${file.relativePath} ${file.provenance} ${file.kind}`.toLowerCase(),
      relativePath: file.relativePath,
      provenance: file.provenance,
      fileKind: file.kind,
      fileId: file.id,
      targetable: true,
      children: symbolNodes(file, activeFileId, facts),
    }));

  return [...folders, ...files];
}

export function buildRayProjectTree(
  files: readonly RayFile[],
  activeFileId: string | null,
  symbolFacts: readonly RayLineFact[],
): readonly RayTreeNode[] {
  const root = createFolder("", "");

  for (const file of files) {
    const parts = cleanParts(file.relativePath);
    if (parts.length === 0) {
      root.files.push(file);
      continue;
    }

    let cursor = root;
    const folders = parts.slice(0, -1);
    const pathParts: string[] = [];

    for (const part of folders) {
      pathParts.push(part);
      const relativePath = pathParts.join("\\");
      let next = cursor.folders.get(part.toLowerCase());
      if (!next) {
        next = createFolder(part, relativePath);
        cursor.folders.set(part.toLowerCase(), next);
      }
      cursor = next;
    }

    cursor.files.push(file);
  }

  return materialize(root, activeFileId, symbolFacts);
}

export function countRayTreeNodes(nodes: readonly RayTreeNode[]): number {
  let count = 0;
  for (const node of nodes) {
    count += 1;
    if (node.children) count += countRayTreeNodes(node.children);
  }
  return count;
}
