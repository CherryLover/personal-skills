---
name: codex-proxy-imagegen
description: Use when Codex needs to generate PNG images through a user-provided /responses-compatible image proxy, especially when the endpoint and API key must come from project-specific environment variables instead of local Codex config or OPENAI_API_KEY.
---

# Codex Proxy ImageGen

## Overview

Generate images through a `/responses`-compatible proxy without reading local Codex config. Use the bundled script so endpoint, API key, and model stay isolated in this skill's own environment variables.

## Environment

Require these variables before making a live request:

```bash
export CODEX_PROXY_IMAGEGEN_URL="https://example.com/openai/responses"
export CODEX_PROXY_IMAGEGEN_API_KEY="..."
export CODEX_PROXY_IMAGEGEN_MODEL="gpt-5.5"
```

- `CODEX_PROXY_IMAGEGEN_URL`: required; pass the full request URL, normally ending in `/responses`.
- `CODEX_PROXY_IMAGEGEN_API_KEY`: required; do not ask the user to paste it into chat.
- `CODEX_PROXY_IMAGEGEN_MODEL`: optional; the script falls back to `gpt-5.5`.

Do not use `~/.codex/config.toml`, `~/.codex/auth.json`, `CODEX_HOME`, or `OPENAI_API_KEY` for this skill's runtime configuration.

## Workflow

1. Create or locate a prompt file. For text-heavy images, include the exact text verbatim and ask for readable Chinese if needed.
2. Confirm required environment variables are present without printing the API key.
3. Run the bundled script from this skill directory:

```bash
python3 <skill-dir>/scripts/generate_image.py \
  --prompt-file <prompt.txt> \
  --out <output.png> \
  --size 1024x1536 \
  --quality high \
  --force
```

4. If debugging is needed, add `--save-raw-sse <output.sse>`.
5. Inspect the generated PNG before reporting success. Check file type, dimensions, and visible quality; use an image viewer when available.
6. Report the final image path and mention any generated sidecar files.

## Quick Commands

Check configuration without revealing the key:

```bash
python3 - <<'PY'
import os
for name in ["CODEX_PROXY_IMAGEGEN_URL", "CODEX_PROXY_IMAGEGEN_API_KEY", "CODEX_PROXY_IMAGEGEN_MODEL"]:
    value = os.environ.get(name, "")
    print(name, "SET" if name.endswith("API_KEY") and value else value or "MISSING")
PY
```

Generate from inline prompt:

```bash
python3 <skill-dir>/scripts/generate_image.py \
  --prompt "画一张简洁的中文天气海报" \
  --out output/weather.png \
  --size 1024x1536 \
  --quality high \
  --force
```

Run script help:

```bash
python3 <skill-dir>/scripts/generate_image.py --help
```

## Common Mistakes

- Passing a base URL without `/responses`; this skill expects the full request URL.
- Forgetting that `CODEX_PROXY_IMAGEGEN_API_KEY` is required even if `OPENAI_API_KEY` exists.
- Reporting success before opening or validating the PNG.
- Committing `.sse` files or generated images unless the user explicitly wants them kept in version control.
