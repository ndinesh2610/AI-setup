import json

from pydantic import ValidationError

from app.models.cv import CVData
from app.services.llm_client import LLMClient


def extract_cv(text: str, client: LLMClient) -> CVData:
    prompt = f"""
Extract CV details into JSON with:
full_name, email, phone, location,
years_experience, skills.

CV:
{text}
"""
    for attempt in range(2):
        result = client.complete(prompt)
        try:
            return CVData.model_validate(json.loads(result))
        except (json.JSONDecodeError, ValidationError) as error:
            if attempt == 1:
                raise
            prompt = f"""
Your previous response was invalid:
{error}

Return corrected JSON only, with:
full_name, email, phone, location,
years_experience, skills.

CV:
{text}
"""

    raise RuntimeError("CV extraction failed")
