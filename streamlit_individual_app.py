import os
import html
import re
import streamlit as st
from graph import run

# ---------------------------
# Small input sanitizer
# ---------------------------
def sanitize(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.strip()
    return text

# ---------------------------
# Page & Status
# ---------------------------
st.set_page_config(page_title="AI Agent", layout="centered")
st.title("AI Agent - Choose required tool: Calculator, SQL → dbt, Search")

try:
    from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, GROQ_API_KEY
except Exception:
    LANGFUSE_PUBLIC_KEY = None
    LANGFUSE_SECRET_KEY = None
    LANGFUSE_HOST = None
    GROQ_API_KEY = None

with st.sidebar:
    st.header("Status")
    lf_status = "✅ Enabled" if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY and LANGFUSE_HOST else "⚠️ Disabled"
    groq_status = "✅ Enabled" if GROQ_API_KEY else "⚠️ Disabled"
    st.write(f"Langfuse: {lf_status}")
    st.write(f"Groq: {groq_status}")
    st.markdown("---")
    st.caption("• LangGraph orchestrates cyclic workflows\n• Langfuse monitors traces\n• Groq powers LLM nodes (interpret & explain)")

# ---------------------------
# Task Selector
# ---------------------------
task = st.radio(
    "Choose a task",
    ["Calculator", "SQL → dbt", "Search"],
    horizontal=True,
)

user_id = st.text_input("User ID (optional)")

# ---------------------------
# Calculator Task
# ---------------------------
if task == "Calculator":
    expression = st.text_input("Expression", value="2+3*5", placeholder="e.g., 2+3*5")
    if st.button("Run"):
        # For plan + interpret_math extract/clean expression
        goal = f"calc {sanitize(expression)}"
        with st.spinner("Running calculator agent..."):
            out = run(goal=goal, user_id=user_id or None)

        result = out.get("result") or {}
        errors = out.get("errors") or []
        context = out.get("context") or {}

        st.subheader("Calculator Result")
        if result:
            expr = result.get("expression")
            val = result.get("value")
            expl = result.get("explanation")  # added by explain_calc node
            if expr is not None:
                st.write(f"**Expression:** `{expr}`")
            if val is not None:
                st.write(f"**Value:** `{val}`")
            if expl:
                st.markdown("**Explanation:**")
                st.markdown(expl)
        else:
            st.info("No result returned.")

        if errors:
            st.subheader("Errors")
            st.error(errors)

        with st.expander("Context"):
            st.json(context)

# ---------------------------
# SQL → dbt Task
# ---------------------------
elif task == "SQL → dbt":
    sql = st.text_area(
        "SQL",
        value="SELECT 1 AS col",
        height=160,
        placeholder="Paste SQL here",
    )
    model_name = st.text_input("Model name (optional)", value="generated_model")
    if st.button("Run"):
        goal = f"sql2dbt {sanitize(sql)}"
        with st.spinner("Converting SQL → dbt model..."):
            out = run(goal=goal, user_id=user_id or None)

        result = out.get("result") or {}
        errors = out.get("errors") or []
        context = out.get("context") or {}

        st.subheader("Generated dbt Model")
        model_content = result.get("model_content") or context.get("sql")
