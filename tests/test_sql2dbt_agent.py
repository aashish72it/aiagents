
from utils.state import AgentState
from tools.sql2dbt_agent import sql2dbt_tool

def test_sql2dbt_tool_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    st = AgentState(goal="SELECT 42 as answer", context={"sql": "SELECT 42 as answer", "model_name": "answer_model"})
    out = sql2dbt_tool(st)
    assert out.result and "model_path" in out.result
