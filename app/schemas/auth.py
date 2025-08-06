from pydantic import BaseModel, ConfigDict, Field


class TokenPair(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
