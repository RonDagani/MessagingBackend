import os
from pymongo import MongoClient, ASCENDING
from redis import Redis

class DBConnection:
    _instance = None  # This will hold the single instance of the class

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            # Initialize the connection only once
            try:
                # Redis database
                cls._instance.redis_client = Redis(
                    host=os.environ.get('REDIS_HOST'),
                    port=os.environ.get('REDIS_PORT'),
                    db=0,
                    decode_responses=True
                )

                # MongoDB
                cls._instance.mongo_client = MongoClient(
                    os.environ.get('MONGODB-CONNECTION-STRING'),
                    uuidRepresentation='standard'
                )
                cls._instance.mongo_client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
                cls._instance.db = cls._instance.mongo_client.get_database("Messaging")
                # Enable sharding on the database
                cls._instance.mongo_client.admin.command('enableSharding', 'Messaging')
            
                # Shard the messages collection by user_id
                cls._instance.mongo_client.admin.command('shardCollection', 'Messaging.messages', key={'user_id': ASCENDING})
            
                # Create indexes
                messages_collection = cls._instance.db.get_collection("messages")
                messages_collection.create_index([('user_id', ASCENDING), ('timestamp', ASCENDING)])
                messages_collection.create_index('created_at', expireAfterSeconds=3600 * 24 * 30)  # 30 days TTL index

            except Exception as e:
                print(e)
        
        return cls._instance
    
