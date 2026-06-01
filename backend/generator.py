# generator.py
from openai import OpenAI
from config import *

_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

def generate(messages: list[dict]) -> str:
    resp = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=600,
    )
    return resp.choices[0].message.content