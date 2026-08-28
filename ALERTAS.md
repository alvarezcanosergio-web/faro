# FARO - Alertas de tarifas LLM

Ultima vigilancia: **2026-08-28T182813 UTC** | Modelos vigilados: **388**

**Resumen:** 12 subidas | 7 bajadas | 8 lanzamientos | 37 retiradas | 6 cambios de contexto

## Subidas de precio

- **`google/gemini-3.7-flash`** (in): $0.38/M -> $0.75/M (**+100.0%**)
- **`google/gemini-3.7-flash`** (out): $1.88/M -> $3.75/M (**+100.0%**)
- **`~google/gemini-flash-latest`** (in): $0.38/M -> $0.75/M (**+100.0%**)
- **`~google/gemini-flash-latest`** (out): $1.88/M -> $3.75/M (**+100.0%**)
- **`deepseek/deepseek-v4-flash-0731`** (in): $0.05/M -> $0.06/M (**+20.0%**)
- **`deepseek/deepseek-v4-flash-0731`** (out): $0.10/M -> $0.12/M (**+20.0%**)
- **`qwen/qwen3.5-122b-a10b`** (out): $2.08/M -> $2.40/M (**+15.4%**)
- **`qwen/qwen3.5-122b-a10b`** (in): $0.26/M -> $0.29/M (**+11.5%**)
- **`deepseek/deepseek-v4-flash`** (in): $0.08/M -> $0.09/M (**+11.3%**)
- **`deepseek/deepseek-v4-flash`** (out): $0.16/M -> $0.17/M (**+11.3%**)
- **`deepseek/deepseek-v3.2`** (out): $0.38/M -> $0.40/M (**+5.3%**)
- **`deepseek/deepseek-v3.2`** (in): $0.26/M -> $0.27/M (**+3.5%**)

## Bajadas de precio (oportunidades)

- `deepseek/deepseek-v4-pro-0813` (in): $1.12/M -> $0.66/M (-41.2%)
- `deepseek/deepseek-v4-pro-0813` (out): $3.37/M -> $1.98/M (-41.2%)
- `nvidia/nemotron-3-ultra-550b-a55b` (out): $3.60/M -> $2.20/M (-38.9%)
- `nvidia/nemotron-3-ultra-550b-a55b` (in): $0.60/M -> $0.50/M (-16.7%)
- `deepseek/deepseek-v4-pro` (in): $0.87/M -> $0.75/M (-13.6%)
- `deepseek/deepseek-v4-pro` (out): $1.74/M -> $1.50/M (-13.6%)
- `~z-ai/glm-latest` (in): $1.40/M -> $1.25/M (-10.7%)

## Nuevos modelos

- `mistralai/codestral-2508:batch` entrada $0.30/M / salida $0.90/M / ctx 256000
- `mistralai/ministral-8b-2512:batch` entrada $0.15/M / salida $0.15/M / ctx 262144
- `mistralai/mistral-large-2512:batch` entrada $0.50/M / salida $1.50/M / ctx 262144
- `mistralai/mistral-medium-3-5:batch` entrada $0.75/M / salida $3.75/M / ctx 262144
- `mistralai/mistral-medium-3.1:batch` entrada $0.40/M / salida $2.00/M / ctx 131072
- `mistralai/mistral-small-2603:batch` entrada $0.15/M / salida $0.60/M / ctx 262144
- `qwen/qwen3.8-2.4t-a95b:batch` entrada $2.00/M / salida $6.00/M / ctx 1010000
- `tencent/hy4-preview` entrada $0.83/M / salida $2.50/M / ctx 1048576

## Modelos retirados

- `moonshotai/kimi-k2.7-code:batch`
- `openai/gpt-3.5-turbo:batch`
- `openai/gpt-4-turbo:batch`
- `openai/gpt-4.1-mini:batch`
- `openai/gpt-4.1-nano:batch`
- `openai/gpt-4.1:batch`
- `openai/gpt-4o-mini:batch`
- `openai/gpt-4o:batch`
- `openai/gpt-5-codex:batch`
- `openai/gpt-5-mini:batch`
- `openai/gpt-5-nano:batch`
- `openai/gpt-5-pro:batch`
- `openai/gpt-5.1:batch`
- `openai/gpt-5.2-pro:batch`
- `openai/gpt-5.2:batch`
- ... y 22 mas (ver events/*.json)

## Cambios de contexto

- `google/gemma-3-27b-it`: 262,144 -> 131,072 tokens
- `kwaipilot/kat-coder-pro-v2.5`: 256,000 -> 262,144 tokens
- `mistralai/voxtral-small-24b-2507`: 32,000 -> 32,768 tokens
- `nvidia/nemotron-3-ultra-550b-a55b`: 512,288 -> 262,144 tokens
- `z-ai/glm-5.3`: 1,048,576 -> 1,310,720 tokens
- `~z-ai/glm-latest`: 1,048,576 -> 1,310,720 tokens
