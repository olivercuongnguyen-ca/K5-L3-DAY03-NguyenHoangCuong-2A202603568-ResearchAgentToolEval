from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class TokenHarborProvider(OpenAIProvider):
    """Token Harbor gateway via its OpenAI-compatible Chat Completions API.

    Configure in .env:
      TOKENHARBOR_API_KEY, TOKENHARBOR_BASE_URL, TOKENHARBOR_MODEL
    """

    def __init__(self) -> None:
        base_url = os.getenv("TOKENHARBOR_BASE_URL")
        if not base_url:
            raise RuntimeError("Missing TOKENHARBOR_BASE_URL (e.g. https://<host>/v1)")
        super().__init__(
            api_key_env="TOKENHARBOR_API_KEY",
            base_url=base_url,
            default_model=os.getenv("TOKENHARBOR_MODEL", "gpt-4o-mini"),
        )
