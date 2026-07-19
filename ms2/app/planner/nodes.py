"""LangGraph node functions for the AI planning agent.

Each function is a single-responsibility graph node that reads from and
writes to PlannerAgentState. Nodes are pure async functions — no side-effects
outside state mutations and necessary I/O.

Graph order:
  intake_node → context_node → plan_node → reflect_node
"""
import os
import json
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.state import PlannerAgentState
from app.planner.neo4j_context import fetch_relevant_subgraph
from app.planner.llm_client import get_llm, get_fallback_llm
from app.config.logger import get_logger

logger = get_logger("ms2.planner.nodes")

# ---------------------------------------------------------------------------
# System prompt for the plan_node — instructs the LLM output format exactly.
# ---------------------------------------------------------------------------
_PLANNER_SYSTEM_PROMPT = """You are a senior software engineer generating a structured test plan.

Given a list of repository files with their paths, language and labels, produce a JSON test plan.

Rules:
- Return ONLY valid JSON — no markdown, no explanation.
- The JSON must have this exact shape:
  {
    "summary": "<one-line description of what will be tested>",
    "language": "<detected language>",
    "framework": "<detected framework or 'unknown'>",
    "testCases": [
      {
        "id": "TC-001",
        "target": "<file path being tested>",
        "description": "<what this test verifies>",
        "type": "<unit|integration|e2e>",
        "priority": "<high|medium|low>"
      }
    ],
    "coverage": {
      "endpoints": <int>,
      "services": <int>,
      "models": <int>
    }
  }
- Generate between 5 and 20 test cases.
- Focus on endpoints, services, and authentication logic first.
- Never invent file paths — only use paths from the provided context.
"""


async def intake_node(state: PlannerAgentState) -> PlannerAgentState:
    """Validate inputs and return initial state with empty placeholders."""
    logger.info(
        "intake_node | analysisId=%s path=%s",
        state["analysisId"],
        state["repositoryPath"],
    )
    return {
        **state,
        "plan": None,
        "testCases": [],
        "executionResults": [],
        "findings": [],
        "report": None,
        "graph": {},
    }


async def context_node(state: PlannerAgentState) -> PlannerAgentState:
    """Query Neo4j and populate state.graph with relevant code nodes."""
    logger.info("context_node | fetching Neo4j subgraph")
    subgraph = await fetch_relevant_subgraph(state["analysisId"])
    logger.info("context_node | nodes=%d", subgraph.get("total", 0))
    return {**state, "graph": subgraph}


def _generate_mock_plan(state: PlannerAgentState) -> dict:
    """Generate a structured test plan based on detected files when LLM is unavailable."""
    nodes = state["graph"].get("nodes", [])
    test_cases = []
    
    # Generate some mock test cases based on nodes
    for i, node in enumerate(nodes[:8]):
        path = node.get("path", "unknown")
        labels = node.get("labels", [])
        primary_label = labels[-1] if len(labels) > 1 else "File"
        
        test_cases.append({
            "id": f"TC-{i+1:03d}",
            "target": path,
            "description": f"Verify the behavior and core functions of the {primary_label} component.",
            "type": "unit" if primary_label in ["Service", "Model"] else "integration",
            "priority": "high" if i < 2 else "medium"
        })
        
    return {
        "summary": "Mock test plan generated automatically because no OpenAI API key was configured.",
        "language": state.get("language", "Unknown"),
        "framework": state.get("framework", "unknown"),
        "testCases": test_cases,
        "coverage": {
            "endpoints": sum(1 for n in nodes if "Endpoint" in n.get("labels", [])),
            "services": sum(1 for n in nodes if "Service" in n.get("labels", [])),
            "models": sum(1 for n in nodes if "Model" in n.get("labels", []))
        }
    }


async def plan_node(state: PlannerAgentState) -> PlannerAgentState:
    """Send Neo4j context to GPT and receive a structured test plan JSON."""
    logger.info("plan_node | checking environment and API keys")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("OPENAI_API_KEY is not configured or is a placeholder. Using mock test planner.")
        plan = _generate_mock_plan(state)
        return {**state, "plan": plan}

    logger.info("plan_node | sending context to LLM")
    nodes = state["graph"].get("nodes", [])
    user_prompt = (
        f"Repository language: {state['language']}\n"
        f"Framework: {state['framework']}\n\n"
        f"Files found ({len(nodes)} total):\n"
        + "\n".join(
            f"  - [{', '.join(n.get('labels', []))}] {n.get('path', 'unknown')}"
            for n in nodes[:100]  # cap to avoid token overflow
        )
    )

    messages = [
        SystemMessage(content=_PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    # Try primary model first; fall back to gpt-4o on any API error.
    try:
        llm = get_llm()
        response = await llm.ainvoke(messages)
    except Exception as primary_err:
        logger.warning(
            "plan_node | primary model failed (%s) — using fallback", primary_err
        )
        try:
            llm = get_fallback_llm()
            response = await llm.ainvoke(messages)
        except Exception as fallback_err:
            logger.error("plan_node | fallback model also failed: %s", fallback_err)
            raise

    raw_content = response.content.strip()

    # Parse the JSON response from the LLM.
    try:
        plan = json.loads(raw_content)
    except json.JSONDecodeError:
        # Attempt to extract JSON if the model added wrapping text despite the prompt.
        start = raw_content.find("{")
        end = raw_content.rfind("}") + 1
        if start != -1 and end > start:
            plan = json.loads(raw_content[start:end])
        else:
            raise ValueError(f"LLM returned non-JSON plan: {raw_content[:200]}")

    logger.info(
        "plan_node | plan generated | testCases=%d",
        len(plan.get("testCases", [])),
    )
    return {**state, "plan": plan}


async def reflect_node(state: PlannerAgentState) -> PlannerAgentState:
    """Validate the plan and extract testCases into state.testCases.

    Flags low-priority issues but does not fail — reflection is best-effort.
    """
    plan = state.get("plan") or {}
    test_cases = plan.get("testCases", [])

    # Warn if coverage looks low.
    if len(test_cases) < 3:
        logger.warning(
            "reflect_node | low coverage — only %d test cases generated",
            len(test_cases),
        )

    # Ensure each test case has required fields.
    validated = []
    for i, tc in enumerate(test_cases):
        if not tc.get("target") or not tc.get("description"):
            logger.warning("reflect_node | skipping malformed test case index=%d", i)
            continue
        validated.append(tc)

    logger.info("reflect_node | validated testCases=%d", len(validated))
    return {**state, "testCases": validated}
