import {
  invoke,
} from "@tauri-apps/api/core";
import type {
  VertexRelayEnvelope,
} from "../relay/types";
import type {
  VertexAdapterSendResult,
} from "./types";

export interface OpenAiApiRuntimeStatus {
  readonly available: boolean;
  readonly configured: boolean;
  readonly model: string;
  readonly credentialSource: string;
  readonly endpoint: string;
}

interface OpenAiApiBackendSendResult {
  readonly ok: boolean;
  readonly status: number;
  readonly detail: string;
  readonly responseId: string;
  readonly model: string;
  readonly outputText: string;
}

export async function getOpenAiApiRuntimeStatus():
  Promise<OpenAiApiRuntimeStatus> {
  try {
    return await invoke<OpenAiApiRuntimeStatus>(
      "openai_api_status",
    );
  } catch {
    return {
      available: false,
      configured: false,
      model: "",
      credentialSource:
        "TAURI_RUNTIME_REQUIRED",
      endpoint: "",
    };
  }
}

export async function sendVertexRelayViaOpenAiApi(
  envelope: VertexRelayEnvelope,
): Promise<VertexAdapterSendResult> {
  const result =
    await invoke<OpenAiApiBackendSendResult>(
      "openai_api_send_relay",
      {
        envelope,
      },
    );

  return {
    ok: result.ok,
    status: result.status,
    detail: result.detail,
    responseText:
      result.outputText,
    providerResponseId:
      result.responseId,
    model: result.model,
  };
}
