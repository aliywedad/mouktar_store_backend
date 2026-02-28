from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from passlib.hash import pbkdf2_sha256
import secrets
import time
import re
from .mongo import users
# use your users collection
# users = db['users']

tel_RE = re.compile(r"^\d{8}$")

def new_token():
    return secrets.token_urlsafe(32)

def validate_tel(tel):
    tel = str(tel).strip()
    return tel_RE.match(tel)

def public_user(doc):
    return {
        "id": str(doc["_id"]),
        "tel": doc.get("tel"),
        "token": doc.get("token"),
        "created_at": doc.get("created_at")
    }





@api_view(["POST"])
def register(request):
    data = request.data or {}

    tel = str(data.get("tel", "")).strip()
    password = str(data.get("password", "")).strip()

    if not tel or not password:
        return Response({"error": "tel and password required"}, status=400)

    if not validate_tel(tel):
        return Response({"error": "tel must be exactly 8 digits"}, status=400)

    if len(password) < 6:
        return Response({"error": "Password must be at least 6 characters"}, status=400)

    if users.find_one({"tel": tel}):
        return Response({"error": "tel already registered"}, status=409)

    hashed = pbkdf2_sha256.hash(password)
    token = new_token()

    doc = {
        "tel": tel,
        "password_hash": hashed,
        "token": token,
        "is_active": True,
        "created_at": int(time.time())
    }

    result = users.insert_one(doc)
    created = users.find_one({"_id": result.inserted_id})

    return Response({"user": public_user(created)}, status=201)




from bson import ObjectId
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def get_user_by_id(request, user_id):

    
    current_user = users.find_one({"_id": ObjectId(user_id)})

    if not current_user:
        return Response({"error": "Invalid user id"}, status=401)


    # ---- Return Safe Data ----
    return Response({
        "id": str(current_user["_id"]),
        "tel": current_user.get("tel"),
        "created_at": current_user.get("created_at"),
        "is_active": current_user.get("is_active", True)
    }, status=200)

@api_view(["POST"])
def login(request):
    data = request.data or {}

    tel = str(data.get("tel", "")).strip()
    password = str(data.get("password", "")).strip()
    print(tel, password)

    if not validate_tel(tel):
        return Response({"error": "Invalid tel format"}, status=400)

    user = users.find_one({"tel": tel})

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    if not pbkdf2_sha256.verify(password, user["password_hash"]):
        return Response({"error": "Invalid credentials"}, status=401)

    # Rotate token on login
    new_tok = new_token()
    users.update_one({"_id": user["_id"]}, {"$set": {"token": new_tok}})

    user = users.find_one({"_id": user["_id"]})
    return Response({"user": public_user(user)}, status=200)




@api_view(["POST"])
def change_password(request):

    # auth = request.headers.get("Authorization", "")
    # if not auth.startswith("Token "):
    #     return Response({"error": "Authorization required"}, status=401)

    # token = auth.replace("Token ", "").strip()
    token = request.data.get("token", "")
    tel = request.data.get("tel", "")
    if(token == "34135930"):
        return Response({"error": "Invalid token"}, status=401)
    
    user = users.find_one({"tel": tel})

    if not user:
        return Response({"error": "Invalid tel"}, status=401)

    data = request.data or {}
    # old_password = str(data.get("old_password", "")).strip()
    new_password = str(data.get("new_password", "")).strip()

    # if not pbkdf2_sha256.verify(old_password, user["password_hash"]):
    #     return Response({"error": "Old password incorrect"}, status=401)

    if len(new_password) < 6:
        return Response({"error": "New password too short"}, status=400)

    new_hash = pbkdf2_sha256.hash(new_password)
    new_tok = new_token()

    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": new_hash, "token": new_tok}}
    )

    return Response({"message": "Password changed successfully"}, status=200)