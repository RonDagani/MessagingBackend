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
                    os.environ.get('MONGODB_CONNECTION_STRING'),
                    uuidRepresentation='standard'
                )
                cls._instance.mongo_client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
                cls._instance.db = cls._instance.mongo_client.get_database("MessagingDB")
                
                cls._instance.mongo_client.admin.command('enableSharding', 'MessagingDB')
            
                # Shard the messages collection by user_id
                cls._instance.mongo_client.admin.command('shardCollection', 'MessagingDB.messages', key={'reciever_id': ASCENDING})
            
                # Create indexes
                messages_collection = cls._instance.db.get_collection("messages")
                messages_collection.create_index([('reciever_id', ASCENDING), ('timestamp', ASCENDING)])
                messages_collection.create_index('created_at', expireAfterSeconds=3600 * 24 )  # 1 days TTL index

            except Exception as e:
                print(e)
        
        return cls._instance
    
