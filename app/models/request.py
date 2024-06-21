from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class RegisterUserRequest(BaseModel):
    username: str

class RegisterGroupRequest(BaseModel):
    group_name: str

class BlockUserRequest(BaseModel):
    user_id: UUID
    block_user_id: UUID

class SendMessageRequest(BaseModel):
        sender_id: UUID
        receiver_id: UUID
        content: str

class SendGroupMessageRequest(BaseModel):
        sender_id: UUID
        group_id: UUID
        content: str
        
class GetMessageRequest(BaseModel):
    user1_id: UUID
    user2_id: UUID
    page: int = 1

class GetGroupMessagesRequest(BaseModel):
    user_id: UUID
    group_id: UUID
    page: int = 1

class GroupMembershipRequest(BaseModel):
    user_id: UUID
