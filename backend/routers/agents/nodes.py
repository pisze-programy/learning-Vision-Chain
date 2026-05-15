import asyncio
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .schemas import GenderAnalysis
from .state import AgentState

load_dotenv()
client = genai.Client()

async def image_cache(state: AgentState) -> dict:
    uploaded_file = client.files.upload(file=state["image_path"])

    token_count_response = client.models.count_tokens(
        model="gemini-2.5-flash",
        contents=uploaded_file
    )
    total_tokens = token_count_response.total_tokens

    if total_tokens >= 1024:
        cache = client.caches.create(
            model="gemini-2.5-flash",
            config=types.CreateCachedContentConfig(
                contents=[uploaded_file],
                ttl="300s",
                display_name=f"task_{state['task_id']}"
            )
        )
        return {
            "cache_id": cache.name,
            "status": f"Success, {total_tokens} tokens"
        }

    return {
        "cache_id": None,
        "status": f"Failed, {total_tokens} tokens"
    }

async def gender_classification(state: AgentState) -> dict[str, Any]:
    system_instruction = (
        "You are a strict computer vision classification agent. "
        "Your task is to look for a primary human or character in the image and determine their gender. "
        "CRITICAL: If the image contains only landscapes, objects, text, or abstract art without any clear human or humanoid character, "
        "you MUST set gender_detected to 'none'"
    )

    prompt = "Analyze the image. If a character is present, classify their gender. If no character exists, classify as 'none'"

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=GenderAnalysis,
        temperature=0.0
    )

    if state.get("cache_id"):
        config.cached_content = state["cache_id"]
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
    else:
        uploaded_file = client.files.upload(file=state["image_path"])
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, prompt],
            config=config
        )

    try:
        result = GenderAnalysis.model_validate_json(response.text)
        gender = result.gender_detected.lower()

        prefix = "NO_CHARACTER_DETECTED:" if gender == "none" else f"Gender: {result.gender_detected} ({result.confidence_score})."

        return {
            "gender": gender,
            "status": f"{prefix} Reason: {result.reasoning}"
        }

    except Exception as e:
        return {
            "status": f"Gender classification critical structural error: {str(e)}"
        }