
import ast
import operator as op
import re
from utils.logger import logger

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def _eval_expr(node):
    if isinstance(node, ast.Num):  # Python <3.8
        return node.n
    if isinstance(node, ast.Constant):  # Python >=3.8
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return operators[ast.USub]
    if isinstance(node, ast.BinOp):
        left = _eval_expr(node.left)
        right = _eval_expr(node.right)
        func = operators[type(node.op)]
        return func(left, right)
    raise ValueError("Unsupported expression")

def extract_expression(text: str) -> str:
    tokens = re.findall(r"[0-9]+(?:\.[0-9]+)?|[+\-*/()]", text)
    if not tokens:
        return ""
    expr = " ".join(tokens)
    expr = re.sub(r"\b0+(\d)", r"\1", expr)
    if not re.search(r"[+\-*/]", expr):
        return ""
    return expr

def calc_tool(state):
    raw_expr = state.context.get("expression") or state.goal.replace("calc", "").strip()
    expr = extract_expression(raw_expr)

    if not expr:
        state.errors.append("No valid arithmetic expression found.")
        return state

    try:
        node = ast.parse(expr, mode='eval').body
        value = _eval_expr(node)
        state.result = {"expression": expr, "value": value}
    except Exception as e:
        state.errors.append(str(e))
        state.errors.append("Unsupported expression")

    return state
