from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4

class User(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)
    username: str
    blocked_users: List[UUID] = []

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "username": "john_doe",
                "blocked_users": ["f47ac10b-58cc-4372-a567-0e02b2c3d479"]
            }
        }