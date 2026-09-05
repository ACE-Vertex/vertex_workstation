import type {
  RayFile,
  RayFileContent,
  RayFinding,
  RayLexicalFacts,
  RayMode,
  RayScanResult,
} from "./models";

export const RAY_HANDOFF_SCHEMA = "ray-vera-handoff/1";

interface BuildRayHandoffInput {
  readonly mode: Exclude<RayMode, "IDLE">;
  readonly root: string;
  readonly scan: RayScanResult | null;
  readonly activeFile: RayFile;
  readonly source: RayFileContent;
  readonly facts: RayLexicalFacts;
  readonly findings: readonly RayFinding[];
  readonly targets: readonly RayFile[];
}

function lineList(values: readonly number[]): string {
  return values.length > 0 ? values.join(", ") : "NONE";
}

function targetLines(targets: readonly RayFile[]): string[] {
  if (targets.length === 0) return ["- NONE"];
  return targets.map(
    (file, index) =>
      `- ${index + 1}. ${file.relativePath} | ${file.provenance} | ${file.kind} | ${file.sizeBytes} bytes`,
  );
}

function factLines(
  title: string,
  facts: readonly { readonly line: number; readonly column: number; readonly kind: string; readonly name: string; readonly evidence: string }[],
  limit: number,
): string[] {
  const bounded = facts.slice(0, limit);
  if (bounded.length === 0) return [`${title}: NONE`];

  return [
    `${title}: ${facts.length}`,
    ...bounded.map(
      (fact) =>
        `- L${fact.line}:C${fact.column} [${fact.kind}] ${fact.name} :: ${fact.evidence}`,
    ),
    ...(facts.length > limit
      ? [`- ... ${facts.length - limit} more omitted from compact fact index`]
      : []),
  ];
}

function findingLines(findings: readonly RayFinding[]): string[] {
  if (findings.length === 0) return ["FINDINGS: NONE"];

  return [
    `FINDINGS: ${findings.length}`,
    ...findings.flatMap((finding, index) => [
      `- ${index + 1}. [${finding.severity}] ${finding.title}`,
      `  SOURCE: ${finding.source}${finding.lineStart ? `:L${finding.lineStart}` : ""}${finding.lineEnd && finding.lineEnd !== finding.lineStart ? `-L${finding.lineEnd}` : ""}`,
      `  FACT_KIND: ${finding.factKind ?? "unspecified"}`,
      `  CONFIDENCE: ${Math.round(finding.confidence * 100)}%`,
      `  EVIDENCE: ${finding.evidence}`,
    ]),
  ];
}

export function buildRayVeraHandoff({
  mode,
  root,
  scan,
  activeFile,
  source,
  facts,
  findings,
  targets,
}: BuildRayHandoffInput): string {
  const generatedAt = new Date().toISOString();

  return [
    "=== VERTEX WORKSTATION — RAY / VERA HANDOFF CAPSULE ===",
    `SCHEMA: ${RAY_HANDOFF_SCHEMA}`,
    `GENERATED_AT: ${generatedAt}`,
    `RAY_MODE: ${mode}`,
    "AUTHORITY: RAY_READ_ONLY_EVIDENCE",
    "MUTATION: NONE",
    "",
    "=== PROJECT SCOPE ===",
    `ROOT: ${root}`,
    `SCANNED_FILES: ${scan?.scannedCount ?? 0}`,
    `SKIPPED_FILES: ${scan?.skippedCount ?? 0}`,
    "",
    "=== ACTIVE TARGET ===",
    `PATH: ${activeFile.path}`,
    `RELATIVE_PATH: ${activeFile.relativePath}`,
    `PROVENANCE: ${activeFile.provenance}`,
    `KIND: ${activeFile.kind}`,
    `SIZE_BYTES: ${activeFile.sizeBytes}`,
    `MODIFIED_UNIX_MS: ${activeFile.modifiedUnixMs}`,
    `TEXT_CANDIDATE: ${activeFile.textCandidate}`,
    "",
    "=== SOURCE SIGHT ===",
    `ENCODING: ${source.encoding}`,
    `LINE_COUNT: ${source.lineCount}`,
    `SOURCE_SIZE_BYTES: ${source.sizeBytes}`,
    `SOURCE_TRUNCATED: ${source.truncated}`,
    "",
    "=== TARGET SET ===",
    ...targetLines(targets),
    "",
    "=== DETERMINISTIC FACT INDEX ===",
    ...factLines("IMPORT_USE_MOD_FACTS", facts.importFacts, 120),
    "",
    ...factLines("SYMBOL_FACTS", facts.symbolFacts, 240),
    "",
    `TODO_FIXME_HACK_LINES: ${lineList(facts.todoLines)}`,
    `EVENT_BINDING_LINES: ${lineList(facts.eventLines)}`,
    `DIRECT_DOM_MUTATION_LINES: ${lineList(facts.directDomMutationLines)}`,
    `CSS_FIXED_LINES: ${lineList(facts.cssFixedLines)}`,
    `CSS_Z_INDEX_LINES: ${lineList(facts.cssZIndexLines)}`,
    "",
    "=== EVIDENCE / FINDINGS ===",
    ...findingLines(findings),
    "",
    "=== VERA HANDOFF INSTRUCTION ===",
    "Treat this capsule as RAY-observed evidence from the selected local source.",
    "Use the exact file path and line coordinates when diagnosing or proposing a repair.",
    "Do not infer unobserved runtime behavior from source evidence alone.",
    "If a repair is requested and the evidence is sufficient, produce the next HUMAN_APPLY VRA.",
    "",
    "=== SOURCE SNAPSHOT BEGIN ===",
    source.content,
    "=== SOURCE SNAPSHOT END ===",
    "",
    "=== END VERTEX WORKSTATION — RAY / VERA HANDOFF CAPSULE ===",
  ].join("\n");
}
