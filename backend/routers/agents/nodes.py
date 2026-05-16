import os
from typing import Any, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types, Client

from .schemas import GenderAnalysis, MaleFeaturesAnalysis, FemaleFeaturesAnalysis
from .state import AgentState

load_dotenv()
client = genai.Client()

IMAGE_result_image_directory = "../storage"

def generate_vision_content(
        client: Client,
        image_path: str,
        prompt: str,
        config: types.GenerateContentConfig,
        cache_id: Optional[str] = None,
        model: str = "gemini-2.5-flash"
) -> types.GenerateContentResponse:
    if cache_id:
        config.cached_content = cache_id
        return client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )

    if not image_path:
        raise ValueError("Execution failed: 'image_path' is missing or None")

    uploaded_file = client.files.upload(file=image_path)

    return client.models.generate_content(
        model=model,
        contents=[uploaded_file, prompt],
        config=config
    )

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

    response = generate_vision_content(
        client=client,
        image_path=state["image_path"],
        prompt=prompt,
        config=config,
        cache_id=state.get("cache_id")
    )

    try:
        result = GenderAnalysis.model_validate_json(response.text)
        gender = result.gender_detected.lower()

        prefix = "NO_CHARACTER_DETECTED:" if gender == "none" else f"Gender: {result.gender_detected} ({result.confidence_score})"

        return {
            "gender": gender,
            "status": f"{prefix} Reason: {result.reasoning}"
        }

    except Exception as e:
        return {
            "status": f"Gender classification critical structural error: {str(e)}"
        }


def feature_analysis(state: AgentState):
    gender = state.get("gender")

    prompt = f"Analyze the {gender} subject in the image and fill out the schema with intensities and feature visibility"

    if gender == "male":
        selected_schema = MaleFeaturesAnalysis
    elif gender == "female":
        selected_schema = FemaleFeaturesAnalysis
    else:
        return {"status": "SKIPPED: No character to analyze features"}

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=selected_schema,
        temperature=0.1
    )

    try:
        response = generate_vision_content(
            client=client,
            image_path=state.get("image_path"),
            prompt=prompt,
            config=config,
            cache_id=state.get("cache_id")
        )

        analysis_result = selected_schema.model_validate_json(response.text)

        return {
            "features_analysis": analysis_result.model_dump(),
            "status": f"SUCCESS: Feature analysis completed for {gender}"
        }

    except Exception as e:
        return {
            "status": f"ERROR: Feature analysis failed. Details: {str(e)}"
        }


def image_retouch_specifier(state: AgentState):
    gender = state.get("gender")
    analysis = state.get("features_analysis")

    if not analysis:
        return {"status": "FAILED: No features analysis data available to inject into templates"}

    if gender == "female":
        skin_val = analysis["skin_retouching_intensity"] if analysis.get("is_skin_visible") else 0
        eye_val = analysis["eye_enhancement_intensity"] if analysis.get("are_eyes_visible") else 0
        jaw_val = analysis["jawline_definition_intensity"] if analysis.get("is_jawline_visible") else 0
        teeth_val = analysis["dental_aesthetic_intensity"] if analysis.get("are_teeth_visible") else 0
        hair_val = analysis["hair_polish_intensity"] if analysis.get("is_hair_visible") else 0
        contour_val = analysis["contouring_dodge_burn_intensity"] if analysis.get("is_face_contouring_possible") else 0
        body_val = analysis["body_sculpting_intensity"] if analysis.get("is_body_visible") else 0
        brow_val = analysis["lash_brow_definition_intensity"] if analysis.get("are_brows_visible") else 0
        specular_val = analysis["specular_highlights_intensity"]

        prompt = (
            "Professional image-to-image enhancement transforming the input subject into a flawless, high-end editorial portrait, "
            "utilizing a [Fujifilm GFX 100S, medium format digital camera] aesthetic with ultra-high resolution and natural-looking sharpness. "
            "Explicitly implement a shallow depth of field, resulting in a dramatic and creamy background bokeh (e.g., f/1.4 - f/2.0 separation) "
            "that completely blurs background details while keeping the subject tack-sharp. "
            "Completely replace the original lighting with a professional editorial three-point lighting system: a dominant softbox (key light) "
            "providing a gentle, diffuse glow, a precise rim light for subject separation, and a subtle fill light. Apply a refined [Cinematic Color Grading] "
            "with flattering, warm skin tones, rich micro-contrast, and clean, deep shadows, reminiscent of a high-budget fashion publication. "
            "Ensure precise localized enhancements based on the following scale, where 10 means maximum realistic effect:\n\n"
            f"[Skin Retouching: {skin_val}] (preserving micro-texture),\n"
            f"[Eye Enhancement: {eye_val}] (brightening and defining),\n"
            f"[Jawline Definition: {jaw_val}],\n"
            f"[Dental Aesthetic: {teeth_val}],\n"
            f"[Hair Polish: {hair_val}] (removing stray hairs and adding shine),\n"
            f"[Contouring/Dodge & Burn: {contour_val}],\n"
            f"[Body Sculpting: {body_val}],\n"
            f"[Lash & Brow Definition: {brow_val}],\n"
            f"[Specular Highlights: {specular_val}].\n\n"
            "Maintain full photorealism without artifacts. Preserve the subject's fundamental features and identity, only enhancing them. "
            "MANDATORY: Do not add any new elements, objects, or text. Do not remove any existing objects, only blemishes. "
            "The result must be a clean, sophisticated, editorial portrait"
        )

    elif gender == "male":
        skin_val = analysis["skin_clarity_intensity"] if analysis.get("is_skin_visible") else 0
        eye_val = analysis["eye_brow_intensity"] if analysis.get("are_eyes_visible") else 0
        jaw_val = analysis["jawline_structure_intensity"] if analysis.get("is_jawline_visible") else 0
        teeth_val = analysis["dental_aesthetic_intensity"] if analysis.get("are_teeth_visible") else 0
        beard_val = analysis["beard_grooming_intensity"] if analysis.get("has_beard") else 0
        hair_val = analysis["hair_pigmentation_intensity"] if analysis.get("is_hair_visible") else 0
        contour_val = analysis["masculine_contouring_intensity"] if analysis.get("is_face_contouring_possible") else 0
        body_val = analysis["muscle_definition_intensity"] if analysis.get("is_body_visible") else 0
        specular_val = analysis["specular_highlights_intensity"]

        prompt = (
            "Professional image-to-image enhancement transforming the input subject into a radiant, high-end masculine editorial portrait. "
            "Utilize a [Fujifilm GFX 100S] aesthetic, emphasizing luminous skin textures and vibrant, natural-looking sharpness. "
            "Implement a moderate depth of field (f/2.8 - f/4.0), creating a soft, professional background bokeh that maintains environment context "
            "while keeping the subject as the focus. "
            "Replace original lighting with [Golden Hour Light Professional Session Lighting], featuring a powerful light warm soft light "
            "(simulating sun-drenched flash) and soft ambient fill to eliminate harsh dark shadows. Apply a [Warm, Vibrant Cinematic Color Grading] "
            "with golden undertones, boosted saturation, and rich micro-contrast for a sun-kissed, healthy look. "
            "Execute localized enhancements precisely according to the scale (0 to 10):\n\n"
            f"[Skin Clarity & Vitality: {skin_val}] (healthy glow, removing only blemishes),\n"
            f"[Eye & Brow Intensity: {eye_val}] (sharper gaze, naturally filled brows),\n"
            f"[Jawline & Bone Structure: {jaw_val}] (refined, chiseled definition),\n"
            f"[Dental Aesthetic: {teeth_val}] (natural white),\n"
            f"[Beard & Stubble Grooming: {beard_val}] (perfectly shaped and dense),\n"
            f"[Hair Pigmentation: {hair_val}] (rich, warm tones),\n"
            f"[Masculine Contouring: {contour_val}] (enhancing features with light, not darkness),\n"
            f"[Muscle Definition & Posture: {body_val}],\n"
            f"[Specular Highlights: {specular_val}] (soft glow on cheekbones and forehead to simulate studio flash).\n\n"
            "Preserve the subject's fundamental identity. MANDATORY: Do not add any new elements, objects, or text. "
            "Do not remove any existing objects. The result must be a sharp, sophisticated, masculine masterpiece"
        )
    else:
        return {"status": "SKIPPED: Non-human or undetermined gender, prompt skipped"}

    return {
        "enhancement_specification": prompt,
        "status": "SUCCESS: Final gender-specific generation prompt constructed successfully"
    }


def execute_image_enhancement(state: AgentState):
    specification = state.get("enhancement_specification")
    task_id = state.get("task_id")
    cache_id = state.get("cache_id")
    image_path = state.get("image_path")

    if not specification:
        return {"status": "FAILED: Missing enhancement specification"}

    client = Client()

    try:
        if cache_id:
            input_image = client.files.get(name=cache_id)
        elif image_path:
            input_image = client.files.upload(file=image_path)
        else:
            return {"status": "FAILED: No image source found in state"}

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[input_image, specification]
        )

        generated_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_bytes = part.inline_data.data
                break

        if not generated_bytes:
            return {"status": "FAILED: Response did not contain generated image data"}

        os.makedirs(IMAGE_result_image_directory, exist_ok=True)

        output_filename = f"{task_id}_enhanced.png"
        full_output_path = os.path.join(IMAGE_result_image_directory, output_filename)

        with open(full_output_path, "wb") as output_file:
            output_file.write(generated_bytes)

        return {
            "result_image_url": full_output_path,
            "status": "SUCCESS: Enhanced image generated successfully via multimodal image model"
        }

    except Exception as e:
        return {
            "status": f"ERROR: Image generation failed. Details: {str(e)}"
        }