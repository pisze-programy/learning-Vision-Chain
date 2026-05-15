import json
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from routers.agents import graph
from routers.agents.graph import compiled_graph
from routers.agents.state import AgentState

router = APIRouter(tags=["Agents"])

class StartProcessRequest(BaseModel):
    task_id: str
    filename: str
    targets: List[str]

async def run_agents_stream(task_id: str, file_path: str):
    initial_state = AgentState(
        task_id=task_id,
        image_path=file_path,
        gender='none',
        result_image_url="",
        status="Initializing"
    )

    async for output in compiled_graph.astream(initial_state):
        for node_name, node_data in output.items():
            event_data = {
                "node": node_name,
                "data": node_data,
                "task_id": task_id
            }
            yield f"data: {json.dumps(event_data)}\n\n"


async def event_generator(task_id: str, initial_state: dict):
    async for output in graph.astream(initial_state):
        for node_name, node_data in output.items():
            event_data = {
                "node": node_name,
                "data": node_data,
                "task_id": task_id
            }

            yield f"data: {json.dumps(event_data)}\n\n"