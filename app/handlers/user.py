from fastapi import HTTPException
from const import dbConnection
from models.user import User
from bson import Binary, uuid
from uuid import UUID

# UserHandler Class
class UserHandler:
    def __init__(self):
        self.db_connection = dbConnection.DBConnection()
        self.users_collection = self.db_connection.db.get_collection("users")

    def get_user(self, user_id: str) -> User:
        try:
            user = self.users_collection.find_one({"user_id": user_id})
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def register_user(self, username: str) -> User:
        try:
            new_user = User(username=username)
            self.users_collection.insert_one(new_user.model_dump())
            return new_user
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def is_blocked_user(self, sender_user_id: str, reciever_user_id: str) -> bool:
        reciever_user = self.get_user(reciever_user_id)
        if sender_user_id in reciever_user['blocked_users']:
            return True
        return False

    def block_user(self, user_id: UUID, block_user_id: UUID):
        if self.is_blocked_user(sender_user_id=block_user_id, reciever_user_id=user_id):
            raise HTTPException(status_code=400, detail="User already blocked")
        
        user = self.get_user(user_id)
        user["blocked_users"].append(block_user_id)
        try:
            self.users_collection.update_one(
                {"user_id": user_id}, 
                {"$set": {"blocked_users": user["blocked_users"]}}
            )
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        return {"message": f"User {block_user_id} has been blocked by user {user_id}"}