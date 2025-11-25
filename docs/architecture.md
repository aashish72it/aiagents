
# Architecture

The system uses LangGraph to orchestrate tool execution through a cyclic pipeline:

1. **Plan** — Decide which tool should handle the goal.
2. **Interpret Math** — Parse and understand mathematical expressions (if applicable).
3. **Explain Calc** — Provide step-by-step explanation for calculations (optional).
4. **Execute** — Run the selected tool.
5. **Evaluate** — Check output/errors and propose fixes.
6. **Decide** — If not done and attempts remain, loop back to execute.

Langfuse is used to create traces, events, and outputs for monitoring.
