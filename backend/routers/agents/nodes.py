import os
import sys
import traceback
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
        skin_part = (
            "Execute high-end commercial frequency separation retouching. Flawlessly smooth out skin tones, micro-wrinkles, and skin folds while strictly preserving natural pore micro-texture. Eliminate blemishes and uneven skin saturation completely."
            if analysis.get("is_skin_visible") else "Maintain baseline skin texture."
        )

        eye_part = (
            "Apply professional digital catchlight to the eyes. Sharpen the iris micro-details, whiten the sclera naturally, and boost contrast. Darken and mathematically align eyelashes and eyebrows for a striking, high-definition editorial gaze."
            if analysis.get("are_eyes_visible") else "Maintain baseline eyes and brows."
        )

        jaw_part = (
            "Execute subtle anatomical liquify transformation on the lower face. Sharpen the jawline contour, eliminate submental fat (double chin shadows), and elevate the chin structure for a sleek, lifted profile."
            if analysis.get("is_jawline_visible") else "Maintain baseline jawline structure."
        )

        teeth_part = (
            "Apply flawless studio dental bleaching, whitening the visible teeth to a realistic bright ivory shade while clearing inner-mouth shadows."
            if analysis.get("are_teeth_visible") else "Maintain baseline mouth state."
        )

        hair_part = (
            "Apply professional hair polish. Digitally remove all stray flyaway hairs, boost global specular hair reflections, and richness of the hair pigmentation tone for a high-gloss fashion finish."
            if analysis.get("is_hair_visible") else "Maintain baseline hair structure."
        )

        contour_part = (
            "Execute deep studio Dodge and Burn mapping. Dramatically sculpt facial dimensions by deepening cheekbone shadows, slimming the nose bridge, and casting professional micro-contrast highlights on the forehead and cheekbones."
            if analysis.get("is_face_contouring_possible") else "Maintain baseline facial lighting."
        )

        body_part = (
            "Execute digital body sculpting and anatomical liquify. Slim the waistline and arms by 5-8%, smooth out skin folds on the torso, correct posture alignment, and enhance the overall silhouette definition to match a fashion magazine layout."
            if analysis.get("is_body_visible") else "Maintain baseline body silhouette."
        )

        prompt = (
            "High-end fashion editorial portrait transformation. Professional image-to-image modification converting the input subject into a polished, magazine-cover luxury version of themselves, maintaining core facial identity but dramatically enhancing aesthetics. "
            "Apply an 85mm portrait lens compression to optimize head proportions and eliminate smartphone wide-angle distortion. "
            "Incorporate a soft, diffused directional ambient illumination. Strictly forbid any solid white outlines, sharp edge halos, or continuous body strokes. All light must blend organically into the subject's skin and hair textures. "
            "Apply professional fashion color grading with warm, glowing skin tones, rich micro-contrast, and deeply saturated clean tones. "
            "Maintain the exact original background composition, forms, and color palette, but apply a heavy, progressive photographic lens blur simulation. The original background must only be blurred, never replaced with new elements or different environments. "
            "Execute the following absolute anatomical and texture modifications:\n\n"
            f"- [Skin & Wrinkles]: {skin_part}\n"
            f"- [Eyes & Lashes]: {eye_part}\n"
            f"- [Jawline Geometry]: {jaw_part}\n"
            f"- [Dental Aesthetics]: {teeth_part}\n"
            f"- [Hair Gloss]: {hair_part}\n"
            f"- [Facial Sculpting]: {contour_part}\n"
            f"- [Body & Silhouette]: {body_part}\n\n"
            "The final output must look like the exact same person, post-processed by a world-class fashion retoucher, looking flawless, elegant, and perfectly attractive without generating any double limbs or broken artifacts. "
            "MANDATORY: Do not add any new elements, objects, or text. Do not change, remove, or replace the original background, only blur its existing content."
        )

    elif gender == "male":
        lens_instruction = "Apply heavy 135mm structural focal flattening and 5% slim face transformation." if analysis.get(
            "lens_simulation_compression") else "Keep original field of view."
        skin_instruction = "Execute advanced low and high frequency split, eliminating tonal defects while enforcing strict matte finish with raw pore preservation." if analysis.get(
            "frequency_separation_skin") else "Keep original skin texture."
        eye_instruction = "Maximize high-frequency micro-contrast on brow hairs and lashes for an intense editorial gaze." if analysis.get(
            "eye_brow_micro_contrast") else "Keep original eyes and brows."
        jaw_instruction = "Execute aggressive anatomical jawline carving, eliminating jaw obloids and widening lower face bone structure." if analysis.get(
            "jawline_carving_structure") else "Keep original jawline structure."
        beard_instruction = "Execute full geometric filling, boosting hair follicle density and edge micro-sharpness." if analysis.get(
            "beard_stubble_grooming") else "Keep original beard state."
        lighting_instruction = (
            "Introduce a soft, highly diffused directional side-glow bleeding organically from the upper-left background. "
            "The light must wrap softly around the texture of the hair and jawline, creating a natural light-bleed (wrap-around effect) "
            "instead of a solid white line. Strictly forbid any continuous uniform outlines, sharp vector-like body strokes, or halo artifacts. "
            "Ensure the lighting remains non-uniform, casting deep organic contrast shadows on the opposite side of the subject."
        ) if analysis.get("rembrandt_split_relighting") else "Keep original lighting conditions."
        contour_instruction = "Execute intense facial restructuring via exposure mapping, accentuating cheekbone cavities, slimming the nose bridge, and deepening the sub-jawline shadow." if analysis.get(
            "anatomic_dodge_burn") else "Keep original facial depth."
        body_instruction = "Execute structural mesh deformation expanding shoulder width and sharpening trapezius posture alignment." if analysis.get(
            "shoulder_trapezius_sculpting") else "Keep original body posture."
        bokeh_instruction = "Execute an optical progressive blur that blends the background smoothly with the subject's edges, avoiding any artificial edge halo artifacts." if analysis.get(
            "depth_masking_bokeh") else "Keep original background clarity."

        prompt = (
            "Professional image-to-image structural modification transforming the input subject into a high-end corporate editorial masculine masterpiece. "
            f"Lens Simulation Specification: {lens_instruction} "
            f"Lighting Architecture: {lighting_instruction} "
            "Enforce a strict matte finish across all surfaces, rejecting any plastic smoothing artifacts, while maximizing high-frequency micro-contrast on skin pores, stubble, and hair follicles. "
            "Execute localized structural transformations strictly according to the following dynamic parameters:\n\n"
            f"-[Skin Texturing]: {skin_instruction}\n"
            f"-[Ocular Definition]: {eye_instruction}\n"
            f"-[Bone Carving]: {jaw_instruction}\n"
            f"-[Facial Hair Optimization]: {beard_instruction}\n"
            f"-[Anatomic Dodge and Burn]: {contour_instruction}\n"
            f"-[Skeletal Silhouette Modification]: {body_instruction}\n"
            f"-[Depth Mapping Falloff]: {bokeh_instruction}\n\n"
            "Preserve the subject's fundamental core identity while executing the structural modifications. "
            "MANDATORY: Do not add any foreign elements, objects, or text. Do not remove existing baseline objects. "
            "The output must strictly be a sharp, high-contrast, matte-finished corporate portrait."
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
            contents=[input_image, specification],
            config=types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    ),
                ]
            )
        )

        candidates = getattr(response, "candidates", [])
        if not candidates:
            return {"status": "FAILED: No candidates returned from model. Check safety filters or API quota."}

        candidate = candidates[0]
        print(f"Finish Reason: {candidate.finish_reason}")

        ratings = getattr(candidate, "safety_ratings", []) or []
        for rating in ratings:
            print(f"Category: {rating.category}, Probability: {rating.probability}, Blocked: {rating.blocked}")

        content = getattr(candidate, "content", None)
        if not content or not getattr(content, "parts", None):
            finish_reason = getattr(candidate, "finish_reason", "UNKNOWN")
            return {"status": f"FAILED: Empty content. Finish reason: {finish_reason}"}

        generated_bytes = None

        parts = getattr(content, "parts", []) if content else []

        for part in parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is not None and hasattr(inline_data, "data"):
                generated_bytes = inline_data.data
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
        exc_type, exc_value, exc_traceback = sys.exc_info()

        full_stack_trace = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )

        print("-" * 60)
        print("CRITICAL GRAPH NODE ERROR CRASH STACK TRACE:")
        print(full_stack_trace)
        print("-" * 60)

        return {
            "status": f"ERROR: Image generation failed. Message: {str(e)}",
            "stack_trace": full_stack_trace
        }