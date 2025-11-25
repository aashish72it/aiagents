
from utils.logger import logger
from config import DBT_DIR
import os
import re

def sanitize_model_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "generated_model"

def default_dbt_model(sql: str, model_name: str) -> str:
    return f"""{{{{ config(materialized='view') }}}}
-- Auto-generated model: {model_name}
-- NOTE: Review tests & documentation.

{sql.strip()}
"""

def write_model_file(content: str, file_name: str = None, folder: str = DBT_DIR):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, file_name or "model.sql")
    with open(path, "w") as f:
        f.write(content)
    return path

def sql2dbt_tool(state):
    """Converts SQL string in state.context['sql'] to a dbt model file locally."""
    sql = state.context.get("sql") or state.goal
    model_name = sanitize_model_name(state.context.get("model_name", "generated_model"))
    state.attempts += 1
    try:
        content = default_dbt_model(sql, model_name)
        path = write_model_file(content, f"{model_name}.sql")
        state.result = {"model_path": path, "model_name": model_name, "model_content": sql}
        return state
    except Exception as e:
        logger.error(f"sql2dbt_tool error: {e}")
        state.errors.append(str(e))
        return state
