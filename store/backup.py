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

import requests
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

TOKEN = "8308670543:AAF0nfOXJs5cO36w9bx4Rp-t7ZL8sSKsmvM"
CHAT_ID = accountData.get('chatId')  # aliy
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


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def send_pdf_to_telegram(request):
    """
    Endpoint to receive a PDF from the frontend and send it to Telegram.
    """
    try:
        pdf_file = request.FILES.get("file")
        message = request.data.get("message", "تقرير العمليات")

        if not pdf_file:
            return Response({"error": "لم يتم إرسال أي ملف"}, status=status.HTTP_400_BAD_REQUEST)

        # Save temporarily
        temp_path = f"/tmp/{pdf_file.name}"
        with open(temp_path, "wb+") as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        code, text = send_to_telegram(temp_path, message)

        # Clean up
        os.remove(temp_path)

        return Response(
            {"status": "تم الإرسال إلى تيليجرام", "telegram_response": text},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
