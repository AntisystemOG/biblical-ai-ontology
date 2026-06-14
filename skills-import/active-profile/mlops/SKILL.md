---
name: mlops
version: 1.0.0
description: |
  Machine Learning Operations: model training, inference, evaluation, and deployment.
  Covers HuggingFace Hub, local GGUF inference (llama.cpp), production serving
  (vLLM), prompt optimization (DSPy), model evaluation harnesses, and experiment
  tracking (Weights & Biases).
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mlops, huggingface, llama.cpp, vllm, dspy, evaluation, serving, training, quantization]
    category: mlops
---

# MLOps

Umbrella skill for machine learning operations: model discovery, inference,
training, evaluation, and deployment.

## When to Use

- User asks about running LLMs locally → load the **llama.cpp** or **vLLM** subsection
- User asks about downloading/uploading models or datasets → load the **HuggingFace Hub** subsection
- User asks about optimizing prompts or building RAG pipelines → load the **DSPy** subsection
- User asks about benchmarking models (MMLU, GSM8K, etc.) → load the **Evaluation** subsection
- User asks about experiment tracking → load the **Weights & Biases** subsection

## Platform / Hardware Matrix

| Goal | Tool | Platforms | Hardware |
|------|------|-----------|----------|
| Local CPU inference | llama.cpp | Linux/macOS/Windows | CPU, Apple Silicon, AMD, Intel |
| Production API serving | vLLM | Linux | NVIDIA GPU |
| Model discovery/download | HuggingFace `hf` CLI | All | N/A |
| Prompt optimization | DSPy | All | Cloud/local LM |
| Benchmarking | lm-evaluation-harness | Linux/macOS | CUDA |
| Experiment tracking | W&B | All | N/A |

---

## HuggingFace Hub (`hf` CLI)

Modern CLI for interacting with the HuggingFace Hub.

```bash
curl -LsSf https://hf.co/cli/install.sh | bash -s
hf auth login
hf whoami
hf models list --search "llama-3"
hf datasets list --search "squad"
hf download meta-llama/Llama-3-8B-Instruct
hf upload REPO_ID local_path/
hf upload-large-folder REPO_ID local_path/
hf repos create my-model --private
hf discussions list REPO_ID
```

**Global flags:** `--format json`, `-q` (quiet).

---

## llama.cpp (Local GGUF Inference)

Run quantized models locally. Best for edge deployment, privacy, and CPU inference.

### Install
```bash
brew install llama.cpp   # macOS/Linux
winget install llama.cpp # Windows
```

### Discover & Run
```bash
# Search trending GGUF models
open https://huggingface.co/models?apps=llama.cpp&sort=trending

# Run directly from Hub (recommended)
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0

# Run exact file
llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
  --hf-file Phi-3-mini-4k-instruct-q4.gguf -c 4096
```

### OpenAI-compatible endpoint check
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"Hello"}]}'
```

---

## vLLM (Production Serving)

High-throughput LLM serving with PagedAttention and continuous batching.

```bash
pip install vllm

# Single GPU (7B-13B)
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 --port 8000

# Multi-GPU (30B-70B)
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --quantization awq --port 8000

# Production: caching + metrics
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching --enable-metrics \
  --metrics-port 9090 --host 0.0.0.0
```

---

## DSPy (Prompt Optimization)

Declarative LM programming from Stanford NLP. Build modular pipelines and optimize prompts automatically.

```bash
pip install dspy
```

```python
import dspy

lm = dspy.Claude(model="claude-sonnet-4-5-20250929")
dspy.settings.configure(lm=lm)

class QA(dspy.Signature):
    """Answer questions with short factual answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often 1-5 words")

qa = dspy.Predict(QA)
print(qa(question="Capital of France?").answer)  # Paris

# Chain of Thought for reasoning
cot = dspy.ChainOfThought(QA)
response = cot(question="If John has 5 apples...")
print(response.rationale)  # reasoning steps
```

---

## lm-evaluation-harness

Benchmark LLMs on standard tasks (MMLU, GSM8K, ARC, HellaSwag, etc.).

```bash
pip install lm-eval
lm_eval --model hf --model_args pretrained=meta-llama/Llama-3-8B --tasks mmlu,gsm8k --batch_size 8
```

---

## Weights & Biases (Experiment Tracking)

Log metrics, hyperparameters, artifacts, and model versions.

```bash
pip install wandb
wandb login

# In training script
import wandb
wandb.init(project="my-project", config={"lr": 0.001})
wandb.log({"loss": 0.5, "accuracy": 0.92})
wandb.finish()
```

---

## Session-Specific References

- `references/huggingface-hub-cheatsheet.md` — hf CLI command quick-reference
- `references/llama-cpp-quant-selector.md` — Q4/Q5/Q6/IQ quant selection for RAM constraints
- `references/vllm-production-checklist.md` — Deployment readiness checklist
- `references/dspy-rag-pattern.md` — RAG pipeline with DSPy signatures and retriever modules
- `references/wandb-project-setup.md` — Team project configuration and artifact versioning
