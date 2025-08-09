from pymongo import MongoClient
import os

MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_KEY = os.getenv("MONGODB_KEY")

class MongoDBService:
    def __init__(self):
        self.client = MongoClient(f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_KEY}@automationworkflowclust.fl5vv6u.mongodb.net/")
        self.db = self.client["automation_workflow"]
        self.collection = self.db["file_metadata"]

    def insert_document(self, document: dict) -> str:
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def find_document(self, query: dict) -> dict:
        return self.collection.find_one(query)

    def find_documents_with_filter(self, filter: dict) -> list:
        return list(self.collection.find(filter))

    def update_document(self, query: dict, update: dict) -> int:
        result = self.collection.update_one(query, {"$set": update})
        return result.modified_count

    def delete_document(self, query: dict) -> int:
        result = self.collection.delete_one(query)
        return result.deleted_count