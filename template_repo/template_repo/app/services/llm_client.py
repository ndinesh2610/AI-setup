import httpx
from pydantic import BaseModel, Field

from app.config import Settings, get_settings


class LLMMessage(BaseModel):
    """Message returned by the LLM."""

    content: str


class LLMChoice(BaseModel):
    """One completion choice."""

    message: LLMMessage


class LLMResponse(BaseModel):
    """Validated LLM API response."""

    choices: list[LLMChoice] = Field(min_length=1)


class LLMClient:
    """Client for communicating with an OpenAI-compatible LLM API."""

    def __init__(
        self,
        settings: Settings | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """Initialize the client with application settings."""
        self.settings = settings or get_settings()

        self.client = httpx.Client(
            base_url=self.settings.llm_base_url.rstrip("/") + "/",
            headers={
                "Authorization": (f"Bearer {self.settings.llm_api_key.get_secret_value()}"),
                "Content-Type": "application/json",
            },
            timeout=self.settings.llm_timeout_seconds,
            transport=transport,
        )

    def complete(self, prompt: str) -> str:
        """Send a prompt and return the model's response."""
        response = self.client.post(
            "chat/completions",
            json={
                "model": self.settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

        response.raise_for_status()
        data = LLMResponse.model_validate(response.json())
        return data.choices[0].message.content

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()
