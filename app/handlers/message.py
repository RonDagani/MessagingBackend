from fastapi import HTTPException
from const import dbConnection
from models.message import Message
from handlers.user import UserHandler
from handlers.group import GroupHandler
from uuid import UUID
import json
import asyncio
from typing import List
from datetime import datetime
from dateutil import parser


def default(obj):
    if isinstance(obj, UUID):
        return str(obj)  # Convert UUID to string
    elif isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def decoder(dict):
    if 'sender_id' in dict:
        dict['sender_id'] = UUID(dict['sender_id'])
    if 'receiver_id' in dict:
        dict['receiver_id'] = UUID(dict['receiver_id'])
    if 'timestamp' in dict:
        dict['timestamp'] = parser.parse(dict['timestamp'])  # Convert ISO 8601 string back to datetime
    return dict

# MessageHandler Class
class MessageHandler:
    def __init__(self):
        self.db_connection = dbConnection.DBConnection()
        self.user_handler = UserHandler()
        self.group_handler = GroupHandler()
        self.users_collection = self.db_connection.db.get_collection("users")
        self.messages_collection = self.db_connection.db.get_collection("messages")
        self.redis_client = self.db_connection.redis_client
        loop = asyncio.get_event_loop()
        loop.create_task(self.schedule_flush())
    
    async def send_message(self, sender_id: UUID, receiver_id: UUID, content: str, is_group_reciever: bool = False):
        if is_group_reciever:
            if not self.group_handler.is_user_in_group(receiver_id, sender_id):
                raise HTTPException(status_code=500, detail="User can't write messages to a group he is not a member of.")
        else:
            if self.user_handler.is_blocked_user(sender_user_id=sender_id, reciever_user_id=receiver_id):
                raise HTTPException(status_code=500, detail=f"User {sender_id} is blocked by user {receiver_id}")
            
        new_message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        message_json = json.dumps(new_message.model_dump(), default=default)
        self.redis_client.lpush('message_queue', message_json)

        if self.redis_client.llen('message_queue') >= 50:
            await self.flush_messages()
        return new_message

    async def flush_messages(self):
        messages = []
        while self.redis_client.llen('message_queue') > 0:
            message = self.redis_client.rpop('message_queue')
            if message:
                messages.append(json.loads(message, object_hook=decoder))

        if messages:
            self.messages_collection.insert_many(messages)
    
    def get_messages(self, user1_id: UUID, user2_id: UUID, page: int = 1) -> List[Message]:
        try:
            messages_per_page = 50
            offset = (page - 1) * messages_per_page
            
            messages = self.messages_collection.find(
                {
                    '$or': [
                        {'sender_id': user1_id, 'receiver_id': user2_id},
                        {'sender_id': user2_id, 'receiver_id': user1_id}
                    ]
                }
            ).sort('timestamp', 1).skip(offset).limit(messages_per_page)
            
            return [Message(**message) for message in messages]
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    def get_group_messages(self, group_id: UUID, user_id: UUID, page: int = 1) -> List[Message]:
        if not self.group_handler.is_user_in_group(group_id, user_id):
            raise HTTPException(status_code=500, detail="User can't read messages of a group he is not a member of.")

        cache_key = f"group_messages:{group_id}:{page}"
        cached_messages = self.redis_client.get(cache_key)
        
        if cached_messages:
            messages = [Message(**msg) for msg in json.loads(cached_messages, object_hook=decoder)]
        else:
            messages_per_page = 50
            offset = (page - 1) * messages_per_page
            
            try:
                messages = self.messages_collection.find(
                    {'receiver_id': group_id}
                ).sort('timestamp', 1).skip(offset).limit(messages_per_page)
                
                messages = [Message(**message) for message in messages]
                
                # Serialize the messages to JSON string and store in Redis with a 10 second expiration
                self.redis_client.set(cache_key, json.dumps([msg.model_dump() for msg in messages], default=default), ex=10)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        return messages

    async def schedule_flush(self):
        while True:
            await asyncio.sleep(30)  # 5 minutes
            await self.flush_messages()