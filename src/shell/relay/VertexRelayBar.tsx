import {
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  getDirectRelayEndpoint,
  setDirectRelayEndpoint,
} from "../../core/relay/directRelayTransport";
import {
  evaluateVertexAdapterRoute,
  getSelectedVertexAdapterId,
  listVertexAdapters,
  sendVertexRelayViaAdapter,
  setSelectedVertexAdapterId,
} from "../../core/adapters/relayAdapterPort";
import type {
  VertexAdapterId,
} from "../../core/adapters/types";
import {
  parseVertexRelay,
  serializeVertexRelay,
} from "../../core/relay/vertexRelay";
import {
  getOpenAiApiRuntimeStatus,
} from "../../core/adapters/openAiApiAdapter";
import type {
  OpenAiApiRuntimeStatus,
} from "../../core/adapters/openAiApiAdapter";
import type { VertexRelayEnvelope } from "../../core/relay/types";
import "./vertexRelay.css";

interface VertexRelayBarProps {
  readonly envelope: VertexRelayEnvelope;
  readonly onReceive?: (
    envelope: VertexRelayEnvelope,
  ) => void;
}

export function VertexRelayBar({
  envelope,
  onReceive,
}: VertexRelayBarProps) {
  const [receiveOpen, setReceiveOpen] =
    useState(false);
  const [linkOpen, setLinkOpen] =
    useState(false);
  const [rawIncoming, setRawIncoming] =
    useState("");
  const [message, setMessage] =
    useState("READY");
  const [sending, setSending] =
    useState(false);
  const [endpoint, setEndpoint] =
    useState(getDirectRelayEndpoint);
  const [adapterId, setAdapterId] =
    useState<VertexAdapterId>(
      getSelectedVertexAdapterId,
    );
  const [
    openAiStatus,
    setOpenAiStatus,
  ] = useState<OpenAiApiRuntimeStatus | null>(
    null,
  );
  const [
    providerResponse,
    setProviderResponse,
  ] = useState<{
    readonly text: string;
    readonly model?: string;
    readonly responseId?: string;
  } | null>(null);

  const adapters = useMemo(
    () => listVertexAdapters(),
    [],
  );

  const activeAdapter = useMemo(
    () =>
      adapters.find(
        (adapter) =>
          adapter.id === adapterId,
      ) ?? adapters[0],
    [adapterId, adapters],
  );

  const adapterRuntime = useMemo(
    () => ({
      openAiApiAvailable:
        openAiStatus?.available,
      openAiApiConfigured:
        openAiStatus?.configured,
    }),
    [openAiStatus],
  );

  const activeRoute = useMemo(
    () =>
      evaluateVertexAdapterRoute(
        adapterId,
        endpoint,
        adapterRuntime,
      ),
    [
      adapterId,
      endpoint,
      adapterRuntime,
    ],
  );

  useEffect(() => {
    if (adapterId !== "OPENAI_API") {
      return;
    }

    let cancelled = false;

    setMessage("OPENAI STATUS...");

    void getOpenAiApiRuntimeStatus()
      .then((status) => {
        if (cancelled) {
          return;
        }

        setOpenAiStatus(status);
        setMessage(
          status.available
            ? (
                status.configured
                  ? "OPENAI READY"
                  : "OPENAI KEY REQUIRED"
              )
            : "OPENAI TAURI REQUIRED",
        );
      });

    return () => {
      cancelled = true;
    };
  }, [adapterId]);

  const serialized = useMemo(
    () => serializeVertexRelay(envelope),
    [envelope],
  );

  const directLinked = Boolean(
    endpoint.trim(),
  );

  async function copyRelay() {
    try {
      await navigator.clipboard.writeText(
        serialized,
      );
      setMessage("COPIED");
    } catch {
      setMessage("COPY FAILED");
    }
  }

  async function sendDirect() {
    const target = endpoint.trim();

    let runtime = adapterRuntime;

    if (adapterId === "OPENAI_API") {
      setSending(true);
      setMessage("OPENAI STATUS...");

      const status =
        await getOpenAiApiRuntimeStatus();

      setOpenAiStatus(status);

      runtime = {
        openAiApiAvailable:
          status.available,
        openAiApiConfigured:
          status.configured,
      };
    }

    const route =
      evaluateVertexAdapterRoute(
        adapterId,
        target,
        runtime,
      );

    if (!route.sendable) {
      setSending(false);
      setMessage(
        `${route.state}: ${route.reason ?? adapterId}`,
      );

      if (
        route.state ===
          "LINK_REQUIRED" &&
        adapterId ===
          "VERTEX_RELAY_HTTP"
      ) {
        setLinkOpen(true);
      }

      return;
    }

    setSending(true);
    setProviderResponse(null);
    setMessage(
      adapterId === "OPENAI_API"
        ? "OPENAI PROCESSING..."
        : "SENDING...",
    );

    try {
      const result =
        await sendVertexRelayViaAdapter(
          adapterId,
          envelope,
          target,
          runtime,
        );

      if (result.responseText) {
        setProviderResponse({
          text: result.responseText,
          model: result.model,
          responseId:
            result.providerResponseId,
        });
      }

      setMessage(
        result.ok
          ? (
              result.responseText
                ? `SENT ${result.status} · RESPONSE READY`
                : `SENT ${result.status}`
            )
          : `SEND FAILED ${result.status}`,
      );
    } catch (error) {
      if (
        error instanceof DOMException &&
        error.name === "AbortError"
      ) {
        setMessage("SEND TIMEOUT");
      } else {
        setMessage(
          error instanceof Error
            ? error.message
            : "SEND FAILED",
        );
      }
    } finally {
      setSending(false);
    }
  }

  async function changeAdapter(
    id: VertexAdapterId,
  ) {
    setSelectedVertexAdapterId(id);
    setAdapterId(id);
    setProviderResponse(null);

    let runtime = adapterRuntime;

    if (id === "OPENAI_API") {
      setMessage("OPENAI STATUS...");

      const status =
        await getOpenAiApiRuntimeStatus();

      setOpenAiStatus(status);

      runtime = {
        openAiApiAvailable:
          status.available,
        openAiApiConfigured:
          status.configured,
      };
    }

    const route =
      evaluateVertexAdapterRoute(
        id,
        endpoint,
        runtime,
      );

    setMessage(
      `ADAPTER ${route.state}`,
    );
  }

  function saveEndpoint() {
    try {
      setDirectRelayEndpoint(endpoint);
      setEndpoint(
        getDirectRelayEndpoint(),
      );
      setMessage(
        endpoint.trim()
          ? "DIRECT LINKED"
          : "DIRECT OFFLINE",
      );
      setLinkOpen(false);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "LINK FAILED",
      );
    }
  }

  function acceptIncoming() {
    try {
      const parsed =
        parseVertexRelay(rawIncoming);
      onReceive?.(parsed);
      setMessage("RECEIVED");
      setRawIncoming("");
      setReceiveOpen(false);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "RECEIVE FAILED",
      );
    }
  }

  return (
    <section className="vertex-relay">
      <div className="vertex-relay-line">
        <div className="vertex-relay-identity">
          <span>VERTEX RELAY</span>
          <strong>
            {envelope.type} / {envelope.action}
          </strong>
          <small>
            TRANSPORT: ADAPTER PORT · CLIPBOARD FALLBACK · HUMAN GATE
          </small>
        </div>

        <div className="vertex-relay-actions">
          <label className="vertex-relay-adapter">
            <span>ADAPTER</span>
            <select
              value={adapterId}
              onChange={(event) =>
                void changeAdapter(
                  event.target.value as VertexAdapterId,
                )
              }
            >
              {adapters.map(
                (adapter) => (
                  <option
                    key={adapter.id}
                    value={adapter.id}
                  >
                    {adapter.name}
                  </option>
                ),
              )}
            </select>
          </label>

          <span
            className={
              activeRoute.state ===
                "READY"
                ? "vertex-relay-link linked"
                : "vertex-relay-link"
            }
            title={
              activeRoute.detail
            }
          >
            {activeRoute.state}
          </span>

          {adapterId ===
          "VERTEX_RELAY_HTTP" ? (
            <span
              className={
                directLinked
                  ? "vertex-relay-link linked"
                  : "vertex-relay-link"
              }
            >
              {directLinked
                ? "HTTP LINKED"
                : "HTTP OFFLINE"}
            </span>
          ) : null}

          {adapterId ===
          "OPENAI_API" ? (
            <>
              <span
                className={
                  openAiStatus?.configured
                    ? "vertex-relay-link linked"
                    : "vertex-relay-link"
                }
                title={
                  openAiStatus?.credentialSource ??
                  "OPENAI STATUS UNKNOWN"
                }
              >
                {openAiStatus?.available
                  ? (
                      openAiStatus.configured
                        ? "API KEY READY"
                        : "API KEY REQUIRED"
                    )
                  : "TAURI REQUIRED"}
              </span>

              {openAiStatus?.model ? (
                <span className="vertex-relay-provider-model">
                  {openAiStatus.model}
                </span>
              ) : null}
            </>
          ) : null}

          {sending ? (
            <span
              className="vertex-relay-processing"
              aria-live="polite"
            >
              <i />
              <i />
              <i />
              PROCESSING
            </span>
          ) : null}

          <span className="vertex-relay-state">
            {message}
          </span>

          <button
            type="button"
            onClick={() => void copyRelay()}
          >
            COPY RELAY
          </button>

          <button
            type="button"
            disabled={sending}
            onClick={() => void sendDirect()}
          >
            {sending ? "SENDING" : "SEND"}
          </button>

          <button
            type="button"
            onClick={() =>
              setReceiveOpen(
                (value) => !value,
              )
            }
          >
            RECEIVE
          </button>
        </div>
      </div>

      {linkOpen ? (
        <div className="vertex-relay-link-editor">
          <label>
            <span>DIRECT RELAY ENDPOINT</span>
            <input
              value={endpoint}
              onChange={(event) =>
                setEndpoint(
                  event.target.value,
                )
              }
              placeholder="http://127.0.0.1:PORT/vertex-relay"
              spellCheck={false}
            />
          </label>

          <div>
            <span>
              Vertex Relay HTTP Adapter の ingress URL。
              外部サービス固有の認証情報はCoreへ保存しない。
            </span>

            <button
              type="button"
              onClick={saveEndpoint}
            >
              CONNECT
            </button>

            <button
              type="button"
              onClick={() => {
                setEndpoint("");
                setDirectRelayEndpoint("");
                setLinkOpen(false);
                setMessage(
                  "DIRECT OFFLINE",
                );
              }}
            >
              CLEAR
            </button>
          </div>
        </div>
      ) : null}

      {providerResponse ? (
        <div className="vertex-relay-provider-response">
          <div className="vertex-relay-provider-response-head">
            <span>OPENAI RESPONSE · HUMAN REVIEW</span>
            <small>
              {providerResponse.model ?? "MODEL UNKNOWN"}
              {providerResponse.responseId
                ? ` · ${providerResponse.responseId}`
                : ""}
            </small>
          </div>

          <textarea
            value={providerResponse.text}
            readOnly
            spellCheck={false}
          />

          <div>
            <span>
              API response is review-only. It is not auto-applied to Canonical or Contract.
            </span>

            <button
              type="button"
              onClick={() => {
                void navigator.clipboard.writeText(
                  providerResponse.text,
                );
                setMessage(
                  "RESPONSE COPIED",
                );
              }}
            >
              COPY RESPONSE
            </button>

            <button
              type="button"
              onClick={() =>
                setProviderResponse(null)
              }
            >
              CLOSE
            </button>
          </div>
        </div>
      ) : null}

      {receiveOpen ? (
        <div className="vertex-relay-receive">
          <textarea
            value={rawIncoming}
            onChange={(event) =>
              setRawIncoming(
                event.target.value,
              )
            }
            placeholder="Vera Relay JSON を貼り付け..."
            spellCheck={false}
          />

          <div>
            <span>
              DRAFT / AMEND は Human 確認後に反映
            </span>

            <button
              type="button"
              onClick={acceptIncoming}
              disabled={!rawIncoming.trim()}
            >
              ACCEPT
            </button>

            <button
              type="button"
              onClick={() => {
                setRawIncoming("");
                setReceiveOpen(false);
                setMessage("REJECTED");
              }}
            >
              REJECT
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
