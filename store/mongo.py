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
payments= db['payments']
def mongo_to_json(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


def mongo_to_json2(doc):
    doc["id"] = str(doc["_id"])
    if("debt" in doc):
        doc["debt"] = str(doc["debt"])
    del doc["_id"]
    return doc
# print(db.list_collection_names())