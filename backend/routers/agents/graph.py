from langgraph.graph import StateGraph, END

from .nodes import gender_classification, image_cache, image_retouch_specifier, feature_analysis, \
    execute_image_enhancement
from .state import AgentState

workflow = StateGraph(AgentState)

workflow.add_node("image_cache", image_cache)
workflow.add_node("gender_classification", gender_classification)
workflow.add_node("feature_analysis", feature_analysis)
workflow.add_node("image_retouch_specifier", image_retouch_specifier)
workflow.add_node("execute_image_enhancement", execute_image_enhancement)

workflow.set_entry_point("image_cache")
workflow.add_edge("image_cache", "gender_classification")
workflow.add_edge("gender_classification", "feature_analysis")
workflow.add_edge("feature_analysis", "image_retouch_specifier")
workflow.add_edge("image_retouch_specifier", "execute_image_enhancement")
workflow.add_edge("execute_image_enhancement", END)

compiled_graph = workflow.compile()