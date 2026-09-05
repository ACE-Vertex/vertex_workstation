use reqwest::Client;
use serde::Serialize;
use serde_json::{json, Value};
use std::{env, time::Duration};

const OPENAI_RESPONSES_URL: &str = "https://api.openai.com/v1/responses";
const DEFAULT_OPENAI_MODEL: &str = "gpt-5.6";
const MAX_RELAY_BYTES: usize = 2 * 1024 * 1024;
const MAX_ERROR_TEXT_BYTES: usize = 4096;

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct OpenAiApiStatus {
    available: bool,
    configured: bool,
    model: String,
    credential_source: String,
    endpoint: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct OpenAiApiSendResult {
    ok: bool,
    status: u16,
    detail: String,
    response_id: String,
    model: String,
    output_text: String,
}

fn configured_api_key() -> Result<String, String> {
    let value = env::var("OPENAI_API_KEY")
        .unwrap_or_default()
        .trim()
        .to_string();

    if value.is_empty() {
        return Err("OPENAI_API_KEY_REQUIRED".to_string());
    }

    Ok(value)
}

fn configured_model() -> String {
    let value = env::var("OPENAI_MODEL")
        .unwrap_or_default()
        .trim()
        .to_string();

    if value.is_empty() {
        DEFAULT_OPENAI_MODEL.to_string()
    } else {
        value
    }
}

fn validate_vertex_relay(envelope: &Value) -> Result<(), String> {
    let bytes = serde_json::to_vec(envelope)
        .map_err(|error| format!("OPENAI_RELAY_SERIALIZE_FAILED: {}", error))?;

    if bytes.len() > MAX_RELAY_BYTES {
        return Err("OPENAI_RELAY_PAYLOAD_GT_2M".to_string());
    }

    let schema = envelope.get("schema").and_then(Value::as_str).unwrap_or("");

    if schema != "vertex-relay/1" {
        return Err("OPENAI_RELAY_SCHEMA_INVALID".to_string());
    }

    let source = envelope.get("source").and_then(Value::as_str).unwrap_or("");

    if source != "VERTEX_WORKSTATION" {
        return Err("OPENAI_RELAY_SOURCE_INVALID".to_string());
    }

    let target = envelope.get("target").and_then(Value::as_str).unwrap_or("");

    if target != "VERA" {
        return Err("OPENAI_RELAY_TARGET_INVALID".to_string());
    }

    Ok(())
}

fn extract_output_text(response: &Value) -> String {
    let mut parts = Vec::new();

    let Some(output) = response.get("output").and_then(Value::as_array) else {
        return String::new();
    };

    for item in output {
        let Some(content) = item.get("content").and_then(Value::as_array) else {
            continue;
        };

        for part in content {
            if part.get("type").and_then(Value::as_str) == Some("output_text") {
                if let Some(text) = part.get("text").and_then(Value::as_str) {
                    parts.push(text);
                }
            }
        }
    }

    parts.join("\n")
}

fn bounded_error_text(text: String) -> String {
    let bytes = text.as_bytes();

    if bytes.len() <= MAX_ERROR_TEXT_BYTES {
        return text;
    }

    String::from_utf8_lossy(&bytes[..MAX_ERROR_TEXT_BYTES]).to_string()
}

#[tauri::command]
pub fn openai_api_status() -> OpenAiApiStatus {
    OpenAiApiStatus {
        available: true,
        configured: configured_api_key().is_ok(),
        model: configured_model(),
        credential_source: "ENV:OPENAI_API_KEY".to_string(),
        endpoint: OPENAI_RESPONSES_URL.to_string(),
    }
}

#[tauri::command]
pub async fn openai_api_send_relay(envelope: Value) -> Result<OpenAiApiSendResult, String> {
    validate_vertex_relay(&envelope)?;

    let api_key = configured_api_key()?;
    let model = configured_model();

    let relay_text = serde_json::to_string_pretty(&envelope)
        .map_err(|error| format!("OPENAI_RELAY_SERIALIZE_FAILED: {}", error))?;

    let body = json!({
        "model": model,
        "instructions":
            "You are the model endpoint behind Vertex Relay. \
             Treat the provided vertex-relay/1 envelope as the user's structured intent. \
             Respond to that intent directly and concisely. \
             Do not claim access to the current ChatGPT web conversation, \
             the user's local machine, or Vertex state that is not present in the envelope.",
        "input": relay_text
    });

    let client = Client::builder()
        .timeout(Duration::from_secs(60))
        .build()
        .map_err(|error| format!("OPENAI_HTTP_CLIENT_FAILED: {}", error))?;

    let response = client
        .post(OPENAI_RESPONSES_URL)
        .bearer_auth(api_key)
        .header("Content-Type", "application/json")
        .header("User-Agent", "VertexWorkstation/0.1.0")
        .json(&body)
        .send()
        .await
        .map_err(|error| {
            if error.is_timeout() {
                "OPENAI_API_TIMEOUT".to_string()
            } else {
                format!("OPENAI_API_REQUEST_FAILED: {}", error)
            }
        })?;

    let status = response.status();
    let status_code = status.as_u16();
    let response_text = response
        .text()
        .await
        .map_err(|error| format!("OPENAI_API_RESPONSE_READ_FAILED: {}", error))?;

    if !status.is_success() {
        return Err(format!(
            "OPENAI_API_HTTP_{}: {}",
            status_code,
            bounded_error_text(response_text),
        ));
    }

    let parsed: Value = serde_json::from_str(&response_text)
        .map_err(|error| format!("OPENAI_API_JSON_INVALID: {}", error))?;

    let output_text = extract_output_text(&parsed);

    if output_text.trim().is_empty() {
        return Err("OPENAI_API_EMPTY_OUTPUT".to_string());
    }

    let response_id = parsed
        .get("id")
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string();

    let response_model = parsed
        .get("model")
        .and_then(Value::as_str)
        .unwrap_or(&model)
        .to_string();

    Ok(OpenAiApiSendResult {
        ok: true,
        status: status_code,
        detail: "OPENAI_RESPONSE_READY".to_string(),
        response_id,
        model: response_model,
        output_text,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn relay_validation_accepts_workstation_to_vera() {
        let envelope = json!({
            "schema": "vertex-relay/1",
            "type": "CANONICAL",
            "action": "SHARE",
            "source": "VERTEX_WORKSTATION",
            "target": "VERA",
            "subject": {
                "id": "vcr",
                "name": "Vertex Canonical Registry"
            },
            "timestamp": "2026-09-05T00:00:00Z",
            "payload": {
                "example": true
            }
        });

        assert!(validate_vertex_relay(&envelope).is_ok());
    }

    #[test]
    fn relay_validation_rejects_reverse_direction() {
        let envelope = json!({
            "schema": "vertex-relay/1",
            "source": "VERA",
            "target": "VERTEX_WORKSTATION"
        });

        let error = validate_vertex_relay(&envelope).expect_err("reverse direction must fail");

        assert_eq!(error, "OPENAI_RELAY_SOURCE_INVALID");
    }

    #[test]
    fn output_text_is_extracted_from_responses_shape() {
        let response = json!({
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Vertex response"
                        }
                    ]
                }
            ]
        });

        assert_eq!(extract_output_text(&response), "Vertex response");
    }
}
