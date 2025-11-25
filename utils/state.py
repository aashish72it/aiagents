
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    goal: str = Field(..., description="User objective or query")
    tool: Optional[str] = Field(None, description="Which tool to run: calc|sql2dbt|search")
    attempts: int = Field(0, description="Number of attempts to run the tools", ge=0, le=10)
    max_attempts: int = 4
    code: Optional[str] = None
    result: Optional[Any] = None
    errors: List[str] = []
    context: Dict[str, Any] = {}
    tests_passed: bool = False
