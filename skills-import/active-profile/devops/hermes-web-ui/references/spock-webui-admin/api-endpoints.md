# Spock WebUI API Endpoints — Response Shapes

Discovered during session fixing "No LLM provider configured" for session
f4ab108a7528.

## GET /api/providers
```json
{
  "providers": [
    {
      "id": "opencode-go",
      "display_name": "OpenCode Go",
      "has_key": false,
      "configurable": true,
      "is_oauth": false,
      "key_source": "none",
      "auth_error": null,
      "models": [...],
      "models_total": 14
    }
  ],
  "active_provider": null
}
```

## GET /api/models
```json
{
  "active_provider": null,
  "default_model": "",
  "configured_model_badges": {},
  "groups": []
}
```

After fixing:
```json
{
  "active_provider": null,
  "default_model": "kimi-k2.6",
  "configured_model_badges": {},
  "groups": [
    {
      "provider": "Default",
      "provider_id": "default",
      "models": [
        {"id": "kimi-k2.6", "label": "Kimi K2.6"}
      ]
    }
  ],
  "aliases": {}
}
```

## GET /api/settings
```json
{
  "default_workspace": "/home/thadd/workspace",
  "onboarding_completed": true,
  "theme": "light",
  "bot_name": "Spock",
  "default_model": "",
  "password_env_var": false,
  "webui_version": "v0.51.92",
  "agent_version": "not detected"
}
```

## POST /api/providers
Request body: `{"provider": "opencode-go", "api_key": "sk-..."}`
Response:
```json
{"ok": true, "provider": "opencode-go", "display_name": "OpenCode Go", "action": "updated"}
```
Removing key (pass `"api_key": ""`):
```json
{"ok": true, "provider": "opencode-go", "display_name": "OpenCode Go", "action": "removed"}
```

## POST /api/default-model
Request body: `{"model": "kimi-k2.6"}`
Response:
```json
{"ok": true, "model": "kimi-k2.6"}
```

## GET /api/health/agent
```json
{
  "alive": true,
  "checked_at": "2026-05-19T10:13:39.927436+00:00",
  "details": {
    "state": "alive",
    "gateway_state": "running",
    "updated_at": "2026-05-19T10:00:23.757404+00:00",
    "active_agents": 0,
    "platform_count": 1,
    "platform_states": {"connected": 1}
  }
}
```
