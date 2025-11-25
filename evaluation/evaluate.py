
from utils.logger import logger
from tools.calc_agent import calc_tool
from tools.search_agent import search_tool
from tools.sql2dbt_agent import sql2dbt_tool
from utils.state import AgentState

def offline_evaluate():
    cases = [
        ("calc", AgentState(goal="2 + 3 * 5", context={"expression": "2 + 3 * 5"})),
        ("search", AgentState(goal="LangGraph cyclic workflows", context={"query": "LangGraph cyclic workflows"})),
        ("sql2dbt", AgentState(goal="SELECT 1 AS col", context={"sql": "SELECT 1 AS col", "model_name": "sample_model"})),
    ]
    results = []
    for name, state in cases:
        logger.info(f"Evaluating {name}")
        if name == "calc":
            results.append(calc_tool(state).result)
        elif name == "search":
            results.append(search_tool(state).result)
        elif name == "sql2dbt":
            results.append(sql2dbt_tool(state).result)
    logger.info(f"Evaluation results: {results}")
    return results

if __name__ == "__main__":
    offline_evaluate()
