from pydantic import BaseModel, Field


class Lead(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    industry: str = Field(..., min_length=1)
    stage: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    source: str = Field(default="Apollo")


class MessagePack(BaseModel):
    subject_A: str
    body_A: str
    subject_B: str
    body_B: str
    followup_1: str
    followup_2: str
