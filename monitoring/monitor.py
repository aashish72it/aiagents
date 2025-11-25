from langfuse import observe, langfuse_context

def start_trace(name: str, user_id: str = None):
    """
    Initialize a trace context for the current run.
    In v3, traces are managed via langfuse_context.
    """
    langfuse_context.update_current_trace(name=name, user_id=user_id)
    return {"trace_id": langfuse_context.get_current_trace_id()}

def log_event(trace_ctx, event_name: str, payload: dict):
    """
    Log an event as a span using @observe decorator.
    """
    @observe(name=event_name)
    def _log(data):
        return data
    _log(payload)

def end_trace(trace_ctx, final_payload: dict = None):
    """
    Update trace metadata before finishing.
    No .end() in v3; just update context.
    """
    langfuse_context.update_current_trace(metadata={"final": final_payload or {}})
    # Optional flush for short-lived apps like Streamlit:
    langfuse_context.flush()
