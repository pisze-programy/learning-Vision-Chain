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

class MaleFeaturesAnalysis(BaseModel):
    lens_simulation_compression: bool = Field(
        description="Is the subject a human face or portrait vulnerable to standard wide-angle focal distortion?"
    )
    frequency_separation_skin: bool = Field(
        description="Is there any visible skin area on the face or neck accessible for professional matte texture optimization?"
    )
    eye_brow_micro_contrast: bool = Field(
        description="Are the subject's eyes, eyelashes, or eyebrows visible in the current framing?"
    )
    jawline_carving_structure: bool = Field(
        description="Is the lower face, jawline, or chin area visible and structurally trackable?"
    )
    beard_stubble_grooming: bool = Field(
        description="Does the subject have any visible facial hair, beard, mustache, or stubble?"
    )
    rembrandt_split_relighting: bool = Field(
        description="Is the image a portrait where original light can be replaced by studio Rembrandt/Split directional patterns?"
    )
    anatomic_dodge_burn: bool = Field(
        description="Are facial dimensions (cheekbones, nose bridge, forehead) visible for standard exposure mapping?"
    )
    shoulder_trapezius_sculpting: bool = Field(
        description="Are the shoulders, neck, or upper torso visible in the framing?"
    )
    depth_masking_bokeh: bool = Field(
        description="Is there a visible background behind the subject that can be isolated using depth mapping?"
    )

class FemaleFeaturesAnalysis(BaseModel):
    is_skin_visible: bool = Field(
        description="Is there any visible skin area on the face, neck, or décolleté accessible for high-end frequency separation and micro-wrinkle smoothing?"
    )
    are_eyes_visible: bool = Field(
        description="Are the subject's eyes, eyelashes, or eyebrows visible and clear enough for catchlight digital sharpening and high-definition lash mapping?"
    )
    is_jawline_visible: bool = Field(
        description="Is the lower face, jawline, or chin contour visible for anatomical liquify modification and double-chin shadow elimination?"
    )
    are_teeth_visible: bool = Field(
        description="Are teeth visible (person is smiling or mouth is open) for bright ivory digital dental bleaching?"
    )
    is_hair_visible: bool = Field(
        description="Is head hair visible and accessible for flyaway cleanup, specular gloss enhancement, and color richness tuning?"
    )
    is_face_contouring_possible: bool = Field(
        description="Are facial dimensions (cheekbones, nose bridge, forehead) visible to execute deep studio Dodge and Burn structure mapping?"
    )
    is_body_visible: bool = Field(
        description="Is the torso, waistline, arms, or silhouette visible in the framing for digital sculpting, waist narrowing, and skin-fold smoothing?"
    )