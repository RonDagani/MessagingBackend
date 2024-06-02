import os
from pymongo import MongoClient

class DBConnection:
    client = MongoClient(os.environ.get('MONGODB-CONNECTION-STRING'))
    db = client.Messaging