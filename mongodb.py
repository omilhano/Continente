from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve MongoDB URI from environment variables
CONNECTION_STRING = os.getenv("MONGO_URI")

if not CONNECTION_STRING:
    raise ValueError("MongoDB connection string is missing. Make sure MONGO_URI is set in the .env file.")

# Connect to MongoDB
client = MongoClient(CONNECTION_STRING)

# Access database and collection
db = client['Preços']
collection = db['Talho']

# Delete all documents in the collection (for example)
result = collection.delete_many({})
print(f"Deleted {result.deleted_count} documents from the collection.")
