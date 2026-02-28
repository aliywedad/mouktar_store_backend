from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .backup import *
 

router = DefaultRouter()
 


urlpatterns = [ 
    path("facteurs/", facteursAPI, name="facteurs"),
    path("storesDebtAPI/", storesDebtAPI, name="storesDebtAPI"),
    # GET single / PATCH / DELETE
    path("storesDebtAPI/<str:storesDebt_id>/", storesDebtAPI, name="storesDebtAPI-detail"),
    path("facteurs/<str:facteur_id>/", facteursAPI, name="facteur-detail"),
    
    path("debts/", debtsAPI, name="debts"),
    path("debts/<str:debt_id>/", debtsAPI, name="debts-detail"),
    
    
    path("stockChangesAPI/", stockChangesAPI, name="stockChangesAPI"),
    path("stockChangesAPI/<str:change_id>/", stockChangesAPI, name="stockChangesAPI-detail"),
    
    path("factoryAPI/", factoryAPI, name="factoryAPI"),
    path("factoryAPI/<str:factory_id>/", factoryAPI, name="factoryAPI-detail"),
    
 
    
    path("stockAPI/", stockAPI, name="stockAPI"),
    path("stockAPI/<str:stock_id>/", stockAPI, name="stockAPI-detail"),
    
    path("products/", productsAPI, name="products"),
    path("api/export_data_to_telegram/", export_data_to_telegram, name="export_data_to_telegram"),
    path("products/<str:product_id>/", productsAPI, name="products-detail"),

    path("payments/", paymentsAPI, name="payments"),
    path("payments/<str:payme_id>/", paymentsAPI, name="payments-detail"),
    path('api/upload/', upload_facteur_image, name='upload_image'),
    path('download_image/', download_image, name='download_image'),
    path('deletePayment/', deletePayment, name='deletePayment   '),
    path('export_json/', export_json, name='export_json'),
    path('addStockChangesAPI/', addStockChangesAPI, name='addStockChangesAPI'),
    
    
    
    path("notes/", NotesAPI, name="notes"),
    path("notes/<str:Notes_id>/", NotesAPI, name="notes-detail"),
    path("getDebtsByPhone/", getDebtsByPhone, name="getDebtsByPhone"),
    
    path("confirmeFacteur/", confirmeFacteur, name="confirmeFacteur"),
    path("addNewPayment/", addNewPayment, name="addNewPayment"),
    path("checkPhoneNumberExistence/", checkPhoneNumberExistence, name="checkPhoneNumberExistence"),
    
    

    
    
    
]
