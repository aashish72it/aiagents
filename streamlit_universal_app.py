
import os
import streamlit as st
from graph import run

# Page config
st.set_page_config(page_title="AI Agent", layout="centered")
st.title("AI Agent - Universal Prompt: calc, SQL→dbt, search")

# Sidebar: Status (optional)
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
    st.caption("Enter any prompt. LangGraph will pick the right tool (calc, SQL→dbt, search).")

# Main UI
user_id = st.text_input("User ID (optional)")
prompt = st.text_area(
    "Enter your prompt",
    placeholder="e.g., calc 2+3*5 or convert SQL to dbt model or find LangGraph docs"
)

if st.button("Run"):
    with st.spinner("Processing your request..."):
        out = run(goal=prompt, user_id=user_id or None)

    result = out.get("result") or {}
    errors = out.get("errors") or []
    context = out.get("context") or {}

    # --- Smart rendering ---
    # 1) If it's a dbt model (sql2dbt), show the model content nicely
    model_content = result.get("model_content")
    if model_content:
        st.subheader("Generated dbt Model")
        st.code(model_content, language="sql")

        # Show path & model name if present
        model_path = result.get("model_path")
        model_name = result.get("model_name")
        if model_name:
            st.write("Model name:", model_name)
        if model_path:
            st.write("Saved at:", model_path)

            # Offer a download button if the file exists
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    st.download_button(
                        label="Download model file",
                        data=f,
                        file_name=os.path.basename(model_path),
                        mime="text/sql",
                    )

    # 2) If it's a search result, render snippets nicely
    elif isinstance(result, dict) and "snippets" in result:
        st.subheader("Search Results")
        snippets = result.get("snippets") or []
        
        if snippets:
            for s in snippets:
                title = s.get("title", "Result")
                link = s.get("link", "#")
                snippet_text = s.get("snippet", "")
                st.markdown(f"- {title} — {snippet_text}")

        else:
            st.info("No snippets returned.")

    # 3) If it's a calc or generic output, render the whole result
    else:
        st.subheader("Result")
        st.write(result)

    # Errors (if any)
    if errors:
        st.subheader("Errors")
        st.write(errors)

    # Optional: show context for debugging
    with st.expander("Context"):
        st.json(context)
