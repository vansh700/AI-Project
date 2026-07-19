"""LangGraph state schema for the AI planning agent.

All nodes in the graph read from and write to this shared state dict.
Fields map directly to the agreed Phase 6 state specification.
"""
from typing import Any
from typing_extensions import TypedDict


class PlannerAgentState(TypedDict):
    """Shared state passed between every node in the planner graph."""

    # Inputs — set by intake_node
    analysisId: str
    repositoryPath: str
    language: str
    framework: str

    # Graph context — populated by context_node
    graph: dict[str, Any]

    # AI output — populated by plan_node
    plan: dict[str, Any] | None

    # Extracted test cases — populated by reflect_node
    testCases: list[dict[str, Any]]

    # Phase 7+ — empty placeholders kept in state for forward compatibility
    executionResults: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    report: dict[str, Any] | None
