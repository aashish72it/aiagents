
from langgraph.graph import StateGraph, START, END
from langfuse import observe
from utils.state import AgentState
from tools.calc_agent import calc_tool
from tools.search_agent import search_tool
from tools.sql2dbt_agent import sql2dbt_tool
from utils.prompts import sql2dbt_system_prompt
from config import GROQ_API_KEY, LLM_MODEL, TEMPERATURE, GROQ_ENDPOINT
import requests

# ---------------------------
# Node Definitions
# ---------------------------

@observe(name="generate", as_type="generation")
def generate_node(state: AgentState) -> AgentState:
    """Uses Groq API to refine or generate SQL/dbt code dynamically."""
    if not GROQ_API_KEY:
        return state

    if state.tool == "sql2dbt":
        # Updated prompt to enforce single best model
        user_prompt = (
            "Convert this SQL into ONE best dbt model only. "
            "Include config(materialized='incremental', unique_key='order_id') and loaded_at column. "
            "Do not provide multiple options or explanations. "
            f"SQL:\n{state.context.get('sql') or state.goal}"
        )
        system_prompt = sql2dbt_system_prompt
    else:
        return state

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": TEMPERATURE
    }

    try:
        resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            generated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if generated_text and generated_text.strip():
                state.context["sql"] = generated_text.strip()
            else:
                state.errors.append("Groq returned empty content.")
        else:
            state.errors.append(f"Groq API error: {resp.status_code}, {resp.text}")
    except Exception as e:
        state.errors.append(f"Groq request failed: {e}")

    return state


@observe(name="plan")
def plan_node(state: AgentState) -> AgentState:
    goal = state.goal.lower()
    if any(k in goal for k in ["calc", "calculate", "expression"]):
        state.tool = "calc"
    elif any(k in goal for k in ["dbt", "sql2dbt", "convert sql", "model"]):
        state.tool = "sql2dbt"
    elif any(k in goal for k in ["search", "duckduckgo", "find"]):
        state.tool = "search"
    else:
        state.tool = "search"
    return state


@observe(name="interpret_math")
def interpret_math_node(state: AgentState) -> AgentState:
    """LLM pre-processing for calc tasks: extract arithmetic expression from natural language."""
    if state.tool == "calc" and GROQ_API_KEY:
        user_prompt = (
            f"Extract only the arithmetic expression from this text: {state.goal}. "
            "Return ONLY the expression, no explanation, no words."
        )

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are a math parser. Return only the arithmetic expression."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0
        }

        try:
            resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                expression = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if expression:
                    state.context["expression"] = expression
                else:
                    state.errors.append("LLM did not return an expression.")
            else:
                state.errors.append(f"Groq API error: {resp.status_code}, {resp.text}")
        except Exception as e:
            state.errors.append(f"LLM interpretation failed: {e}")

    return state


@observe(name="execute")
def execute_node(state: AgentState) -> AgentState:
    if state.tool == "calc":
        return calc_tool(state)
    if state.tool == "sql2dbt":
        return sql2dbt_tool(state)
    if state.tool == "search":
        return search_tool(state)
    state.errors.append(f"Unknown tool: {state.tool}")
    return state


@observe(name="explain_calc")
def explain_calc_node(state: AgentState) -> AgentState:
    if state.tool == "calc" and state.result:
        original_prompt = state.goal
        expression = state.result.get("expression")
        value = state.result.get("value")

        user_prompt = (
            f"Original question: {original_prompt}\n"
            f"Computed expression: {expression}\n"
            f"Result: {value}\n\n"
            "Respond to the original question in a helpful way. "
            "Explain the steps clearly and include the final result."
        )

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": ("You are a helpful math assistant."
                        "Use the expression and result to answer the original question clearly.")},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0
        }

        try:
            resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                explanation = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if explanation:
                    state.result["explanation"] = explanation
            else:
                state.errors.append(f"Groq API error: {resp.status_code}, {resp.text}")
        except Exception as e:
            state.errors.append(f"LLM explanation failed: {e}")

    return state


@observe(name="evaluate")
def evaluate_node(state: AgentState) -> AgentState:
    if state.result and not state.errors:
        state.tests_passed = True
        return state

    if state.tool == "calc" and state.errors:
        state.context["expression"] = (state.context.get("expression") or state.goal).replace(" ", "")
    elif state.tool == "search" and (not state.result or not state.result.get("snippets")):
        state.context["query"] = state.goal + " site:docs langgraph"
    elif state.tool == "sql2dbt" and state.errors:
        sql = state.context.get("sql") or state.goal
        if not sql.strip().endswith(";"):
            state.context["sql"] = sql.strip() + ";"
    return state


@observe(name="decide")
def decide_node(state: AgentState) -> AgentState:
    state.attempts = (state.attempts or 0) + 1
    return state

# ---------------------------
# Graph Setup
# ---------------------------

graph = StateGraph(AgentState)
graph.add_node("plan", plan_node)
graph.add_node("interpret_math", interpret_math_node)
graph.add_node("generate", generate_node)
graph.add_node("execute", execute_node)
graph.add_node("explain_calc", explain_calc_node)
graph.add_node("evaluate", evaluate_node)
graph.add_node("decide", decide_node)

graph.add_edge(START, "plan")
graph.add_edge("plan", "interpret_math")
graph.add_conditional_edges(
    "interpret_math",
    lambda state: "generate" if state.tool == "sql2dbt" else "execute"
)
graph.add_conditional_edges(
    "execute",
    lambda state: "explain_calc" if state.tool == "calc" else "evaluate"
)
graph.add_edge("explain_calc", "evaluate")
graph.add_edge("generate", "execute")
graph.add_edge("evaluate", "decide")

graph.add_conditional_edges(
    "decide",
    lambda state: END if (state.tests_passed or state.attempts >= state.max_attempts) else "execute"
)

app = graph.compile()

# ---------------------------
# Runner
# ---------------------------

def run(goal: str, user_id: str = None):
    initial_state = {
        "goal": goal,
        "tool": None,
        "context": {"user_id": user_id} if user_id else {},
        "result": None,
        "errors": [],
        "tests_passed": False,
        "attempts": 0,
        "max_attempts": 3
    }
    out = app.invoke(initial_state)
    return out
