# Security Boundaries

- Credentials are loaded from environment variables or a local key-file path and are ignored by Git.
- API, health, metrics, reports, browser state, and dashboard responses never return credential values.
- Agent run records retain only the safe model name, key identifier, latency, and error type.
- Gemini output is validated as structured data and can add narrative context only.
- Response actions are a backend enum allowlist. `RESPONSE_MODE=simulation` is the default and performs no infrastructure action.
- Suricata, Zeek, and Wazuh remain adapter interfaces until explicitly connected.
