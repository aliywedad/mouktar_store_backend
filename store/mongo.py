from pymongo import MongoClient
client = MongoClient(
    "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.10"
)

db = client.store
users = db['users']
facteurs = db['facteurs']
clients = db['clients']
Notes= db['notes']
debts= db['debts']
products= db['products']
def mongo_to_json(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc
print(db.list_collection_names())