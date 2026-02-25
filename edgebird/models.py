"""Multi-model LLM interface using litellm."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import litellm


# Suppress litellm telemetry/logging noise
litellm.suppress_debug_info = True
litellm.set_verbose = False

# Default model roster — user can override via config
DEFAULT_MODELS = [
    {"id": "anthropic/claude-sonnet-4-20250514", "label": "claude"},
    {"id": "openai/gpt-4o", "label": "gpt"},
    {"id": "ollama/llama3.2", "label": "llama-local"},
]


@dataclass
class ModelResponse:
    model_id: str
    label: str
    content: str
    usage: dict = field(default_factory=dict)
    error: str | None = None


async def _call_model(
    model_id: str,
    label: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 1.0,
    max_tokens: int = 4096,
) -> ModelResponse:
    """Call a single model via litellm."""
    try:
        response = await litellm.acompletion(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            }
        return ModelResponse(model_id=model_id, label=label, content=content, usage=usage)
    except Exception as e:
        return ModelResponse(
            model_id=model_id, label=label, content="", error=str(e)
        )


async def scatter_multi(
    system_prompt: str,
    user_prompt: str,
    models: list[dict] | None = None,
    temperature: float = 1.0,
    max_tokens: int = 4096,
) -> list[ModelResponse]:
    """Run the same prompt against multiple models concurrently.

    Each model gets identical input. Outputs are independent — no cross-contamination.
    """
    models = models or DEFAULT_MODELS
    tasks = [
        _call_model(
            model_id=m["id"],
            label=m["label"],
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        for m in models
    ]
    return await asyncio.gather(*tasks)


def scatter_multi_sync(
    system_prompt: str,
    user_prompt: str,
    models: list[dict] | None = None,
    temperature: float = 1.0,
    max_tokens: int = 4096,
) -> list[ModelResponse]:
    """Synchronous wrapper for scatter_multi."""
    return asyncio.run(
        scatter_multi(system_prompt, user_prompt, models, temperature, max_tokens)
    )
