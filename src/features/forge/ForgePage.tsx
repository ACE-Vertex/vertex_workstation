import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BUILD_IDENTITY } from "../../buildIdentity";
import { ArtifactInspector } from "./ArtifactInspector";
import { ConsolePanel } from "./ConsolePanel";
import {
  applyForgeStage,
  isForgeTauriRuntime,
  pickForgeFolder,
  readReceivingBayFingerprint,
  rollbackForgeStage,
  scanReceivingBay,
  stageForgeArtifact,
} from "./forgeApi";
import { ForgeStatusCards } from "./ForgeStatusCards";
import { IncomingCargo } from "./IncomingCargo";
import type {
  ForgeApplyResult,
  ForgeArtifact,
  ForgePathState,
  ForgeRollbackResult,
  ForgeRuntimeState,
  ForgeScanResult,
  ForgeStageResult,
} from "./models";
import { PathSwitcher } from "./PathSwitcher";
import {
  PRODUCTION_ROOT_OPTIONS,
  RECEIVING_BAY_OPTIONS,
} from "./seedData";
import "./forgeRuntime.css";

const nowLabel = () =>
  new Date().toLocaleTimeString("ja-JP", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

const FORGE_RECEIVING_WATCH_INTERVAL_MS = 1500;

export function ForgePage() {
  const tauriAvailable = isForgeTauriRuntime();

  const [paths, setPaths] = useState<ForgePathState>({
    receivingBay: RECEIVING_BAY_OPTIONS[0],
    productionRoot: PRODUCTION_ROOT_OPTIONS[0],
  });
  const [scan, setScan] = useState<ForgeScanResult | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [runtimeState, setRuntimeState] =
    useState<ForgeRuntimeState>("READY");
  const [runtimeError, setRuntimeError] = useState<string | null>(null);
  const [stageResult, setStageResult] =
    useState<ForgeStageResult | null>(null);
  const [applyResult, setApplyResult] =
    useState<ForgeApplyResult | null>(null);
  const [rollbackResult, setRollbackResult] =
    useState<ForgeRollbackResult | null>(null);
  const receivingFingerprintRef = useRef("");
  const receivingWatchInFlightRef = useRef(false);

  const [shellLines, setShellLines] = useState<string[]>([
    "VERTEX WORKSTATION FORGE NEXT — receiving bay service ready",
    `BUILD=${BUILD_IDENTITY.build}`,
    "FORGE_READ_SIDE=ACTIVE",
    "STAGE=READY",
    "APPLY_ROLLBACK=HUMAN_GATE",
  ]);
  const [ledgerLines, setLedgerLines] = useState<string[]>([
    `[${nowLabel()}] FORGE 000008 STAGE ENGINE INITIALIZED`,
    `[${nowLabel()}] MANIFEST_INSPECTOR=READY`,
  ]);

  const artifacts = scan?.artifacts ?? [];

  const selected = useMemo(
    () => artifacts.find((artifact) => artifact.id === selectedId),
    [artifacts, selectedId],
  );

  const ready = artifacts.filter(
    (artifact) => artifact.status === "READY",
  ).length;
  const attention = artifacts.filter(
    (artifact) => artifact.status === "ATTENTION",
  ).length;
  const verified = artifacts.filter(
    (artifact) =>
      artifact.status === "READY" &&
      artifact.stageHistory === "VERIFIED",
  ).length;

  const refresh = useCallback(
    async (nextPaths: ForgePathState = paths) => {
      if (!tauriAvailable) {
        setRuntimeState("READY");
        setRuntimeError(
          "LOCAL UI PREVIEW — FORGE FILESYSTEM REQUIRES TAURI RUNTIME",
        );
        return;
      }

      setRuntimeState("SCANNING");
      setRuntimeError(null);
      setStageResult(null);
      setApplyResult(null);
      setRollbackResult(null);
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — scanning receiving bay",
        `RECEIVING_BAY=${nextPaths.receivingBay}`,
        `AUTHORIZED_ROOT=${nextPaths.productionRoot}`,
        "MANIFEST_MODE=READ_ONLY",
      ]);

      try {
        const result = await scanReceivingBay(
          nextPaths.receivingBay,
          nextPaths.productionRoot,
        );
        receivingFingerprintRef.current =
          await readReceivingBayFingerprint(result.receivingBay);

        setScan(result);
        setPaths({
          receivingBay: result.receivingBay,
          productionRoot: result.productionRoot,
        });

        setSelectedId((current) => {
          if (
            result.artifacts.some(
              (artifact) => artifact.id === current,
            )
          ) {
            return current;
          }
          return result.artifacts[0]?.id ?? "";
        });

        const readyCount = result.artifacts.filter(
          (artifact) => artifact.status === "READY",
        ).length;
        const attentionCount =
          result.artifacts.length - readyCount;

        setShellLines([
          "VERTEX WORKSTATION FORGE NEXT — receiving bay scan complete",
          `RECEIVING=${result.artifacts.length}`,
          `READY=${readyCount}`,
          `ATTENTION=${attentionCount}`,
          `IGNORED_NON_VRA=${result.ignoredCount}`,
          "MANIFEST_SOURCE=REAL_VRA_ZIP",
          "STAGE=ARMED_FOR_READY_ARTIFACT",
          "APPLY=ARMED_AFTER_STAGE",
          "ROLLBACK=ARMED_AFTER_APPLY",
        ]);
        setLedgerLines((current) =>
          [
            `[${nowLabel()}] RECEIVING_SCAN PASS — ${result.artifacts.length} artifact(s)`,
            `[${nowLabel()}] READY=${readyCount} ATTENTION=${attentionCount} IGNORED=${result.ignoredCount}`,
            ...current,
          ].slice(0, 48),
        );
        setRuntimeState("READY");
      } catch (error) {
        const message =
          error instanceof Error ? error.message : String(error);
        setScan(null);
        setSelectedId("");
        setRuntimeState("ERROR");
        setRuntimeError(message);
        setShellLines([
          "VERTEX WORKSTATION FORGE NEXT — receiving bay scan failed",
          `ERROR=${message}`,
        ]);
        setLedgerLines((current) =>
          [
            `[${nowLabel()}] RECEIVING_SCAN FAIL — ${message}`,
            ...current,
          ].slice(0, 48),
        );
      }
    },
    [paths, tauriAvailable],
  );

  useEffect(() => {
    if (tauriAvailable) {
      void refresh(paths);
    } else {
      setRuntimeError(
        "LOCAL UI PREVIEW — FORGE FILESYSTEM REQUIRES TAURI RUNTIME",
      );
    }
    // Initial visible scan. Receiving Bay live watch continues below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tauriAvailable]);

  useEffect(() => {
    if (!tauriAvailable || runtimeState !== "READY") return;

    let disposed = false;

    const probeReceivingBay = async () => {
      if (
        disposed ||
        receivingWatchInFlightRef.current ||
        document.visibilityState === "hidden"
      ) {
        return;
      }

      receivingWatchInFlightRef.current = true;

      try {
        const fingerprint = await readReceivingBayFingerprint(
          paths.receivingBay,
        );

        if (disposed) return;

        if (!receivingFingerprintRef.current) {
          receivingFingerprintRef.current = fingerprint;
          return;
        }

        if (fingerprint === receivingFingerprintRef.current) {
          return;
        }

        receivingFingerprintRef.current = fingerprint;
        setLedgerLines((current) =>
          [
            `[${nowLabel()}] RECEIVING WATCH CHANGE DETECTED — rescanning`,
            ...current,
          ].slice(0, 48),
        );
        await refresh(paths);
      } catch (error) {
        if (!disposed) {
          const message =
            error instanceof Error ? error.message : String(error);
          setRuntimeError((current) =>
            current === message ? current : message,
          );
        }
      } finally {
        receivingWatchInFlightRef.current = false;
      }
    };

    const timer = window.setInterval(
      () => void probeReceivingBay(),
      FORGE_RECEIVING_WATCH_INTERVAL_MS,
    );

    return () => {
      disposed = true;
      window.clearInterval(timer);
    };
  }, [
    paths.productionRoot,
    paths.receivingBay,
    refresh,
    runtimeState,
    tauriAvailable,
  ]);

  async function browsePath(
    kind: "receivingBay" | "productionRoot",
  ) {
    if (!tauriAvailable) return;

    const label =
      kind === "receivingBay"
        ? "Select FORGE Receiving Bay"
        : "Select Authorized Production Root";

    try {
      const selectedPath = await pickForgeFolder(
        paths[kind],
        label,
      );
      if (!selectedPath) return;

      const nextPaths = {
        ...paths,
        [kind]: selectedPath,
      };
      setPaths(nextPaths);
      await refresh(nextPaths);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      setRuntimeState("ERROR");
      setRuntimeError(message);
    }
  }

  async function stageArtifact(artifact: ForgeArtifact) {
    if (!tauriAvailable) return;

    setRuntimeState("STAGING");
    setRuntimeError(null);
    setStageResult(null);
    setApplyResult(null);
    setRollbackResult(null);

    setShellLines([
      "VERTEX WORKSTATION FORGE NEXT — staging artifact",
      `ARTIFACT=${artifact.id}`,
      `SOURCE=${artifact.filePath}`,
      `TARGET=${artifact.target}`,
      "HASH_VERIFICATION=RUNNING",
      "TARGET_MUTATION=NO",
    ]);
    setLedgerLines((current) =>
      [
        `[${nowLabel()}] STAGE START ${artifact.id}`,
        ...current,
      ].slice(0, 48),
    );

    try {
      const result = await stageForgeArtifact(
        artifact.filePath,
        paths.productionRoot,
      );

      setStageResult(result);
      setScan((current) =>
        current
          ? {
              ...current,
              artifacts: current.artifacts.map((item) =>
                item.id === artifact.id
                  ? { ...item, stageHistory: "VERIFIED" as const }
                  : item,
              ),
            }
          : current,
      );
      setRuntimeState("READY");
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — stage complete",
        `STAGE_ID=${result.stageId}`,
        `ARTIFACT_SHA256=${result.artifactSha256}`,
        `PAYLOAD=${result.payloadCount}`,
        `HASH_VERIFIED=${result.verifiedCount}`,
        `STAGING_ROOT=${result.stagingRoot}`,
        `TARGET=${result.targetRoot}`,
        "TARGET_MUTATION=NO",
        "NEXT_GATE=HUMAN_APPLY",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] STAGE PASS ${artifact.id}`,
          `[${nowLabel()}] HASH ${result.verifiedCount}/${result.payloadCount} VERIFIED`,
          `[${nowLabel()}] STAGE_ID=${result.stageId}`,
          `[${nowLabel()}] TARGET_MUTATION=NO`,
          ...current,
        ].slice(0, 48),
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      if (artifact.stageHistory !== "VERIFIED") {
        setScan((current) =>
          current
            ? {
                ...current,
                artifacts: current.artifacts.map((item) =>
                  item.id === artifact.id
                    ? { ...item, stageHistory: "ERROR" as const }
                    : item,
                ),
              }
            : current,
        );
      }
      setRuntimeState("ERROR");
      setRuntimeError(message);
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — stage failed",
        `ARTIFACT=${artifact.id}`,
        `ERROR=${message}`,
        "TARGET_MUTATION=NO",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] STAGE FAIL ${artifact.id} — ${message}`,
          ...current,
        ].slice(0, 48),
      );
    }
  }

  async function applyStage(stage: ForgeStageResult) {
    if (!tauriAvailable) return;

    setRuntimeState("APPLYING");
    setRuntimeError(null);
    setApplyResult(null);
    setRollbackResult(null);
    setShellLines([
      "VERTEX WORKSTATION FORGE NEXT — HUMAN APPLY",
      `STAGE_ID=${stage.stageId}`,
      `ARTIFACT=${stage.artifactId}`,
      `TARGET=${stage.targetRoot}`,
      "BACKUP=PREPARE BEFORE MUTATION",
      "TARGET_MUTATION=ARMED",
    ]);
    setLedgerLines((current) =>
      [
        `[${nowLabel()}] APPLY START ${stage.artifactId}`,
        `[${nowLabel()}] HUMAN_GATE=CONFIRMED_BY_APPLY_CLICK`,
        ...current,
      ].slice(0, 48),
    );

    try {
      const result = await applyForgeStage(
        stage.stageId,
        paths.productionRoot,
      );
      setApplyResult(result);
      setRuntimeState("READY");
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — apply complete",
        `STAGE_ID=${result.stageId}`,
        `ARTIFACT_SHA256=${result.artifactSha256}`,
        `TARGET=${result.targetRoot}`,
        `APPLIED=${result.appliedCount}`,
        `BACKUP_ROOT=${result.backupRoot}`,
        "TARGET_MUTATION=YES",
        "NEXT_GATE=RUNTIME_ACCEPTANCE_OR_ROLLBACK",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] APPLY PASS ${result.artifactId}`,
          `[${nowLabel()}] FILES ${result.appliedCount} MUTATED`,
          `[${nowLabel()}] BACKUP ${result.backupRoot}`,
          `[${nowLabel()}] ROLLBACK=ARMED`,
          ...current,
        ].slice(0, 48),
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      setRuntimeState("ERROR");
      setRuntimeError(message);
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — apply failed",
        `STAGE_ID=${stage.stageId}`,
        `ERROR=${message}`,
        "AUTO_RESTORE=ATTEMPTED_BY_RUST_IF_MUTATION_BEGAN",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] APPLY FAIL ${stage.artifactId} — ${message}`,
          ...current,
        ].slice(0, 48),
      );
    }
  }

  async function rollbackStage(stage: ForgeStageResult) {
    if (!tauriAvailable) return;

    setRuntimeState("ROLLING_BACK");
    setRuntimeError(null);
    setShellLines([
      "VERTEX WORKSTATION FORGE NEXT — rollback",
      `STAGE_ID=${stage.stageId}`,
      `TARGET=${stage.targetRoot}`,
      "BACKUP_RESTORE=RUNNING",
    ]);
    setLedgerLines((current) =>
      [
        `[${nowLabel()}] ROLLBACK START ${stage.artifactId}`,
        ...current,
      ].slice(0, 48),
    );

    try {
      const result = await rollbackForgeStage(
        stage.stageId,
        paths.productionRoot,
      );
      setRollbackResult(result);
      setRuntimeState("READY");
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — rollback complete",
        `STAGE_ID=${result.stageId}`,
        `TARGET=${result.targetRoot}`,
        `RESTORED=${result.restoredCount}`,
        `REMOVED_NEW=${result.removedCount}`,
        "TARGET_STATE=PRE_APPLY_RESTORED",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] ROLLBACK PASS ${stage.artifactId}`,
          `[${nowLabel()}] RESTORED=${result.restoredCount} REMOVED=${result.removedCount}`,
          ...current,
        ].slice(0, 48),
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : String(error);
      setRuntimeState("ERROR");
      setRuntimeError(message);
      setShellLines([
        "VERTEX WORKSTATION FORGE NEXT — rollback failed",
        `STAGE_ID=${stage.stageId}`,
        `ERROR=${message}`,
        "MANUAL_RECOVERY=REQUIRED",
      ]);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] ROLLBACK FAIL ${stage.artifactId} — ${message}`,
          ...current,
        ].slice(0, 48),
      );
    }
  }

  async function copyInspection(artifact: ForgeArtifact) {
    const summary = JSON.stringify(
      {
        id: artifact.id,
        file: artifact.filePath,
        title: artifact.title,
        schema: artifact.schemaVersion,
        source: artifact.source,
        target: artifact.target,
        authority: artifact.authority,
        payloadCount: artifact.payloadCount,
        verificationCount: artifact.verificationCount,
        status: artifact.status,
        stageHistory: artifact.stageHistory,
        artifactSha256: artifact.artifactSha256,
        manifestValid: artifact.manifestValid,
        targetAuthorized: artifact.targetAuthorized,
        operationPreview: artifact.operationPreview,
        errors: artifact.errors,
        stage:
          stageResult?.artifactId === artifact.id
            ? stageResult
            : null,
        apply:
          applyResult?.artifactId === artifact.id
            ? applyResult
            : null,
        rollback:
          rollbackResult &&
          stageResult?.artifactId === artifact.id &&
          rollbackResult.stageId === stageResult.stageId
            ? rollbackResult
            : null,
      },
      null,
      2,
    );

    try {
      await navigator.clipboard.writeText(summary);
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] COPY_INSPECTION ${artifact.id}`,
          ...current,
        ].slice(0, 48),
      );
    } catch {
      setLedgerLines((current) =>
        [
          `[${nowLabel()}] COPY_INSPECTION FAILED ${artifact.id}`,
          ...current,
        ].slice(0, 48),
      );
    }
  }

  const busy =
    runtimeState === "SCANNING" ||
    runtimeState === "STAGING" ||
    runtimeState === "APPLYING" ||
    runtimeState === "ROLLING_BACK";

  return (
    <main className="forge-page">
      <header className="forge-hero">
        <div>
          <span>ARTIFACT ENGINEERING · VERIFICATION · DISPATCH</span>
          <h1>
            VERTEX <strong>WORKSTATION</strong>
          </h1>
          <p>
            受信 → 検査 → 鍛造 → 検証 → Evidence → ディスパッチ
          </p>
        </div>

        <div className="hero-right">
          <span className="works-online">FORGE ONLINE</span>
          <code>v{BUILD_IDENTITY.version}</code>
          <code>BUILD {BUILD_IDENTITY.build}</code>
        </div>
      </header>

      <section className="forge-topline">
        <ForgeStatusCards
          receiving={artifacts.length}
          ready={ready}
          verified={verified}
          attention={attention}
        />

        <PathSwitcher
          label="RECEIVING BAY"
          value={paths.receivingBay}
          options={RECEIVING_BAY_OPTIONS}
          disabled={busy}
          onChange={(receivingBay) =>
            setPaths((current) => ({
              ...current,
              receivingBay,
            }))
          }
          onCommit={() => void refresh()}
          onBrowse={() => void browsePath("receivingBay")}
        />

        <PathSwitcher
          label="AUTHORIZED PRODUCTION ROOT"
          value={paths.productionRoot}
          options={PRODUCTION_ROOT_OPTIONS}
          disabled={busy}
          onChange={(productionRoot) =>
            setPaths((current) => ({
              ...current,
              productionRoot,
            }))
          }
          onCommit={() => void refresh()}
          onBrowse={() => void browsePath("productionRoot")}
        />
      </section>

      <section className="forge-grid">
        <IncomingCargo
          artifacts={artifacts}
          selectedId={selectedId}
          busy={busy}
          onSelect={(id) => {
            setSelectedId(id);
            setStageResult(null);
            setApplyResult(null);
            setRollbackResult(null);
            setLedgerLines((current) =>
              [
                `[${nowLabel()}] INSPECT ${id}`,
                ...current,
              ].slice(0, 48),
            );
          }}
          onRefresh={() => void refresh()}
        />

        <ArtifactInspector
          artifact={selected}
          stageResult={stageResult}
          applyResult={applyResult}
          rollbackResult={rollbackResult}
          staging={runtimeState === "STAGING"}
          applying={runtimeState === "APPLYING"}
          rollingBack={runtimeState === "ROLLING_BACK"}
          onStage={(artifact) =>
            void stageArtifact(artifact)
          }
          onApply={(stage) =>
            void applyStage(stage)
          }
          onRollback={(stage) =>
            void rollbackStage(stage)
          }
          onCopyInspection={(artifact) =>
            void copyInspection(artifact)
          }
        />

        <ConsolePanel
          eyebrow="03 / FOUNDRY STREAM"
          title="Vertex Shell"
          badge={
            runtimeState === "ERROR"
              ? "ATTN"
              : runtimeState === "SCANNING"
                ? "SCAN"
                : runtimeState === "STAGING"
                  ? "STAGE"
                  : runtimeState === "APPLYING"
                    ? "APPLY"
                    : runtimeState === "ROLLING_BACK"
                      ? "RBK"
                      : "PASS"
          }
          lines={
            runtimeError
              ? [...shellLines, `RUNTIME=${runtimeError}`]
              : shellLines
          }
        />

        <ConsolePanel
          eyebrow="04 / EVIDENCE VAULT"
          title="Works Ledger"
          lines={ledgerLines}
        />
      </section>

      <footer
        className={`state-board forge-activity ${
          busy ? "busy" : ""
        }`}
      >
        <span>
          {runtimeState === "SCANNING"
            ? "FORGE ACTIVITY — SCANNING RECEIVING BAY..."
            : runtimeState === "STAGING"
              ? "FORGE ACTIVITY — HASH VERIFY + IMMUTABLE STAGING..."
              : runtimeState === "APPLYING"
                ? "FORGE ACTIVITY — HUMAN APPLY + BACKUP + TARGET MUTATION..."
                : runtimeState === "ROLLING_BACK"
                  ? "FORGE ACTIVITY — ROLLBACK + BACKUP RESTORE..."
                  : runtimeState === "ERROR"
                ? "FORGE ACTIVITY — ATTENTION REQUIRED"
                : rollbackResult
                  ? `WORKS STATE BOARD — ROLLBACK COMPLETE ${rollbackResult.stageId}`
                  : applyResult
                    ? `WORKS STATE BOARD — APPLY COMPLETE ${applyResult.appliedCount} FILE(S)`
                    : stageResult
                      ? `WORKS STATE BOARD — STAGE VERIFIED ${stageResult.verifiedCount}/${stageResult.payloadCount} · APPLY ARMED`
                  : `WORKS STATE BOARD — ${artifacts.length} REAL .VRA ARTIFACT(S) VISIBLE`}
        </span>
        <span>
          {runtimeState === "STAGING"
            ? "STG"
            : runtimeState === "APPLYING"
              ? "APL"
              : runtimeState === "ROLLING_BACK"
                ? "RBK"
                : busy
                  ? "SCAN"
                  : "VCR"}
        </span>
      </footer>
    </main>
  );
}
