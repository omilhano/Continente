from pymongo import MongoClient
from datetime import date

# Connection string
CONNECTION_STRING = 'mongodb+srv://alexmvfrancisco:C8JEg4QyncRXMQqT@cluster0.lp8w7.mongodb.net/'

# Connect to MongoDB
client = MongoClient(CONNECTION_STRING)

# Access database and collection
db = client['Preços']
collection = db['Talho']

# Data to insert (example structure)
# Delete all documents in the collection
result = collection.delete_many({})
print(f"Deleted {result.deleted_count} documents from the collection.")


