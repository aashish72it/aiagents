from utils.state import AgentState
from tools.calc_agent import calc_tool

def test_calc_tool_basic():
    st = AgentState(goal="2+2", context={"expression": "2+2"})
    out = calc_tool(st)
    assert out.result["value"] == 4
