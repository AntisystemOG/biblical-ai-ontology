# WebUI Reasoning Config System

End-to-end reference for how reasoning effort (`none` → `xhigh`) flows from the WebUI chat through the bridge to the agent core.

## Architecture Overview

```
WebUI ChatInput ──► chat.ts store ──► Socket.IO /chat-run ──► server handle-bridge-run ──► agent-bridge client.ts ──► hermes_bridge.py ──► run_agent.py AIAgent ──► provider transport
```

## Effort Levels (Hermes Core)

The agent core (`agent/lmstudio_reasoning.py`) supports these levels:

| Level | Description |
|---|---|
| `none` | No reasoning/thinking output |
| `minimal` | Minimal reasoning |
| `low` | Fast responses with lighter reasoning |
| `medium` | Balances speed and reasoning depth (default) |
| `high` | Greater reasoning depth for complex problems |
| `xhigh` | Extra high reasoning depth |

**Note:** Not all models support all levels. The transport clamps unsupported levels:
- LM Studio: checks `capabilities.reasoning.allowed_options`
- Gemini: maps to `thinkingLevel: low/medium/high`
- Claude (via OpenRouter): maps to `reasoning_effort: low/medium/high`

## Current Limitation (June 2026)

**The reasoning config is read ONCE from `config.yaml` at bridge startup.**

In `hermes_bridge.py`:
```python
def _load_reasoning_config() -> dict[str, Any] | None:
    from hermes_constants import parse_reasoning_effort
    effort = str((_load_cfg().get("agent") or {}).get("reasoning_effort", "") or "").strip()
    return parse_reasoning_effort(effort)
```

This is passed to `AIAgent()` constructor. There is **NO per-run override** in the bridge's `chat()` action or `start_chat()` method.

## Where to Add Per-Chat Override

### 1. WebUI Client
Add `reasoning_effort` to the `runPayload` in `packages/client/src/stores/hermes/chat.ts`:

```typescript
const runPayload = {
  input,
  session_id: sid,
  profile: activeSession.value?.profile || ...,
  model: ...,
  provider: ...,
  reasoning_effort: activeSession.value?.reasoningEffort || 'medium',  // NEW
  queue_id: userMsg.id,
  source: 'cli' as const,
}
```

### 2. WebUI Server
In `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts`, extract `reasoning_effort` from the Socket.IO event data and pass it to `bridge.chat()`:

```typescript
const started = await bridge.chat(
  session_id,
  bridgeInput as AgentBridgeMessage,
  bridgeHistory,
  fullInstructions,
  profile,
  {
    ...(resolvedModel ? { model: resolvedModel } : {}),
    ...(resolvedProvider ? { provider: resolvedProvider } : {}),
    ...(data.reasoning_effort ? { reasoning_effort: data.reasoning_effort } : {}),  // NEW
  },
)
```

### 3. Agent Bridge
Update `AgentBridgeChatOptions` in `packages/server/src/services/hermes/agent-bridge/client.ts`:

```typescript
export interface AgentBridgeChatOptions {
  force_compress?: boolean
  storage_message?: AgentBridgeMessage
  model?: string
  provider?: string
  source?: string
  wait?: boolean
  timeout?: number
  reasoning_effort?: string  // NEW
}
```

Then in `bridge.chat()`, include it in the request payload:
```typescript
...(options.reasoning_effort ? { reasoning_effort: options.reasoning_effort } : {}),
```

### 4. Hermes Bridge Script
In `hermes_bridge.py`, modify `start_chat()` and `_run_chat()` to accept `reasoning_effort`, then construct a per-run `reasoning_config` dict:

```python
reasoning_config = {"enabled": reasoning_effort != "none", "effort": reasoning_effort}
```

Pass this to `AIAgent.chat()` or the internal runner. **Caution:** `AIAgent` currently sets `self.reasoning_config` at init time. The `chat()` method may need to accept an override parameter, or a new per-run setter may be needed.

## Provider-Specific Reasoning Mapping

### OpenAI / Chat Completions (`agent/transports/chat_completions.py`)

For models with reasoning support (Claude 3.7 Sonnet via OpenRouter, OpenAI o1/o3, etc.):
```python
if reasoning_config and reasoning_config.get("enabled") is not False:
    _e = (reasoning_config.get("effort") or "").strip().lower()
    if _e in {"low", "medium", "high"}:
        kwargs["reasoning_effort"] = _e
```

### Anthropic (`agent/transports/anthropic.py`)

Anthropic uses `thinking` blocks with `budget_tokens`. The `reasoning_config` is mapped to a token budget based on model context window.

### Codex (`agent/transports/codex.py`)

Codex models use `reasoning.effort` in the Responses API:
```python
if reasoning_config and reasoning_config.get("enabled") is not False:
    effort = reasoning_config.get("effort", "medium")
    # Codex supports: "low", "medium", "high"
```

### Gemini (`agent/transports/chat_completions.py`)

Uses `_build_gemini_thinking_config()` which maps effort to `thinkingLevel: low/medium/high` and `includeThoughts: True/False`.

## DB Schema Note

The WebUI SQLite DB (`hermes-web-ui.db`) `sessions` table has no `reasoning_effort` column. To persist per-session effort, either:
1. Add a column to the `sessions` table (requires migration)
2. Store it in `settings.json` or session metadata JSON
3. Default to the global config and only override per-message

## Related Files

| File | Role |
|---|---|
| `packages/client/src/components/hermes/chat/ChatInput.vue` | Where the UI slider would live |
| `packages/client/src/stores/hermes/chat.ts` | `sendMessage()` builds the `runPayload` |
| `packages/server/src/services/hermes/run-chat/handle-bridge-run.ts` | Forwards payload to bridge |
| `packages/server/src/services/hermes/agent-bridge/client.ts` | Bridge client, `AgentBridgeChatOptions` |
| `packages/server/src/services/hermes/agent-bridge/hermes_bridge.py` | Bridge script, `_load_reasoning_config()` |
| `/home/thadd/hermes-agent-ui/agent/lmstudio_reasoning.py` | Effort resolution and clamping |
| `/home/thadd/hermes-agent-ui/agent/transports/chat_completions.py` | Provider-specific mapping |
| `/home/thadd/hermes-agent-ui/run_agent.py` | `AIAgent` constructor and `chat()` method |

## Session Reference

Task `t_4fefb013`: "Add per-chat reasoning depth slider (like Claude Desktop) to WebUI" — full acceptance criteria and component breakdown.