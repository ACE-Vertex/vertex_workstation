import {
  sendVertexRelayDirect,
} from "../relay/directRelayTransport";
import type {
  VertexRelayEnvelope,
} from "../relay/types";
import {
  VertexAdapterRegistry,
} from "./registry";
import {
  sendVertexRelayViaOpenAiApi,
} from "./openAiApiAdapter";
import type {
  VertexAdapter,
  VertexAdapterDescriptor,
  VertexAdapterId,
  VertexAdapterRouteEvaluation,
  VertexAdapterRuntimeContext,
  VertexAdapterSendResult,
} from "./types";

export const VERTEX_ADAPTER_PORT_KEY =
  "vertex.adapter.port.active.v1";

const relayHttpAdapter: VertexAdapter = {
  descriptor: {
    id: "VERTEX_RELAY_HTTP",
    name: "Vertex Relay HTTP",
    kind: "RELAY_TRANSPORT",
    state: "READY",
    capabilities: [
      "SEND_RELAY",
      "RECEIVE_RELAY",
    ],
    detail:
      "Real HTTP POST transport into Vertex Relay / Bridge / MCP ingress.",
  },
  async send(
    envelope,
    context,
  ) {
    const endpoint =
      context.endpoint?.trim() ?? "";

    if (!endpoint) {
      throw new Error(
        "ADAPTER_LINK_REQUIRED:VERTEX_RELAY_HTTP",
      );
    }

    return sendVertexRelayDirect(
      envelope,
      endpoint,
    );
  },
};

const chatGptMcpAdapter: VertexAdapter = {
  descriptor: {
    id: "CHATGPT_MCP",
    name: "ChatGPT MCP",
    kind: "MODEL_PROVIDER",
    state: "EXTERNAL_GATE",
    capabilities: [
      "MCP_READ",
      "MCP_WRITE",
    ],
    gate:
      "CHATGPT_APP_OR_MCP_CONNECTION_REQUIRED",
    detail:
      "Official MCP boundary. Product/account connection is external to Workstation.",
  },
};

const openAiApiAdapter: VertexAdapter = {
  descriptor: {
    id: "OPENAI_API",
    name: "OpenAI API",
    kind: "MODEL_PROVIDER",
    state: "READY",
    capabilities: [
      "SEND_RELAY",
      "RECEIVE_RELAY",
    ],
    gate:
      "OPENAI_API_KEY_REQUIRED",
    detail:
      "Real Tauri/Rust Responses API adapter. Credential remains outside Presentation and Relay payloads.",
  },
  async send(
    envelope,
    _context,
  ) {
    return sendVertexRelayViaOpenAiApi(
      envelope,
    );
  },
};

const localLlmAdapter: VertexAdapter = {
  descriptor: {
    id: "LOCAL_LLM",
    name: "Local LLM",
    kind: "MODEL_PROVIDER",
    state: "UNCONFIGURED",
    capabilities: [
      "SEND_RELAY",
      "RECEIVE_RELAY",
    ],
    gate:
      "LOCAL_MODEL_RUNTIME_ADAPTER_REQUIRED",
    detail:
      "Reserved provider-neutral slot for local model runtimes.",
  },
};

const hyperAgentAdapter: VertexAdapter = {
  descriptor: {
    id: "HYPER_AGENT",
    name: "Hyper Agent",
    kind: "AGENT_RUNTIME",
    state: "UNCONFIGURED",
    capabilities: [
      "SEND_RELAY",
      "RECEIVE_RELAY",
      "MCP_READ",
      "MCP_WRITE",
    ],
    gate:
      "HYPER_AGENT_ADAPTER_REQUIRED",
    detail:
      "Reserved Vertex-owned agent runtime adapter slot.",
  },
};

const registry =
  new VertexAdapterRegistry();

for (const adapter of [
  relayHttpAdapter,
  chatGptMcpAdapter,
  openAiApiAdapter,
  localLlmAdapter,
  hyperAgentAdapter,
]) {
  registry.register(adapter);
}

export function listVertexAdapters():
  readonly VertexAdapterDescriptor[] {
  return registry
    .list()
    .map(
      (adapter) =>
        adapter.descriptor,
    );
}

export function getVertexAdapter(
  id: VertexAdapterId,
): VertexAdapter {
  return registry.get(id);
}

export function getSelectedVertexAdapterId():
  VertexAdapterId {
  try {
    const value =
      localStorage.getItem(
        VERTEX_ADAPTER_PORT_KEY,
      ) as VertexAdapterId | null;

    if (
      value &&
      listVertexAdapters().some(
        (adapter) =>
          adapter.id === value,
      )
    ) {
      return value;
    }
  } catch {
    // localStorage is optional.
  }

  return "VERTEX_RELAY_HTTP";
}

export function setSelectedVertexAdapterId(
  id: VertexAdapterId,
): void {
  registry.get(id);

  try {
    localStorage.setItem(
      VERTEX_ADAPTER_PORT_KEY,
      id,
    );
  } catch {
    // Selection still works for this session.
  }
}


export function evaluateVertexAdapterRoute(
  id: VertexAdapterId,
  endpoint?: string,
  runtime?: VertexAdapterRuntimeContext,
): VertexAdapterRouteEvaluation {
  const adapter =
    registry.get(id);

  if (
    id === "VERTEX_RELAY_HTTP" &&
    !(endpoint?.trim())
  ) {
    return {
      adapterId: id,
      state: "LINK_REQUIRED",
      sendable: false,
      reason:
        "VERTEX_RELAY_HTTP_ENDPOINT_REQUIRED",
      detail:
        "The real HTTP adapter is available, but no Relay ingress endpoint is configured.",
    };
  }

  if (id === "OPENAI_API") {
    if (
      runtime?.openAiApiAvailable ===
        false
    ) {
      return {
        adapterId: id,
        state: "UNCONFIGURED",
        sendable: false,
        reason:
          "OPENAI_API_TAURI_RUNTIME_REQUIRED",
        detail:
          "OpenAI API transport is owned by the Tauri/Rust backend and is unavailable in browser-only preview.",
      };
    }

    if (
      runtime?.openAiApiConfigured !==
        true
    ) {
      return {
        adapterId: id,
        state: "LINK_REQUIRED",
        sendable: false,
        reason:
          "OPENAI_API_KEY_REQUIRED",
        detail:
          "The OpenAI API adapter is implemented, but the user-owned OPENAI_API_KEY environment credential is not configured.",
      };
    }
  }

  if (
    adapter.descriptor.state ===
      "EXTERNAL_GATE"
  ) {
    return {
      adapterId: id,
      state: "EXTERNAL_GATE",
      sendable: false,
      reason:
        adapter.descriptor.gate ??
        "EXTERNAL_PROVIDER_GATE",
      detail:
        adapter.descriptor.detail,
    };
  }

  if (
    adapter.descriptor.state ===
      "UNCONFIGURED"
  ) {
    return {
      adapterId: id,
      state: "UNCONFIGURED",
      sendable: false,
      reason:
        adapter.descriptor.gate ??
        "ADAPTER_CONFIGURATION_REQUIRED",
      detail:
        adapter.descriptor.detail,
    };
  }

  if (!adapter.send) {
    return {
      adapterId: id,
      state: "UNCONFIGURED",
      sendable: false,
      reason:
        "ADAPTER_SEND_NOT_IMPLEMENTED",
      detail:
        adapter.descriptor.detail,
    };
  }

  return {
    adapterId: id,
    state: "READY",
    sendable: true,
    detail:
      adapter.descriptor.detail,
  };
}

export async function sendVertexRelayViaAdapter(
  id: VertexAdapterId,
  envelope: VertexRelayEnvelope,
  endpoint?: string,
  runtime?: VertexAdapterRuntimeContext,
): Promise<VertexAdapterSendResult> {
  const adapter =
    registry.get(id);
  const route =
    evaluateVertexAdapterRoute(
      id,
      endpoint,
      runtime,
    );

  if (!route.sendable) {
    throw new Error(
      `ADAPTER_ROUTE_BLOCKED:${id}:${route.state}:${route.reason ?? "UNKNOWN"}`,
    );
  }

  if (!adapter.send) {
    throw new Error(
      `ADAPTER_ROUTE_INVARIANT_BROKEN:${id}`,
    );
  }

  return adapter.send(
    envelope,
    {
      endpoint,
      runtime,
    },
  );
}
