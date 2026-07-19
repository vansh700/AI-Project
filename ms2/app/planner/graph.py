"""LangGraph StateGraph assembly for the AI planner.

Wires intake → context → plan → reflect in a simple linear pipeline
and compiles it into an executable graph.
"""
from langgraph.graph import StateGraph, END
from app.planner.state import PlannerAgentState
from app.planner.nodes import (
    intake_node,
    context_node,
    plan_node,
    reflect_node,
)

_compiled_graph = None


def get_planner_graph():
    """Return the compiled LangGraph planner (created once, reused per process)."""
    global _compiled_graph
    if _compiled_graph is None:
        builder = StateGraph(PlannerAgentState)

        builder.add_node("intake", intake_node)
        builder.add_node("context", context_node)
        builder.add_node("plan", plan_node)
        builder.add_node("reflect", reflect_node)

        # Linear pipeline — no conditional edges in Phase 6
        builder.set_entry_point("intake")
        builder.add_edge("intake", "context")
        builder.add_edge("context", "plan")
        builder.add_edge("plan", "reflect")
        builder.add_edge("reflect", END)

        _compiled_graph = builder.compile()

    return _compiled_graph
