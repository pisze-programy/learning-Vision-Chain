from pydantic import BaseModel, Field

from routers.agents.state import GenderType


class GenderAnalysis(BaseModel):
    gender_detected: GenderType = Field(
        description="Detected gender of the primary character. If no human/character is present, you MUST return 'none'"
    )
    confidence_score: float = Field(
        description="Confidence score of the detection between 0.0 and 1.0. For 'none', set to 1.0 if absolutely sure no human is present")
    reasoning: str = Field(
        description="Brief technical justification for the classification or for the absence of characters")


from pydantic import BaseModel, Field


class MaleFeaturesAnalysis(BaseModel):
    is_skin_visible: bool = Field(description="Is skin visible and accessible for clarity enhancement?")
    skin_clarity_intensity: int = Field(ge=0, le=10, description="Suggested healthy glow/blemish removal intensity")

    are_eyes_visible: bool = Field(description="Are eyes and brows visible for sharpening?")
    eye_brow_intensity: int = Field(ge=0, le=10, description="Suggested sharpness and brow filling intensity")

    is_jawline_visible: bool = Field(description="Is jawline and lower face bone structure visible?")
    jawline_structure_intensity: int = Field(ge=0, le=10, description="Suggested chiseled definition intensity")

    are_teeth_visible: bool = Field(description="Are teeth visible (person is smiling/mouth open)?")
    dental_aesthetic_intensity: int = Field(ge=0, le=10, description="Suggested natural teeth whitening intensity")

    has_beard: bool = Field(description="Does the subject have a visible beard or stubble?")
    beard_grooming_intensity: int = Field(ge=0, le=10, description="Suggested density and shaping intensity")

    is_hair_visible: bool = Field(description="Is head hair visible?")
    hair_pigmentation_intensity: int = Field(ge=0, le=10,
                                             description="Suggested rich, warm tone enhancement intensity")

    is_face_contouring_possible: bool = Field(description="Is the face orientation/lighting suitable for contouring?")
    masculine_contouring_intensity: int = Field(ge=0, le=10,
                                                description="Suggested feature enhancement via light intensity")

    is_body_visible: bool = Field(description="Is the torso/body visible for muscle and posture tracking?")
    muscle_definition_intensity: int = Field(ge=0, le=10,
                                             description="Suggested muscle definition enhancement intensity")

    specular_highlights_intensity: int = Field(ge=0, le=10,
                                               description="Suggested soft studio flash glow intensity on cheekbones/forehead")


class FemaleFeaturesAnalysis(BaseModel):
    is_skin_visible: bool = Field(description="Is skin visible and accessible for retouching?")
    skin_retouching_intensity: int = Field(ge=0, le=10,
                                           description="Suggested micro-texture preserving retouch intensity")

    are_eyes_visible: bool = Field(description="Are eyes clearly visible?")
    eye_enhancement_intensity: int = Field(ge=0, le=10, description="Suggested brightening and definition intensity")

    is_jawline_visible: bool = Field(description="Is the jawline contour visible?")
    jawline_definition_intensity: int = Field(ge=0, le=10, description="Suggested jawline definition intensity")

    are_teeth_visible: bool = Field(description="Are teeth visible (person is smiling/mouth open)?")
    dental_aesthetic_intensity: int = Field(ge=0, le=10, description="Suggested teeth whitening intensity")

    is_hair_visible: bool = Field(description="Is head hair visible?")
    hair_polish_intensity: int = Field(ge=0, le=10, description="Suggested stray hair removal and shine intensity")

    is_face_contouring_possible: bool = Field(description="Is face lighting suitable for Dodge & Burn?")
    contouring_dodge_burn_intensity: int = Field(ge=0, le=10,
                                                 description="Suggested highlights/shadows contouring intensity")

    is_body_visible: bool = Field(description="Is the body/silhouette visible for shaping?")
    body_sculpting_intensity: int = Field(ge=0, le=10, description="Suggested body silhouette sculpting intensity")

    are_brows_visible: bool = Field(description="Are eyelashes and eyebrows visible?")
    lash_brow_definition_intensity: int = Field(ge=0, le=10,
                                                description="Suggested lash and brow definition intensity")

    specular_highlights_intensity: int = Field(ge=0, le=10,
                                               description="Suggested soft studio flash glow intensity on cheekbones/forehead")