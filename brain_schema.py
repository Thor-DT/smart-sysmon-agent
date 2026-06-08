 
from pydantic import BaseModel, Field
from typing import Literal, List

class MitigationAction(BaseModel):
    # Literal forces the AI to ONLY choose from these specific string tokens
    action: Literal["ALLOW", "MONITOR", "TERMINATE"] = Field(
        description="The response strategy for the target process."
    )
    pid: int = Field(
        description="The process identifier targeted by this action. Use 0 if action is ALLOW."
    )
    process_name: str = Field(
        description="The name of the process being acted upon."
    )
    reasoning: str = Field(
        description="A brief, human-readable structural analysis explaining why this action was selected."
    )

class AgentDecisionBatch(BaseModel):
    verdict: List[MitigationAction] = Field(
        description="A list containing evaluating entries for any heavy system processes."
    )