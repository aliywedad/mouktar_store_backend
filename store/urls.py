from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .backup import *
 

router = DefaultRouter()
 


urlpatterns = [
    path("facteurs/", facteursAPI, name="facteurs"),
    # GET single / PATCH / DELETE
    path("facteurs/<str:facteur_id>/", facteursAPI, name="facteur-detail"),
    
    path("debts/", debtsAPI, name="debts"),
    path("debts/<str:debt_id>/", debtsAPI, name="debts-detail"),
    
    path("notes/", NotesAPI, name="notes"),
    path("notes/<str:Notes_id>/", NotesAPI, name="notes-detail"),
    path("getDebtsByPhone/", getDebtsByPhone, name="getDebtsByPhone"),
    
    path("confirmeFacteur/", confirmeFacteur, name="confirmeFacteur"),

    
    
    
]
