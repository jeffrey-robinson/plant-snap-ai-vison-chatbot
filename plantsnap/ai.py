from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash"
GENERIC_RESPONSE_ERROR = "I couldn't generate a response. Please try again."


def create_gemini_client(api_key):
    return genai.Client(api_key=api_key)


def create_chat(client):
    return client.chats.create(
        model=PRIMARY_MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )


def send_message(client, chat, parts):
    try:
        response = chat.send_message(parts)
        return response.text or GENERIC_RESPONSE_ERROR, chat, None
    except Exception as error:
        error_text = str(error)
        if "503" not in error_text and "UNAVAILABLE" not in error_text:
            return None, chat, f"Gemini request failed: {error_text}"

    try:
        fallback_chat = client.chats.create(
            model=FALLBACK_MODEL,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            history=chat.get_history(curated=True),
        )
        response = fallback_chat.send_message(parts)
        return response.text or GENERIC_RESPONSE_ERROR, fallback_chat, None
    except Exception:
        return None, chat, "Gemini is temporarily busy. Please try again in a moment."