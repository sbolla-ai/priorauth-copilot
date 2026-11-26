"""Thin model-provider clients. Each returns (text, usage). Keys come from the environment only."""
from __future__ import annotations

import os


class ProviderError(RuntimeError):
    pass


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, model: str | None = None):
        try:
            import anthropic
        except ImportError as e:
            raise ProviderError("pip install '.[anthropic]' to use the Anthropic provider") from e
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ProviderError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic()
        self.model = model or os.getenv("PRIORAUTH_MODEL", "claude-sonnet-5-5")

    def complete(self, system: str, user: str) -> tuple[str, dict]:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")
        return text, {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}


class OpenAIProvider:
    name = "openai"

    def __init__(self, model: str | None = None):
        try:
            import openai
        except ImportError as e:
            raise ProviderError("pip install '.[openai]' to use the OpenAI provider") from e
        if not os.getenv("OPENAI_API_KEY"):
            raise ProviderError("OPENAI_API_KEY is not set")
        self.model = model or os.getenv("PRIORAUTH_MODEL")
        if not self.model:
            raise ProviderError("Set PRIORAUTH_MODEL to the OpenAI model you want to evaluate")
        self.client = openai.OpenAI()

    def complete(self, system: str, user: str) -> tuple[str, dict]:
        resp = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        usage = {"input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens}
        return resp.choices[0].message.content or "", usage


def get_provider(name: str, model: str | None = None):
    providers = {"anthropic": AnthropicProvider, "openai": OpenAIProvider}
    if name not in providers:
        raise ProviderError(f"Unknown provider '{name}'. Choose one of: {', '.join(providers)} (or use --extractor baseline)")
    return providers[name](model)
