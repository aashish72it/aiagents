
# Architecture

The system uses LangGraph to orchestrate tool execution through a cyclic pipeline:

1. **Plan** — Decide which tool should handle the goal.
2. **Execute** — Run the selected tool.
3. **Evaluate** — Check output/errors and propose fixes.
4. **Decide** — If not done and attempts remain, loop back to execute.

Langfuse is used to create traces, events, and outputs for monitoring.
