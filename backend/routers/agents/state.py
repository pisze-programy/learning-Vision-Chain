from typing import TypedDict, Optional, Literal

GenderType = Literal["male", "female", "none"]

class AgentState(TypedDict):
    task_id: str
    cache_id: Optional[str]
    image_path: str
    gender: GenderType
    result_image_url: str
    status: str