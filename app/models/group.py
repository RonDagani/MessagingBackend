from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4

class Group(BaseModel):
    group_id: UUID = Field(default_factory=uuid4)
    group_name: str
    members: List[UUID] = []
    messages: List[UUID] = []

    class Config:
        schema_extra = {
            "example": {
                "group_id": "b47ac10b-58cc-4372-a567-0e02b2c3d481",
                "group_name": "Developers",
                "members": ["f47ac10b-58cc-4372-a567-0e02b2c3d479", "e47ac10b-58cc-4372-a567-0e02b2c3d480"],
                "messages": ["d290f1ee-6c54-4b01-90e6-d701748f0851"]
            }
        }