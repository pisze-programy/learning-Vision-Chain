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
