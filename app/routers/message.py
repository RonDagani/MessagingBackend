from handlers import message as messageHandler
from models import request, message as messageModel
from fastapi import APIRouter
from typing import List

class messageRouter:
    def __init__(self):
        self.message_handler = messageHandler.MessageHandler()
        self.router = APIRouter()
        self.router.add_api_route("/messages/send", self.send_message, methods=["POST"], response_model=messageModel.Message)
        self.router.add_api_route("/messages/get", self.get_messages, methods=["POST"], response_model=List[messageModel.Message])
        self.router.add_api_route("/group/messages/send", self.send_group_messages, methods=["POST"], response_model=messageModel.Message)
        self.router.add_api_route("/group/messages/get", self.get_group_messages, methods=["POST"], response_model=List[messageModel.Message])

    async def send_message(self, request: request.SendMessageRequest):
        return await self.message_handler.send_message(request.sender_id, request.receiver_id, request.content)
    
    async def send_group_messages(self, request: request.SendGroupMessageRequest):
        return await self.message_handler.send_message(request.sender_id, request.group_id, request.content, is_group_reciever=True)
    
    def get_messages(self, request: request.GetMessageRequest):
        return self.message_handler.get_messages(request.user1_id, request.user2_id, request.page)
    
    def get_group_messages(self, request: request.GetGroupMessagesRequest):
        return self.message_handler.get_group_messages(request.group_id, request.user_id, request.page)