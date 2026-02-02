# import pandas as pd
# from pymongo import MongoClient
# from datetime import datetime

# from pymongo import MongoClient
# client = MongoClient(
#     "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.10"
# )

# db = client.store
 
# debts= db['debts']
# payments= db['payments']

 
# # Load Excel
# df = pd.read_excel("debts.xlsx")

# now_ts = int(datetime.now().timestamp() * 1000)

# for _, row in df.iterrows():
#     name = str(row["name"]) 
#     tel = int(row["tel"])
#     amount = int(row["amount"])

#     if not tel or amount <= 0:
#         print(f"⛔ Skipped invalid row: {row}")
#         continue

#     # 1️⃣ Find existing debt
#     debt = debts.find_one({"tel": tel})

#     if debt:
#         # Update existing debt
#         debts.update_one(
#             {"_id": debt["_id"]},
#             {
#                 "$inc": {"debt": amount},
#                 "$set": {"timestamp": now_ts}
#             }
#         )
#         debt_id = str(debt["_id"])
#     else:
#         # Create new debt
#         res = debts.insert_one({
#             "name": name,
#             "tel": tel,
#             "debt": amount,
#             "timestamp": now_ts
#         })
#         debt_id = str(res.inserted_id)

#     # 2️⃣ Insert payment record
#     payments.insert_one({
#         "note": "add via excel",
#         "amount": amount,
#         "wallet": "excel",
#         "tel": tel,
#         "debt": debt_id,
#         "facteur": "",
#         "type": "debt",
#         "timestamp": now_ts
#     })

#     print(f"✅ Imported: {name} | {tel} | {amount}")

# print("🎉 Excel import finished successfully")
