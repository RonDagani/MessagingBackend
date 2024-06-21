from handlers import user as userHandler
from models import request, user as userModel
from fastapi import APIRouter

class userRouter:
    def __init__(self):
        self.user_handler = userHandler.UserHandler()
        self.router = APIRouter()
        self.router.add_api_route("/users/register", self.register_user, methods=["POST"], response_model=userModel.User)
        self.router.add_api_route("/users/block", self.block_user, methods=["POST"])

    def register_user(self, request: request.RegisterUserRequest):
        return self.user_handler.register_user(request.username)

    def block_user(self, request: request.BlockUserRequest):
        return self.user_handler.block_user(request.user_id, request.block_user_id)


# @app.post("/users/register", response_model=User)
# async def register_user(request: RegisterUserRequest):
#     return await user_handler.register_user(request.username)

# @app.post("/users/block")
# async def block_user(request: BlockUserRequest):
#     return await user_handler.block_user(request.user_id, request.block_user_id)

# Example usage of the FastAPI endpoints
# POST /users/register
# {
#     "username": "john_doe"
# }
# Response: { "user_id": "uuid", "username": "john_doe", "blocked_users": [] }

# POST /users/block
# {
#     "user_id": "uuid",
#     "block_user_id": "uuid"
# }
# Response: { "message": "User block_user_id has been blocked" }
