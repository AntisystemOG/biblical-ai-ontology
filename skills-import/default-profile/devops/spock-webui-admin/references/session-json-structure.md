# Spock WebUI Session JSON Structure

When direct-editing session files, these are the critical fields that control
model routing. The rest (messages, tool_calls, context_messages) are chat history.

## Root fields controlling model routing

```json
{
  "session_id": "f4ab108a7528",
  "model": "kimi-k2.6",
  "model_provider": "opencode-go",
  "profile": "default",
  "gateway_routing": null,
  "gateway_routing_history": [],
  "llm_title_generated": false,
  "enabled_toolsets": null
}
```

## Key fields

| Field | Type | Purpose |
|-------|------|---------|
| `model` | string | Model ID used for this session. Example: `kimi-k2.6`, `openai/gpt-5.4-mini` |
| `model_provider` | string or null | Provider ID. Must match a provider the WebUI knows. Example: `opencode-go`, `ollama`, `anthropic` |
| `profile` | string | Spock profile name. Default is `"default"`. Custom profiles have their own `~/.spock/profiles/<name>/config.yaml` |
| `gateway_routing` | string or null | If set, overrides model for gateway-dispatched turns |
| `enabled_toolsets` | list or null | Toolset IDs enabled for this session |

## What we fixed in session f4ab108a7528

Before:
```json
{
  "model": "openai/gpt-5.4-mini",
  "model_provider": null
}
```

After:
```json
{
  "model": "kimi-k2.6",
  "model_provider": "opencode-go"
}
```

The `model_provider: null` was the root cause of "No LLM provider configured"
even though a model string was present. Both fields must be non-null for a
session to route to an LLM.

## _index.json mirror

The `_index.json` file in the same directory contains the same `model` and
`model_provider` fields per session entry. If you edit the session JSON
but not the index, the sidebar may show stale model info until the next
full refresh.
