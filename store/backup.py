import json
import os
import smtplib
import traceback
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .constants  import *
from .mongo import *
import requests
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

TOKEN = "8308670543:AAF0nfOXJs5cO36w9bx4Rp-t7ZL8sSKsmvM"
CHAT_ID = "6606270031"  
getUpdate=url = f"https://api.telegram.org/bot8308670543:AAF0nfOXJs5cO36w9bx4Rp-t7ZL8sSKsmvM/getUpdates"


def send_to_telegram(file_path, message="تقرير جديد"):
    """Send a local file to Telegram as a document."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": message},
            files={"document": f},
        )

    return response.status_code, response.text


@api_view(["GET"])
def export_data_to_telegram(request):
    """
    Generate JSON backup file and send it to Telegram.
    """
    try:
        # 🔹 Collect your data
        data = {
            "users": [mongo_to_json(doc) for doc in db['users'].find()],
            "facteurs": [mongo_to_json(doc) for doc in db['facteurs'].find()],
            "notes": [mongo_to_json(doc) for doc in db['notes'].find()],
            "debts": [mongo_to_json(doc) for doc in db['debts'].find()],
            "products": [mongo_to_json(doc) for doc in db['products'].find()],
            "payments": [mongo_to_json2(doc) for doc in db['payments'].find()],
            "stock": [mongo_to_json(doc) for doc in db['Stock'].find()],
            "stockChanges": [mongo_to_json(doc) for doc in db['StockChanges'].find()],
            "storeDebts": [mongo_to_json(doc) for doc in db['Stores_debt'].find()],
            "factory": [mongo_to_json(doc) for doc in db['factory'].find()],
        }

        # 🔹 Create JSON file
        file_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        temp_path = f"/tmp/{file_name}"

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # 🔹 Send to Telegram
        code, text = send_to_telegram(temp_path, "📦 نسخة احتياطية للنظام")

        # 🔹 Remove file
        os.remove(temp_path)

        return Response({
            "status": "Backup sent to Telegram successfully"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
