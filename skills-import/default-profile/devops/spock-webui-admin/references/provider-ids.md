# Spock WebUI Provider IDs and Model IDs

Canonical provider IDs used in the WebUI (from api/config.py and api/providers.py).
These are the exact strings to pass to `/api/providers` and `/api/default-model`.

## Providers with env-var key support

| ID | Display Name | Env Var | Notes |
|----|-------------|---------|-------|
| `opencode-go` | OpenCode Go | `OPENCODE_GO_API_KEY` | Flat-rate $10/mo |
| `opencode-zen` | OpenCode Zen | `OPENCODE_ZEN_API_KEY` | Pay-as-you-go credits |
| `kimi-coding` | Kimi / Moonshot | `KIMI_API_KEY` | Moonshot v1, kimi-latest, kimi-k2.5 |
| `anthropic` | Anthropic | `ANTHROPIC_API_KEY` | Claude Opus/Sonnet/Haiku |
| `openai` | OpenAI | `OPENAI_API_KEY` | GPT-5.x family |
| `deepseek` | DeepSeek | `DEEPSEEK_API_KEY` | V4 Pro/Flash, Reasoner |
| `gemini` | Gemini | `GEMINI_API_KEY` | 3.x Pro/Flash, 2.5 Pro/Flash |
| `google` | Google | `GEMINI_API_KEY` | Same models as gemini provider |
| `minimax` | MiniMax | `MINIMAX_API_KEY` | M2.7, M2.5, M2.1 |
| `minimax-cn` | MiniMax (China) | `MINIMAX_API_KEY` | Chinese endpoint |
| `mistralai` | Mistral | `MISTRAL_API_KEY` | Large, Small |
| `nvidia` | NVIDIA NIM | `NVIDIA_API_KEY` | Nemotron, Llama 3.3 |
| `qwen` | Qwen | `QWEN_API_KEY` | Qwen3 Coder, Qwen3.6 Plus |
| `x-ai` | xAI | `XAI_API_KEY` | Grok 4.20 |
| `xiaomi` | Xiaomi | `XIAOMI_API_KEY` | MiMo v2.x |
| `zai` | Z.AI / GLM | `ZAI_API_KEY` or `GLM_API_KEY` | GLM-5.x family |
| `ollama-cloud` | Ollama Cloud | `OLLAMA_API_KEY` | Cloud-hosted models |
| `openrouter` | OpenRouter | `OPENROUTER_API_KEY` | Router for many models |
| `lmstudio` | LM Studio | `LMSTUDIO_API_KEY` | Local LM Studio server |

## OAuth providers (no API key — configure via CLI OAuth flow)

| ID | Display Name |
|----|-------------|
| `copilot` | GitHub Copilot |
| `copilot-acp` | Copilot ACP |
| `nous` | Nous Portal |
| `openai-codex` | OpenAI Codex |
| `qwen-oauth` | Qwen OAuth |
| `xai-oauth` | xAI Grok OAuth |

## Local / no-key providers

| ID | Display Name | Notes |
|----|-------------|-------|
| `ollama` | Ollama | Local server at localhost:11434 |
| `huggingface` | HuggingFace | No key required for some endpoints |
| `alibaba` | Alibaba | No key required |
| `meta-llama` | Meta Llama | No key required |

## Key model IDs by provider (selected)

### opencode-go
- `kimi-k2.6`
- `kimi-k2.5`
- `deepseek-v4-pro`
- `deepseek-v4-flash`
- `glm-5.1`
- `glm-5`
- `mimo-v2.5-pro`
- `qwen3.6-plus`

### kimi-coding
- `kimi-k2.5`
- `kimi-latest`
- `moonshot-v1-8k`
- `moonshot-v1-32k`
- `moonshot-v1-128k`

### anthropic
- `claude-opus-4.7`
- `claude-sonnet-4.6`
- `claude-haiku-4-5`

### openai
- `gpt-5.5`
- `gpt-5.5-mini`
- `gpt-5.4`
- `gpt-5.4-mini`
