from langgraph.graph import StateGraph, END

from .nodes import gender_classification, image_cache
from .state import AgentState

workflow = StateGraph(AgentState)

workflow.add_node("image_cache", image_cache)
workflow.add_node("gender_classification", gender_classification)

workflow.set_entry_point("image_cache")
workflow.add_edge("image_cache", "gender_classification")
workflow.add_edge("gender_classification", END)

compiled_graph = workflow.compile()