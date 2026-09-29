"""LLM access via Groq (OpenAI-compatible) with retry + model fallback for flaky calls."""
import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
MODELS = [m.strip() for m in os.getenv("LLM_MODELS", "openai/gpt-oss-120b,qwen/qwen3-32b").split(",")]


def chat(system: str, user: str, temperature: float = 0.2) -> str:
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
    )
    last_err = None
    for model in MODELS:
        for attempt in range(2):
            try:
                r = client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                )
                text = r.choices[0].message.content or ""
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except Exception as e:  # rate limit, format errors, transient network
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"All LLM models failed: {last_err}")
