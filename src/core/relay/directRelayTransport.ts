import type { VertexRelayEnvelope } from "./types";
import { serializeVertexRelay } from "./vertexRelay";

export const VERTEX_RELAY_ENDPOINT_KEY =
  "vertex.relay.direct.endpoint.v1";

export interface DirectRelayResult {
  readonly ok: boolean;
  readonly status: number;
  readonly detail: string;
}

export function getDirectRelayEndpoint(): string {
  try {
    return localStorage.getItem(
      VERTEX_RELAY_ENDPOINT_KEY,
    ) ?? "";
  } catch {
    return "";
  }
}

export function setDirectRelayEndpoint(
  endpoint: string,
): void {
  const value = endpoint.trim();

  if (!value) {
    localStorage.removeItem(
      VERTEX_RELAY_ENDPOINT_KEY,
    );
    return;
  }

  const url = new URL(value);

  if (
    url.protocol !== "http:" &&
    url.protocol !== "https:"
  ) {
    throw new Error(
      "DIRECT_ENDPOINT_PROTOCOL_INVALID",
    );
  }

  localStorage.setItem(
    VERTEX_RELAY_ENDPOINT_KEY,
    url.toString(),
  );
}

export async function sendVertexRelayDirect(
  envelope: VertexRelayEnvelope,
  endpoint: string,
): Promise<DirectRelayResult> {
  const url = new URL(endpoint);

  if (
    url.protocol !== "http:" &&
    url.protocol !== "https:"
  ) {
    throw new Error(
      "DIRECT_ENDPOINT_PROTOCOL_INVALID",
    );
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(
    () => controller.abort(),
    10_000,
  );

  try {
    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Content-Type":
          "application/vnd.vertex-relay+json",
        Accept: "application/json, text/plain, */*",
      },
      body: serializeVertexRelay(envelope),
      signal: controller.signal,
    });

    const detail = (
      await response.text()
    ).slice(0, 512);

    return {
      ok: response.ok,
      status: response.status,
      detail,
    };
  } finally {
    window.clearTimeout(timeout);
  }
}
