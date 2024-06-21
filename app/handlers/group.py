from fastapi import HTTPException
from const import dbConnection
from models.group import Group
from bson import Binary, uuid
from uuid import UUID
from pymongo import ReturnDocument
from handlers import user


# GroupHandler Class
class GroupHandler:
    def __init__(self):
        self.db_connection = dbConnection.DBConnection()
        self.user_handler = user.UserHandler()
        self.groups_collection = self.db_connection.db.get_collection("groups")

    def register_group(self, group_name: str) -> Group:
        try:
            new_group = Group(group_name=group_name)
            self.groups_collection.insert_one(new_group.model_dump())
            return new_group
        except:
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def add_user(self, group_id: UUID, user_id: UUID):
        try:
            # validating user existance
            self.user_handler.get_user(user_id=user_id)

            # adding
            result = self.groups_collection.find_one_and_update(
                {"group_id": group_id},
                {"$addToSet": {"members": user_id}},
                return_document=ReturnDocument.AFTER
            )
            if not result:
                raise HTTPException(status_code=404, detail="Group not found")
            return Group(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def remove_user(self, group_id: UUID, user_id: UUID):
        try:
            # validating user existance
            self.user_handler.get_user(user_id=user_id)

            result = self.groups_collection.find_one_and_update(
                {"group_id": group_id},
                {"$pull": {"members": user_id}},
                return_document=ReturnDocument.AFTER
            )
            if not result:
                raise HTTPException(status_code=404, detail="Group not found")
            return Group(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def is_user_in_group(self, group_id: UUID, user_id: UUID):
        # validating user existance
        self.user_handler.get_user(user_id=user_id)
        group = self.groups_collection.find_one({
            "group_id": group_id,
            "members": user_id
        })
        return group is not None