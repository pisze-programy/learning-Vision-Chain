from typing import TypedDict, Optional, Literal, Dict, Any

GenderType = Literal["male", "female", "none"]

class AgentState(TypedDict):
    task_id: str
    cache_id: Optional[str]
    image_path: str
    gender: GenderType
    features_analysis: Optional[Dict[str, Any]]
    enhancement_specification: Optional[str]
    result_image_url: str
    status: str