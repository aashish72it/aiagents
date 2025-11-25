
from graph import run

def test_graph_run_calc():
    out = run("calc 1+1")
    assert out.result
