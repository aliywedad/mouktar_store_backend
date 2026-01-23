import random
import string
from .mongo import *
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from store.permissions import HasTokenPermission
from .models import  *
from .constants import *
from bson import ObjectId

from decimal import Decimal, InvalidOperation 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction as db_transaction
from .backup import *
from django.utils.timezone import now
from django.db.models import Sum, Count
from rest_framework.decorators import api_view ,permission_classes
import hashlib
from datetime import timedelta
import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

@api_view(["GET", "POST", "PATCH", "DELETE"])
def facteursAPI(request, facteur_id=None ):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = request.GET.get("tel")
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")
            tel = request.GET.get("tel")
            print(tel,createdFrom,createdTo,tel)
            if facteur_id:
                doc = facteurs.find_one({"_id": ObjectId(facteur_id)})
                if not doc:
                    return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response({"data": mongo_to_json(doc)}, status=status.HTTP_200_OK)
            else:
                # Build query based on provided parameters
                query = {}
                
                # Filter by clientId if provided
                if tel:
                    query["tel"] = tel
                
                # Filter by date range if createdFrom or createdTo are provided
                # Assuming you have a "createdAt" field storing timestamps
                if createdFrom or createdTo:
                    date_filter = {}
                    if createdFrom:
                        date_filter["$gte"] = float(createdFrom)  # Convert to float if needed
                    if createdTo:
                        date_filter["$lte"] = float(createdTo)    # Convert to float if needed
                    query["timestamp"] = date_filter
                
                # Get all Notesions with filters and order by date (newest first)
                Notesions_data = [mongo_to_json(d) for d in 
                                   facteurs.find(query).sort("timestamp", -1)]
                
                return Response({"data": Notesions_data}, status=status.HTTP_200_OK)

        # ---------------- POST ----------------
        elif request.method == "POST":
            data = request.data
            data["tel"] = str(data["tel"])

              
            result = facteurs.insert_one(data)
            return Response(
                {"message": "Facteur created", "id": str(result.inserted_id)},
                status=status.HTTP_201_CREATED
            )

        # ---------------- PATCH / UPDATE ----------------
        elif request.method == "PATCH":
            if not facteur_id:
                return Response({"error": "Facteur ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
            update_data = request.data
            if not update_data:
                return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            result = facteurs.update_one(
                {"_id": ObjectId(facteur_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)

            updated_doc = facteurs.find_one({"_id": ObjectId(facteur_id)})
            return Response({"data": mongo_to_json(updated_doc)}, status=status.HTTP_200_OK)

        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not facteur_id:
                return Response({"error": "Facteur ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
            result = facteurs.delete_one({"_id": ObjectId(facteur_id)})
            if result.deleted_count == 0:
                return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Facteur deleted"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def confirmeFacteur(request):
    try:
        facteur_id = request.data.get("id_facteur")
        if not facteur_id:
            return Response({"error": "id_facteur is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1️⃣ Get the facture
        facteur = facteurs.find_one({"_id": ObjectId(facteur_id)})
        if not facteur:
            return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)

        remaining_amount = facteur["total"] - facteur.get("payed_price", 0)
        if remaining_amount <= 0:
            return Response({"message": "Facture is already fully paid"}, status=status.HTTP_200_OK)

        # 2️⃣ Update debt for this customer
        debt = debts.find_one({"tel": facteur["tel"]})
        payment_record = {
            "note": f"تم إضافة مبلغ {remaining_amount} إلى الدين",
            "amount": remaining_amount,
            "facteur": facteur_id,
            "type":"debt",
            "timestamp": int(datetime.now().timestamp() * 1000) 
        }

        if debt:
            # Update existing debt
            debts.update_one(
                {"_id": debt["_id"]},
                {
                    "$inc": {"debt": remaining_amount},
                    "$push": {"payments": {"$each": [payment_record], "$position": 0}}
                }
            )
        else:
            # Create new debt if none exists
            debts.insert_one({
                "tel": str(facteur["tel"]),
                "debt": remaining_amount,
                "payments": [payment_record],
                "name":facteur["name"],
                "timestamp":int(datetime.now().timestamp() * 1000) 
            })

        facteurs.update_one(
            {"_id": ObjectId(facteur_id)},
            {"$set": {"send": True}}
        )

        return Response({"message": "Facteur confirmed and debt updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(["GET", "POST", "PATCH", "DELETE"])
def debtsAPI(request, debt_id=None):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = request.GET.get("tel")
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")

            if debt_id:
                doc = debts.find_one({"_id": ObjectId(debt_id)})
                if not doc:
                    return Response(
                        {"error": "Debt not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                return Response(
                    {"data": mongo_to_json(doc)},
                    status=status.HTTP_200_OK
                )

            # Build query
            query = {}

            if tel:
                query["tel"] = tel

            if createdFrom or createdTo:
                date_filter = {}
                if createdFrom:
                    date_filter["$gte"] = float(createdFrom)
                if createdTo:
                    date_filter["$lte"] = float(createdTo)
                query["timestamp"] = date_filter
            print("query : ",query)
            debts_data = [
                mongo_to_json(d)
                for d in debts.find(query)
                .sort("timestamp", -1)
            ]
            # print(debts_data)

            return Response(
                {"data": debts_data},
                status=status.HTTP_200_OK
            )

        # ---------------- POST ----------------
        elif request.method == "POST":
            data = request.data
            data['tel']=str(data["tel"])
            result = debts.insert_one(data)
            return Response(
                {
                    "message": "Debt created",
                    "id": str(result.inserted_id)
                },
                status=status.HTTP_201_CREATED
            )

        # ---------------- PATCH ----------------
        elif request.method == "PATCH":
            if not debt_id:
                return Response(
                    {"error": "Debt ID is required for update"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            update_data = request.data
            update_data["tel"] = str(update_data["tel"])

            if not update_data:
                return Response(
                    {"error": "No data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = debts.update_one(
                {"_id": ObjectId(debt_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return Response(
                    {"error": "Debt not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            updated_doc = debts.find_one({"_id": ObjectId(debt_id)})
            return Response(
                {"data": mongo_to_json(updated_doc)},
                status=status.HTTP_200_OK
            )

        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not debt_id:
                return Response(
                    {"error": "Debt ID is required for deletion"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = debts.delete_one({"_id": ObjectId(debt_id)})
            if result.deleted_count == 0:
                return Response(
                    {"error": "Debt not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Debt deleted"},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


 
 
@api_view(["GET", "POST", "PATCH", "DELETE"])
def NotesAPI(request, Notes_id=None):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")
            tel = request.GET.get("tel")
            print("Filters:", tel,createdFrom, createdTo)

            if Notes_id:
                # Get single note by ID
                doc = Notes.find_one({"_id": ObjectId(Notes_id)})
                if not doc:
                    return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response({"data": mongo_to_json(doc)}, status=status.HTTP_200_OK)
            else:
                # Build query dict
                query = {}

                # Filter by clientId if provided
                if tel:
                    query["tel"] = int(tel)

                # Filter by date range if provided
                # Assuming your Notes collection has a "date" or "timestamp" field in ISO or timestamp format
                if createdFrom or createdTo:
                    date_filter = {}
                    if createdFrom:
                        date_filter["$gte"] = float(createdFrom)  # timestamp in ms
                    if createdTo:
                        date_filter["$lte"] = float(createdTo)
                    query["timestamp"] = date_filter  # field storing numeric timestamp

                # Fetch filtered notes, sort newest first
                notes_data = [mongo_to_json(d) for d in Notes.find(query).sort("timestamp", -1)]

                return Response({"data": notes_data}, status=status.HTTP_200_OK)


        # ---------------- POST ----------------
        elif request.method == "POST":
            data = request.data
 
            result = Notes.insert_one(data)
            return Response(
                {"message": "Notes created", "id": str(result.inserted_id)},
                status=status.HTTP_201_CREATED
            )

        # ---------------- PATCH / UPDATE ----------------
        elif request.method == "PATCH":
            if not Notes_id:
                return Response(
                    {"error": "Notes ID is required for update"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            update_data = request.data
            if not update_data:
                return Response(
                    {"error": "No data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = Notes.update_one(
                {"_id": ObjectId(Notes_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return Response(
                    {"error": "Notes not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            updated_doc = Notes.find_one({"_id": ObjectId(Notes_id)})
            return Response(
                {"data": mongo_to_json(updated_doc)},
                status=status.HTTP_200_OK
            )

        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not Notes_id:
                return Response(
                    {"error": "Notes ID is required for deletion"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = Notes.delete_one({"_id": ObjectId(Notes_id)})
            if result.deleted_count == 0:
                return Response(
                    {"error": "Notes not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Notes deleted"},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )




@api_view(["POST"])
def getDebtsByPhone(request):
    tel = request.data.get("tel")
   
    if not tel:
        return Response(
            {"error": "Phone number (tel) is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    print("tel :", tel)

    debts_data = [
        mongo_to_json(note)
        for note in debts.find({"tel":tel}) 
    ]

    if not debts_data:
        return Response(
            {"data": [], "message": "No records found for this phone number"},
            status=status.HTTP_200_OK
        )

    return Response(
        {"data": debts_data},
        status=status.HTTP_200_OK
    )
