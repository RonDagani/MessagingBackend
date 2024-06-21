from handlers import group as groupHandler
from models import request, group as groupModel
from fastapi import APIRouter, HTTPException
from uuid import UUID

class groupRouter:
    def __init__(self):
        self.group_handler = groupHandler.GroupHandler()
        self.router = APIRouter()
        self.router.add_api_route("/groups/register", self.register_group, methods=["POST"], response_model=groupModel.Group)
        self.router.add_api_route("/groups/{group_id}/add-user",self.add_user_to_group,methods=["POST"],response_model=groupModel.Group)
        self.router.add_api_route("/groups/{group_id}/remove-user",self.remove_user_from_group,methods=["POST"],response_model=groupModel.Group)

    def register_group(self, request: request.RegisterGroupRequest):
            return self.group_handler.register_group(request.group_name)
    
    def add_user_to_group(self, group_id: UUID, request: request.GroupMembershipRequest):
            return self.group_handler.add_user(group_id, request.user_id)

    def remove_user_from_group(self, group_id: UUID, request: request.GroupMembershipRequest):
            return self.group_handler.remove_user(group_id, request.user_id)