from typing import Literal

from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    category: Literal["hazardous", "factual", "conceptual", "quiz", "general"] = Field(
        description="The single bucket the user's latest message falls into."
    )


class EvalResult(BaseModel):
    passed: bool = Field(description="True only if the answer meets every criterion.")
    feedback: str = Field(
        description="One or two sentences naming the specific gap to fix. Empty if passed."
    )
