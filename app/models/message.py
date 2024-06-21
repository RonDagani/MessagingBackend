from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Message(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    sender_id: UUID
    receiver_id: UUID # reciever id ban also be a group
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "sender_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "receiver_id": "e47ac10b-58cc-4372-a567-0e02b2c3d480",
                "content": "Hello, this is a test message!",
                "timestamp": "2024-05-31T17:00:00Z"
            }
        }