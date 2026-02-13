import random
import string

from django.conf import settings
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
from .validations import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction as db_transaction
from .backup import *
from django.utils.timezone import now
from django.db.models import Sum, Count
from rest_framework.decorators import api_view ,permission_classes
import hashlib
from datetime import time, timedelta
import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

@api_view(["GET", "POST", "PATCH", "DELETE"])
def facteursAPI(request, facteur_id=None ):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = int(request.GET.get("tel",0))
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")
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

            
            
            
                    
        # ---------------- POST ----------------
        elif request.method == "POST":
            data = request.data

            # Validate required fields
            name = data.get("name", "").strip()
            tel = data.get("tel", "")

            if not name:
                return Response(
                    {"error": "اسم العميل مطلوب"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not tel:
                return Response(
                    {"error": "رقم الهاتف مطلوب"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                data["tel"] = int(tel)
            except ValueError:
                return Response(
                    {"error": "رقم الهاتف يجب أن يكون عدداً صحيحاً"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Optional: Check tel length
            if len(str(data["tel"])) < 8:
                return Response(
                    {"error": "رقم الهاتف يجب أن يكون 8 أرقام على الأقل"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Insert the facteur
            result = facteurs.insert_one(data)
            return Response(
                {"message": "تم إنشاء الفاتورة بنجاح", "id": str(result.inserted_id)},
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

 
 
@api_view(["GET", "POST", "PATCH", "DELETE"])
def storesDebtAPI(request, storesDebt_id=None ):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = int(request.GET.get("tel",0))
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")
            debtType=request.GET.get("debtType")
            print(tel,createdFrom,createdTo,tel)
            if storesDebt_id:
                print("storesDebt_id fount ")
                doc = storesDebt.find_one({"_id": ObjectId(storesDebt_id)})
                if not doc:
                    return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response({"data": mongo_to_json(doc)}, status=status.HTTP_200_OK)
            else:
                # Build query based on provided parameters
                query = {}
                
                # Filter by clientId if provided
                if tel:
                    query["tel"] = tel
                if debtType is not None:
                    try:
                        debtType = int(debtType)

                        if debtType == 1:
                            query["OnUs"] = True
                        elif debtType == 2:
                            query["OnUs"] = False
                    except ValueError:
                        return Response(
                            {"error": "Invalid debtType value"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
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
                                   storesDebt.find(query).sort("timestamp", -1)]
                
                return Response({"data": Notesions_data}, status=status.HTTP_200_OK)

        # ---------------- POST ----------------

            
            
            
                    
        # ---------------- POST ----------------
        elif request.method == "POST":
            data=request.data
            clean, errors = validate_stores_debt_payload(request.data, partial=False)
            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
 
            # Insert the facteur
            result = storesDebt.insert_one(data)
            return Response(
                {"message": "تم إنشاء الفاتورة بنجاح", "id": str(result.inserted_id)},
                status=status.HTTP_201_CREATED
            )


        # ---------------- PATCH / UPDATE ----------------
        elif request.method == "PATCH":
            if not storesDebt_id:
                return Response({"error": "Facteur ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
            update_data = request.data
            clean, errors = validate_stores_debt_payload(request.data, partial=False)
            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            if not update_data:
                return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            result = storesDebt.update_one(
                {"_id": ObjectId(storesDebt_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)

            updated_doc = storesDebt.find_one({"_id": ObjectId(storesDebt_id)})
            return Response({"data": mongo_to_json(updated_doc)}, status=status.HTTP_200_OK)

        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not storesDebt_id:
                return Response({"error": "Facteur ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
            result = storesDebt.delete_one({"_id": ObjectId(storesDebt_id)})
            if result.deleted_count == 0:
                return Response({"error": "Facteur not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Facteur deleted"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import uuid
import os
from django.conf.urls.static import static


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        ext = os.path.splitext(image.name)[1]
        safe_name = f"{uuid.uuid4()}{ext}"

        path = default_storage.save(f'uploads/{safe_name}', image)
        url = request.build_absolute_uri(settings.MEDIA_URL + path)

        return JsonResponse({'url': url})


@csrf_exempt
def upload_facteur_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        tel = request.POST.get('tel')
        place=request.POST.get('place')

        if not tel:
            return JsonResponse({'error': 'tel is required'}, status=400)

        ext = os.path.splitext(image.name)[1]
        safe_name = f"{uuid.uuid4()}{ext}"

        # Correct folder structure
        path = default_storage.save(
            f'uploads/{place}/{tel}/{safe_name}',
            image
        )

        url = request.build_absolute_uri(settings.MEDIA_URL + path)

        return JsonResponse({'url': url})

    return JsonResponse({'error': 'Invalid request'}, status=400)


 

# 


@api_view(["GET", "POST", "PATCH", "DELETE"])
def productsAPI(request, product_id=None):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            name = request.GET.get("name")
            category = request.GET.get("category")
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")

            if product_id:
                doc = products.find_one({"_id": ObjectId(product_id)})
                if not doc:
                    return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response({"data": mongo_to_json(doc)}, status=status.HTTP_200_OK)
            else:
                # Build query based on provided parameters
                query = {}

                if name:
                    query["name"] = {"$regex": name, "$options": "i"}  # case-insensitive search
                if category:
                    query["category"] = category

                # Filter by date range if provided
                if createdFrom or createdTo:
                    date_filter = {}
                    if createdFrom:
                        date_filter["$gte"] = float(createdFrom)
                    if createdTo:
                        date_filter["$lte"] = float(createdTo)
                    query["timestamp"] = date_filter

                # Get all products with filters, sorted by newest first
                products_data = [mongo_to_json(d) for d in products.find(query).sort("timestamp", -1)]
                return Response({"data": products_data}, status=status.HTTP_200_OK)

        # ---------------- POST ----------------
        elif request.method == "POST":
            data = request.data
            # You can add additional processing for fields if needed
            result = products.insert_one(data)
            return Response(
                {"message": "Product created", "id": str(result.inserted_id)},
                status=status.HTTP_201_CREATED
            )

        # ---------------- PATCH / UPDATE ----------------
        elif request.method == "PATCH":
            if not product_id:
                return Response({"error": "Product ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
            update_data = request.data
            if not update_data:
                return Response({"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST)

            result = products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            updated_doc = products.find_one({"_id": ObjectId(product_id)})
            return Response({"data": mongo_to_json(updated_doc)}, status=status.HTTP_200_OK)

        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not product_id:
                return Response({"error": "Product ID is required for deletion"}, status=status.HTTP_400_BAD_REQUEST)
            result = products.delete_one({"_id": ObjectId(product_id)})
            if result.deleted_count == 0:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "Product deleted"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 
@api_view(["GET", "POST", "PATCH", "DELETE"])
def paymentsAPI(request, payme_id=None):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = request.GET.get("tel")
            debtID = request.GET.get("debtId")
            # # if tel is not provided stop 
            # if not tel:
            #     return Response(
            #         {"error": "Phone number (tel) is required"},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            createdFrom = request.GET.get("createdFrom")
            createdTo = request.GET.get("createdTo")
            print("debt id is : ",debtID)
            

            if payme_id:
                doc = payments.find_one({"_id": ObjectId(payme_id)})
                if not doc:
                    return Response(
                        {"error": "Payment not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                return Response(
                    {"data": mongo_to_json(doc)},
                    status=status.HTTP_200_OK
                )
            else:
                query = {}

               
                if debtID:
                    query["debt"] = { "$eq": debtID }



                # Date range filter
                if createdFrom or createdTo:
                    date_filter = {}
                    if createdFrom:
                        date_filter["$gte"] = float(createdFrom)
                    if createdTo:
                        date_filter["$lte"] = float(createdTo)
                    query["timestamp"] = date_filter

                payments_data = [
                    mongo_to_json2(d)
                    for d in payments.find(query).sort("timestamp", -1) 
                ]
                # print("payments_data:",payments_data)

                return Response(
                    {"data":payments_data},
                    status=status.HTTP_200_OK
                )
 
        # ---------------- DELETE ----------------
        elif request.method == "DELETE":
            if not payme_id:
                return Response(
                    {"error": "Payment ID is required for deletion"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = payments.delete_one({"_id": ObjectId(payme_id)})

            if result.deleted_count == 0:
                return Response(
                    {"error": "Payment not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Payment deleted"},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        print(e)
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
def checkPhoneNumberExistence(request):
    tel = int(request.data.get("tel"))

    if not tel:
        return Response(
            {"error": "Phone number is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exists = facteurs.find_one({"tel": tel}) is not None

    return Response(
        {
            "tel": tel,
            "exists": exists
        },
        status=status.HTTP_200_OK
    )



@api_view(["POST"])
def addNewPayment(request):
    try:
        tel = int(request.data.get("tel", 0))
        amount = int(request.data.get("amount", 0))
        type = request.data.get("type")
        debtId = request.data.get("debtId", "")
        wallet = request.data.get("wallet", "")

        if not tel:
            return Response({"error": "tel is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get debt
        debt = debts.find_one({"_id": ObjectId(debtId)}) if debtId else debts.find_one({"tel": tel})
        if not debt:
            return Response({"error": "Debt not found for this tel"}, status=status.HTTP_404_NOT_FOUND)

        now_ts = int(datetime.now().timestamp() * 1000)
        FIVE_MINUTES = 5 * 60 * 1000

        # 🔹 Get the last payment for this phone & type
        last_payment = payments.find_one(
            {"tel": tel, "type": type, "wallet": wallet},
            sort=[("timestamp", -1)]
        )

        if last_payment:
            if (last_payment["amount"] == amount) and ((now_ts - last_payment["timestamp"]) < FIVE_MINUTES):
                return Response(
                    {"error": f"تم إضافة هذا المبلغ مسبقاً خلال آخر 5 دقائق."},
                    status=status.HTTP_409_CONFLICT
                )

        # Proceed with payment/debt
        if type == "payment":
            if debt["debt"] < amount:
                return Response({"error": "Payment amount exceeds current debt"}, status=status.HTTP_400_BAD_REQUEST)

            # Update debt
            new_debt = debt["debt"] - amount
            debts.update_one({"_id": debt["_id"]}, {"$set": {"debt": new_debt, "timestamp": now_ts}})

            # Insert payment
            payments.insert_one({
                "note": f"تم دفع مبلغ {amount}",
                "amount": amount,
                "wallet": wallet,
                "facteur": "",
                "tel": tel,
                "debt": str(debt["_id"]),
                "type": "payment",
                "timestamp": now_ts
            })

        elif type == "debt":
            # Update debt
            new_debt = debt["debt"] + amount
            debts.update_one({"_id": debt["_id"]}, {"$set": {"debt": new_debt, "timestamp": now_ts}})

            # Insert debt record
            payments.insert_one({
                "note": f"تم إضافة مبلغ {amount} إلى الدين",
                "amount": amount,
                "wallet": wallet,
                "tel": tel,
                "debt": str(debt["_id"]),
                "facteur": "",
                "type": "debt",
                "timestamp": now_ts
            })

        else:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": True}, status=status.HTTP_200_OK)

    except Exception as e:
        print("=================== error ==============================")
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)







 
 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from datetime import datetime

@api_view(["POST"])
def confirmeFacteur(request):
    try:
        facteur_id = request.data.get("id_facteur")
        
        if not facteur_id:
            return Response({"error": "رقم الفاتورة مطلوب"}, status=status.HTTP_400_BAD_REQUEST)

        # 1️⃣ الحصول على الفاتورة
        facteur = facteurs.find_one({"_id": ObjectId(facteur_id)})
         
        if not facteur:
            return Response({"error": "الفاتورة غير موجودة"}, status=status.HTTP_404_NOT_FOUND)
        
        if facteur.get("send", False):
            return Response({"error": "تم إرسال هذه الفاتورة مسبقًا"}, status=status.HTTP_400_BAD_REQUEST)

        tel = int(facteur.get("tel", 0))
        if tel == 0:
            return Response({"error": "هذه الفاتورة لا تحتوي على رقم هاتف"}, status=status.HTTP_400_BAD_REQUEST)
            
        str_payedPrice = facteur.get("payed_price", 0)
        name = facteur.get("name", "بدون اسم")

        payed_price = int(str_payedPrice) if str_payedPrice else 0
        total = int(facteur.get("total", 0))
        remaining_amount = total - payed_price

        if remaining_amount <= 0:
            facteurs.update_one(
                {"_id": ObjectId(facteur_id)},
                {"$set": {"send": True}}
            )
            return Response({"message": "تم دفع الفاتورة بالكامل مسبقًا"}, status=status.HTTP_200_OK)

        # 2️⃣ تحديث الدين للعميل
        debt = debts.find_one({"tel": tel})

        payment_record = {
            "note": f"تم إضافة مبلغ {remaining_amount} إلى الدين",
            "amount": remaining_amount,
            "wallet": "",
            "tel": tel,
            "facteur": facteur_id,
            "type": "debt",
            "timestamp": int(datetime.now().timestamp() * 1000)
        }

        if debt:
            # تحديث الدين الحالي
            debts.update_one(
                {"_id": debt["_id"]},
                {
                    "$inc": {"debt": remaining_amount},
                    "$set": {"timestamp": int(datetime.now().timestamp() * 1000)}
                }
            )
            payment_record["debt"] = str(debt["_id"])
            payments.insert_one(payment_record)
        else:
            # إنشاء دين جديد إذا لم يكن موجود
            newdebt = debts.insert_one({
                "tel": tel,
                "debt": remaining_amount,
                "name": name,
                "timestamp": int(datetime.now().timestamp() * 1000)
            })
            payment_record["debt"] = str(newdebt.inserted_id)
            payments.insert_one(payment_record)

        # تحديث حالة الفاتورة
        facteurs.update_one(
            {"_id": ObjectId(facteur_id)},
            {"$set": {"send": True}}
        )
        
        return Response({"message": "تم تأكيد الفاتورة وتحديث الدين بنجاح ✅"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("=================== error ==============================")
        print(e)
        return Response({"error": f"حدث خطأ: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(["GET"])

def export_json(request):
    # جلب البيانات من MongoDB
    data = {
        "users": [mongo_to_json(doc) for doc in db['users'].find()],
        "facteurs": [mongo_to_json(doc) for doc in db['facteurs'].find()],
        # "clients": [mongo_to_json(doc) for doc in db['clients'].find()],
        "notes": [mongo_to_json(doc) for doc in db['notes'].find()],
        "debts": [mongo_to_json(doc) for doc in db['debts'].find()],
        "products": [mongo_to_json(doc) for doc in db['products'].find()],
        "payments": [mongo_to_json2(doc) for doc in db['payments'].find()],
        "storeDebts": [mongo_to_json(doc) for doc in db['Stores_debt'].find()],
    }

    # تحويل dict إلى JSON string
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # اسم الملف
    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Response لتحميل الملف مباشرة
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



@api_view(["DELETE"])
def deletePayment(request):
    try:
        payment_id = request.data.get("payment_id")

        if not payment_id:
            return Response({"error": "معرّف الدفع مطلوب"}, status=status.HTTP_400_BAD_REQUEST)

        # 1️⃣ Find the payment
        payment = payments.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            return Response({"error": "الدفع غير موجود"}, status=status.HTTP_404_NOT_FOUND)

        debt_id = payment.get("debt")
        amount = int(payment.get("amount", 0))
        type = payment.get("type")

        # 2️⃣ Update debt if it exists
        if debt_id:
            debt = debts.find_one({"_id": ObjectId(debt_id)})
            if debt:
                new_debt = debt["debt"]
                
                if type == "payment":
                    # Payment decreases debt → deleting it increases debt
                    new_debt += amount
                elif type == "debt":
                    # Debt increases debt → deleting it decreases debt
                    new_debt -= amount

                # Prevent negative debt
                if new_debt < 0:
                    new_debt = 0

                debts.update_one(
                    {"_id": debt["_id"]},
                    {"$set": {"debt": new_debt, "timestamp": int(datetime.now().timestamp() * 1000)}}
                )

        # 3️⃣ Delete the payment
        payments.delete_one({"_id": ObjectId(payment_id)})

        return Response({"message": "تم حذف الدفع بنجاح ✅"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("=================== error ==============================")
        print(e)
        return Response({"error": f"حدث خطأ: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(["GET", "POST", "PATCH", "DELETE"])
def debtsAPI(request, debt_id=None):
    try:
        # ---------------- GET ----------------
        if request.method == "GET":
            tel = int(request.GET.get("tel",0))
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

        elif request.method == "POST":
            data = request.data
            try:
                data['tel'] = int(data["tel"])
            except ValueError:
                return Response(
                {"message": "رقم الهاتف يجب أن يكون عددًا صحيحًا صالحًا"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if this tel already exists
            existing_debt = debts.find_one({"tel": data['tel']})
            if existing_debt:
                return Response(
            {"message": "يوجد بالفعل دين لهذا الرقم"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # If not exists, create new debt
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
        print("======================= error ============================")
        print(e)
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
            tel = request.GET.get("tel",0)
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

from django.http import HttpResponse

@api_view(["GET"])

def download_image(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse("No URL provided", status=400)

    resp = requests.get(url)
    if resp.status_code != 200:
        return HttpResponse("Failed to fetch image", status=400)

    filename = url.split('/')[-1]
    response = HttpResponse(resp.content, content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@api_view(["POST"])
def getDebtsByPhone(request):
    tel = request.data.get("tel",0)
   
    if not tel:
        return Response(
            {"error": "Phone number (tel) is required"},
            status=status.HTTP_400_BAD_REQUEST
        )


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
