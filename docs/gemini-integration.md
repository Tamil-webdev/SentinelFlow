# Gemini Integration

Gemini runs only in the FastAPI backend. The frontend calls the SOC API and receives redacted operational status; it never receives an API key or accesses Gemini directly.

`GeminiKeyManager` loads `GEMINI_API_KEY_*` variables and, optionally, a locally configured `GEMINI_KEY_FILE`. It recognizes plain one-key-per-line and `NAME=value` files. Credential values stay in memory only. Status responses expose safe identifiers such as `key-01`, never secret values.

The manager distributes requests across healthy keys and isolates invalid credentials. Transient, timeout, and rate-limit failures create a configured cooldown before reuse. This improves fault isolation and availability; it does not bypass or multiply provider/project quotas.

Set `AI_MODE=gemini` and configure `GEMINI_MODEL` to enable the official `google-genai` SDK. Set `AI_MODE=mock` to run deterministic, no-network fallback narratives. The SOC still detects, scores, responds, and reports when Gemini is unavailable.

For Kubernetes, create `gemini-secrets` outside this repository and store `GEMINI_API_KEY_1` (and additional numbered keys if required) there. The supplied manifest marks the reference optional so demo-mode deployment continues without Gemini.

Gemini receives only structured incident facts after deterministic detection. Its output is constrained to `SecurityNarrative` Pydantic JSON and is treated as supplemental analyst context. It cannot select arbitrary commands or execute actions. The response layer retains its enum allowlist and simulation default.
