import json

from openai import OpenAI

from ..config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Lazily create (and cache) the OpenAI client.

    The client is not instantiated at import time so the app can boot even
    when OPENAI_API_KEY is not set (e.g. in local development or when the
    key hasn't been configured yet in Railway). The client is only created
    the first time it's actually needed, at which point a missing/invalid
    key will surface as a normal request-time error instead of crashing
    the whole application on startup.
    """
    global _client
    if _client is None:
        # Fall back to a placeholder key in development so instantiating the
        # client doesn't raise. Any actual API call will fail with a clear
        # authentication error if the real key isn't configured.
        api_key = settings.OPENAI_API_KEY or "sk-dev-placeholder-key"
        _client = OpenAI(api_key=api_key, timeout=120.0, max_retries=2)
    return _client


def generate_script(niche: str, length_seconds: int) -> dict:
    target_words = int(length_seconds * 2.3)
    prompt = f'''You write viral short-form video scripts for the niche: "{niche}".

Write a script for a {length_seconds}-second faceless video (~{target_words} words spoken).
Rules:
- Hook in the first line (curiosity, bold claim, or question)
- Punchy, spoken-language sentences, no stage directions
- End with a call to action (follow/like/comment) worked in naturally
- Do not use emojis in the spoken script

Return ONLY valid JSON in this exact shape:
{{
  "title": "short catchy title",
  "script": "the full spoken script as one string",
  "caption": "social media caption, under 150 chars, with 1-2 emojis",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
}}'''

    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.9,
    )

    return json.loads(response.choices[0].message.content)
