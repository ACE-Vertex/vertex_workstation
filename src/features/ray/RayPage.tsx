import { useEffect, useMemo, useState } from "react";
import { OperationIndicator } from "../../shell/OperationIndicator";
import { ProcessingGridDistortion } from "../../shell/ProcessingGridDistortion";
import "../../shell/operationIndicator.css";
import "../../shell/processingGridDistortion.css";
import "./rayProcessing.css";
import { buildFindings, inspectLexically } from "./rayAnalysis";
import { buildRayVeraHandoff } from "./rayHandoff";
import {
  isTauriRuntime,
  pickProjectRoot,
  readProjectFile,
  scanProject,
} from "./rayApi";
import { RayEvidence } from "./RayEvidence";
import { RayInspector } from "./RayInspector";
import { RayProjectRootBar } from "./RayProjectRootBar";
import { RayProjectTree } from "./RayProjectTree";
import { RaySourceViewer } from "./RaySourceViewer";
import { RayTargetSet } from "./RayTargetSet";
import type {
  RayFile,
  RayFileContent,
  RayMode,
  RayRuntimeState,
  RayScanResult,
} from "./models";

const DEFAULT_ROOT = String.raw`G:\Vertex_Project\Development\vertex_workstation`;
const RECENT_KEY = "vertex.ray.recentRoots.v1";

type OperationPhase = "PROJECT SCAN" | "FILE READ";
type RayClipState = "READY" | "CLIPPING" | "COPIED" | "FAILED";

interface RayOperation {
  readonly phase: OperationPhase;
  readonly detail: string;
  readonly startedAt: number;
}

function readRecentRoots(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed)
      ? parsed.filter((value): value is string => typeof value === "string").slice(0, 8)
      : [];
  } catch {
    return [];
  }
}

function writeRecentRoots(roots: readonly string[]) {
  try {
    localStorage.setItem(RECENT_KEY, JSON.stringify(roots.slice(0, 8)));
  } catch {
    // Local persistence is a convenience only.
  }
}

export function RayPage() {
  const tauriAvailable = isTauriRuntime();

  const [root, setRoot] = useState(DEFAULT_ROOT);
  const [rootDraft, setRootDraft] = useState(DEFAULT_ROOT);
  const [recentRoots, setRecentRoots] = useState<string[]>(readRecentRoots);
  const [scan, setScan] = useState<RayScanResult | null>(null);
  const [runtimeState, setRuntimeState] = useState<RayRuntimeState>("READY");
  const [runtimeError, setRuntimeError] = useState<string | null>(null);
  const [operation, setOperation] = useState<RayOperation | null>(null);

  const [activeId, setActiveId] = useState<string | null>(null);
  const [targetOrder, setTargetOrder] = useState<string[]>([]);
  const [locked, setLocked] = useState(false);
  const [mode, setMode] = useState<RayMode>("IDLE");

  const [source, setSource] = useState<RayFileContent | null>(null);
  const [sourceError, setSourceError] = useState<string | null>(null);
  const [focusLine, setFocusLine] = useState<number | null>(null);
  const [clipState, setClipState] = useState<RayClipState>("READY");
  const [clipBytes, setClipBytes] = useState(0);

  const files = scan?.files ?? [];

  const fileById = useMemo(
    () => new Map(files.map((file) => [file.id, file])),
    [files],
  );

  const targetIds = useMemo(
    () => new Set(targetOrder),
    [targetOrder],
  );

  const targets = useMemo(
    () =>
      targetOrder
        .map((id) => fileById.get(id))
        .filter((file): file is RayFile => Boolean(file)),
    [targetOrder, fileById],
  );

  const activeFile = activeId ? fileById.get(activeId) : undefined;
  const facts = useMemo(() => inspectLexically(source), [source]);
  const findings = useMemo(
    () => buildFindings(source, facts, mode),
    [source, facts, mode],
  );

  async function loadRoot(nextRoot: string) {
    const clean = nextRoot.trim();
    if (!clean) return;

    if (!tauriAvailable) {
      setRuntimeState("READY");
      setRuntimeError("LOCAL UI PREVIEW — RAY FILESYSTEM REQUIRES TAURI RUNTIME");
      setOperation(null);
      return;
    }

    setRuntimeState("SCANNING");
    setRuntimeError(null);
    setOperation({
      phase: "PROJECT SCAN",
      detail: clean,
      startedAt: Date.now(),
    });
    setMode("IDLE");
    setLocked(false);
    setTargetOrder([]);
    setActiveId(null);
    setSource(null);
    setSourceError(null);
    setFocusLine(null);
    setClipState("READY");
    setClipBytes(0);

    try {
      const result = await scanProject(clean);
      setScan(result);
      setRoot(result.root);
      setRootDraft(result.root);

      const nextRecent = [
        result.root,
        ...recentRoots.filter((item) => item.toLowerCase() !== result.root.toLowerCase()),
      ].slice(0, 8);
      setRecentRoots(nextRecent);
      writeRecentRoots(nextRecent);

      const firstText = result.files.find((file) => file.textCandidate);
      setActiveId(firstText?.id ?? result.files[0]?.id ?? null);
      setRuntimeState("READY");
    } catch (error) {
      setScan(null);
      setRuntimeState("ERROR");
      setRuntimeError(error instanceof Error ? error.message : String(error));
    } finally {
      setOperation(null);
    }
  }

  async function browseRoot() {
    if (!tauriAvailable) {
      setRuntimeState("READY");
      setRuntimeError("LOCAL UI PREVIEW — BROWSE REQUIRES TAURI RUNTIME");
      return;
    }

    setRuntimeError(null);
    try {
      const selected = await pickProjectRoot(rootDraft);
      if (selected) {
        setRootDraft(selected);
        await loadRoot(selected);
      }
    } catch (error) {
      setRuntimeState("ERROR");
      setRuntimeError(error instanceof Error ? error.message : String(error));
    }
  }

  function toggleTarget(id: string) {
    if (locked) return;

    setTargetOrder((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );
  }

  async function copyRayToClipboard(nextMode: "QUICK" | "DEEP") {
    if (!activeFile || !source) return;

    const nextFindings = buildFindings(source, facts, nextMode);
    const capsule = buildRayVeraHandoff({
      mode: nextMode,
      root,
      scan,
      activeFile,
      source,
      facts,
      findings: nextFindings,
      targets,
    });

    setClipState("CLIPPING");
    setClipBytes(new Blob([capsule]).size);

    try {
      await navigator.clipboard.writeText(capsule);
      setClipState("COPIED");
    } catch (error) {
      setClipState("FAILED");
      setRuntimeError(
        error instanceof Error
          ? `RAY CLIPBOARD FAILED: ${error.message}`
          : "RAY CLIPBOARD FAILED",
      );
    }
  }

  function runQuickRay() {
    setMode("QUICK");
  }

  function runDeepRay() {
    setMode("DEEP");
    void copyRayToClipboard("DEEP");
  }

  function copyCurrentRay() {
    const nextMode = mode === "QUICK" ? "QUICK" : "DEEP";
    if (mode === "IDLE") setMode(nextMode);
    void copyRayToClipboard(nextMode);
  }

  useEffect(() => {
    if (!tauriAvailable) {
      setRuntimeState("READY");
      setRuntimeError("LOCAL UI PREVIEW — RAY FILESYSTEM REQUIRES TAURI RUNTIME");
      return;
    }

    void loadRoot(DEFAULT_ROOT);
    // Initial RAY boot scans the canonical Workstation project in Tauri runtime.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tauriAvailable]);

  useEffect(() => {
    if (!tauriAvailable || !activeFile) {
      setSource(null);
      setSourceError(null);
      return;
    }

    if (!activeFile.textCandidate) {
      setSource(null);
      setSourceError(null);
      return;
    }

    let cancelled = false;
    setFocusLine(null);
    setRuntimeState("READING");
    setOperation({
      phase: "FILE READ",
      detail: activeFile.relativePath,
      startedAt: Date.now(),
    });
    setSource(null);
    setSourceError(null);

    void readProjectFile(root, activeFile.path)
      .then((result) => {
        if (cancelled) return;
        setSource(result);
        setRuntimeState("READY");
      })
      .catch((error) => {
        if (cancelled) return;
        setSource(null);
        setSourceError(error instanceof Error ? error.message : String(error));
        setRuntimeState("ERROR");
      })
      .finally(() => {
        if (!cancelled) setOperation(null);
      });

    return () => {
      cancelled = true;
    };
  }, [tauriAvailable, root, activeFile]);

  const busy = runtimeState === "SCANNING" || runtimeState === "READING";

  return (
    <main className={`ray-page ${operation ? "ray-processing" : ""}`}>
      <ProcessingGridDistortion active={Boolean(operation)} />

      <header className="ray-hero">
        <div>
          <span>SOFTWARE OBSERVATION · TARGETING · EVIDENCE</span>
          <h1>RAY <strong>NEXT</strong></h1>
          <p>照準器 + 顕微鏡 + CT + 証拠保全装置</p>
        </div>

        <div className="ray-hero-status">
          <span>FILE SIGHT</span>
          <strong>
            {tauriAvailable
              ? scan
                ? `${scan.scannedCount} FILES VISIBLE`
                : "NOT SCANNED"
              : "LOCAL PREVIEW"}
          </strong>
          <code>{root}</code>
        </div>
      </header>

      <RayProjectRootBar
        draft={rootDraft}
        recentRoots={recentRoots}
        busy={busy || !tauriAvailable}
        onDraftChange={setRootDraft}
        onLoad={() => void loadRoot(rootDraft)}
        onBrowse={() => void browseRoot()}
        onRecent={(value) => {
          setRootDraft(value);
          void loadRoot(value);
        }}
      />

      {operation ? (
        <OperationIndicator
          active
          system="RAY"
          phase={operation.phase}
          detail={operation.detail}
          startedAt={operation.startedAt}
          readyLabel=""
        />
      ) : null}

      <section className="ray-command-bar">
        <button
          type="button"
          className={locked ? "lock active" : "lock"}
          onClick={() => setLocked((value) => !value)}
        >
          {locked ? "TARGET LOCKED" : "TARGET LOCK"}
        </button>

        <button
          type="button"
          className={mode === "QUICK" ? "active" : ""}
          onClick={runQuickRay}
          disabled={!source}
        >
          QUICK RAY
        </button>

        <button
          type="button"
          className={mode === "DEEP" ? "active deep" : "deep"}
          onClick={runDeepRay}
          disabled={!source || clipState === "CLIPPING"}
          title="Run DEEP RAY and copy the Vera handoff capsule to the clipboard"
        >
          {clipState === "CLIPPING" ? "CLIPPING..." : "DEEP RAY"}
        </button>

        <button
          type="button"
          className="ray-copy-vera"
          onClick={copyCurrentRay}
          disabled={!source || clipState === "CLIPPING"}
          title="Copy the current RAY result again for pasting into Vera"
        >
          COPY RAY → VERA
        </button>

        <span
          className={`ray-clip-state ${clipState.toLowerCase()}`}
          title="DEEP RAY automatically clips a Vera handoff capsule"
        >
          CLIP {clipState}
          {clipBytes > 0 ? ` · ${Math.ceil(clipBytes / 1024)} KB` : ""}
        </span>
      </section>

      {runtimeError ? (
        <div className="ray-runtime-error">
          <strong>RAY RUNTIME</strong>
          <code>{runtimeError}</code>
        </div>
      ) : null}

      <section className="ray-cockpit">
        <RayProjectTree
          files={files}
          symbolFacts={facts.symbolFacts}
          targetIds={targetIds}
          activeId={activeId}
          locked={locked}
          onActivate={(id) => {
            setFocusLine(null);
            setActiveId(id);
          }}
          onRevealLine={(fileId, line) => {
            setActiveId(fileId);
            setFocusLine(line);
          }}
          onToggleTarget={toggleTarget}
        />

        <RaySourceViewer
          file={activeFile}
          source={source}
          reading={runtimeState === "READING"}
          error={sourceError}
          focusLine={focusLine}
        />

        <RayInspector
          file={activeFile}
          source={source}
          facts={facts}
          mode={mode}
        />

        <RayTargetSet
          targets={targets}
          locked={locked}
          onActivate={setActiveId}
        />

        <RayEvidence
          findings={findings}
          onRevealLine={(line) => setFocusLine(line)}
        />
      </section>

      <footer className="ray-status-board">
        <span>FLOATING_WINDOW_POLICY=PROHIBITED_FOR_PERSISTENT_TOOLS</span>
        <span>
          FILES={scan?.scannedCount ?? 0} · SKIPPED={scan?.skippedCount ?? 0} ·
          STATE={tauriAvailable ? runtimeState : "LOCAL_UI"}
        </span>
        <span>RAY_MODE={mode} · CLIP={clipState}</span>
      </footer>
    </main>
  );
}
