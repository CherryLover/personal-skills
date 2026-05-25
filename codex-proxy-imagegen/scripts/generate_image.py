#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ENDPOINT_ENV = "CODEX_PROXY_IMAGEGEN_URL"
API_KEY_ENV = "CODEX_PROXY_IMAGEGEN_API_KEY"
MODEL_ENV = "CODEX_PROXY_IMAGEGEN_MODEL"
DEFAULT_MODEL = "gpt-5.5"


@dataclass(frozen=True)
class ProxyConfig:
    endpoint: str
    api_key: str
    model: str = DEFAULT_MODEL


@dataclass(frozen=True)
class ImageResult:
    image_bytes: bytes
    revised_prompt: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ImageGenerationError(RuntimeError):
    pass


def load_proxy_config() -> ProxyConfig:
    endpoint = os.environ.get(ENDPOINT_ENV, "").strip()
    api_key = os.environ.get(API_KEY_ENV, "").strip()
    model = os.environ.get(MODEL_ENV, DEFAULT_MODEL).strip() or DEFAULT_MODEL

    missing = [name for name, value in ((ENDPOINT_ENV, endpoint), (API_KEY_ENV, api_key)) if not value]
    if missing:
        raise ImageGenerationError("Missing required environment variable(s): " + ", ".join(missing))

    return ProxyConfig(endpoint=endpoint, api_key=api_key, model=model)


def build_image_request(prompt: str, model: str, size: str, quality: str) -> dict[str, Any]:
    return {
        "model": model,
        "stream": True,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    }
                ],
            }
        ],
        "tools": [
            {
                "type": "image_generation",
                "size": size,
                "quality": quality,
            }
        ],
    }


def request_image_sse(config: ProxyConfig, payload: dict[str, Any], timeout: int = 300) -> str:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        config.endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ImageGenerationError(f"Image API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ImageGenerationError(f"Image API request failed: {exc.reason}") from exc


def extract_image_result(sse_text: str) -> ImageResult:
    stripped = sse_text.lstrip()
    if stripped.startswith("{"):
        payload = json.loads(stripped)
        if "error" in payload:
            raise ImageGenerationError(json.dumps(payload["error"], ensure_ascii=False))
        raise ImageGenerationError("Expected SSE stream, got JSON without image result")

    for event, data in iter_sse_events(sse_text):
        if event != "response.output_item.done":
            continue
        payload = json.loads(data)
        item = payload.get("item", {})
        if item.get("type") != "image_generation_call" or not item.get("result"):
            continue

        metadata = {
            key: item.get(key)
            for key in ("status", "size", "quality", "output_format", "background", "action")
            if key in item
        }
        return ImageResult(
            image_bytes=base64.b64decode(item["result"]),
            revised_prompt=item.get("revised_prompt") or "",
            metadata=metadata,
        )

    raise ImageGenerationError("No image_generation_call result found in SSE response")


def save_image_result(result: ImageResult, out_path: Path, force: bool = False) -> Path:
    if out_path.exists() and not force:
        raise FileExistsError(f"Output already exists: {out_path} (use --force to overwrite)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(result.image_bytes)

    revised_prompt = result.revised_prompt.strip()
    if revised_prompt:
        out_path.with_suffix(".revised-prompt.txt").write_text(revised_prompt, encoding="utf-8")
    if result.metadata:
        out_path.with_suffix(".metadata.json").write_text(
            json.dumps(result.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return out_path


def iter_sse_events(sse_text: str):
    for block in sse_text.split("\n\n"):
        if not block.strip():
            continue
        event = ""
        data_lines: list[str] = []
        for line in block.splitlines():
            if line.startswith("event: "):
                event = line[len("event: ") :]
            elif line.startswith("data: "):
                data_lines.append(line[len("data: ") :])
        if data_lines:
            yield event, "\n".join(data_lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate images through the configured /responses-compatible image proxy."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Text prompt for image generation")
    prompt_group.add_argument("--prompt-file", type=Path, help="Read the prompt from a UTF-8 text file")
    parser.add_argument("--out", type=Path, required=True, help="Output PNG path")
    parser.add_argument("--model", help=f"Model name; default reads {MODEL_ENV} or falls back to {DEFAULT_MODEL}")
    parser.add_argument("--size", default="1024x1536", help="Image size, for example 1024x1536")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds")
    parser.add_argument("--save-raw-sse", type=Path, help="Optional path to save the raw SSE response")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    args = parser.parse_args()

    try:
        prompt = args.prompt if args.prompt is not None else args.prompt_file.read_text(encoding="utf-8")
        config = load_proxy_config()
        model = args.model or config.model
        payload = build_image_request(prompt=prompt, model=model, size=args.size, quality=args.quality)

        print(f"Endpoint: {config.endpoint}")
        print(f"Model: {model}")
        print("Calling image generation proxy; this may take a few minutes...")

        sse_text = request_image_sse(config=config, payload=payload, timeout=args.timeout)
        if args.save_raw_sse:
            args.save_raw_sse.parent.mkdir(parents=True, exist_ok=True)
            args.save_raw_sse.write_text(sse_text, encoding="utf-8")
        result = extract_image_result(sse_text)
        save_image_result(result, args.out, force=args.force)
    except (OSError, ImageGenerationError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote: {args.out}")
    if result.revised_prompt:
        print(f"Wrote: {args.out.with_suffix('.revised-prompt.txt')}")
    if result.metadata:
        print(f"Wrote: {args.out.with_suffix('.metadata.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
