from django.db import models




class Users(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=False)
    password = models.CharField(max_length=255, blank=True, null=False)
    token = models.CharField(max_length=255, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    roles = models.JSONField(default=list, blank=True)
    agency = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, default="active")


    def __str__(self):
        return self.name
class Phones(models.Model):
    phone = models.CharField(max_length=50,unique=True)
     

    def __str__(self):
        return self.phone
from datetime import date

class Agency(models.Model):
    name = models.CharField(max_length=200,unique=True)
    expireDate=models.DateField()
    def is_expired(self):
        """Return True if the agency's expire date is in the past."""
        return self.expireDate < date.today()
class Days(models.Model):
    name = models.CharField(max_length=50)
    benefit=models.FloatField(default=0)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency')
    operationsR=models.IntegerField(default=0)
    operationsV=models.IntegerField(default=0)
    date=models.DateField(auto_now_add=True)
    initBalance=models.FloatField(default=0)
    Balance=models.FloatField(default=0)
    cash=models.FloatField(default=0)

    def __str__(self):
        return self.name
from django.utils import timezone

class LastTransaction(models.Model):
    phone = models.IntegerField()
    amount = models.FloatField()
    type = models.CharField(max_length=16)
    day = models.ForeignKey('Days', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['phone', 'type', 'day']),  # fast lookup
        ]

    def __str__(self):
        return f"{self.type} - {self.amount} on {self.day.name}"
    
    
    
class Transactions(models.Model):
    TYPE_CHOICES = [
        ('versement', 'Versement'), #versement
        ('retrait', 'Retrait'),#retrait
        ('retrait_coms', 'Retrait_coms'),#retrait
        ('retraitMostevid', 'RetraitMostevid'),
        ('augmante', 'Augmante'),
        ('check', 'Check'),
        ('manualeVersement', 'ManualeVersement'), #versement
        ('manualeRetrait', 'ManualeRetrait'),#retrait
        
    ]
    day = models.ForeignKey(Days, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    amount = models.FloatField()
    phone = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comission=models.FloatField(default=0)
    before=models.FloatField(default=0)
    agency=models.CharField(max_length=255, blank=False, null=False)
    descriptions = models.CharField(max_length=255, blank=True, null=True)
    after=models.FloatField(default=0)
    cashAfter=models.FloatField(default=0)
    cashBefore=models.FloatField(default=0)
    isCanceled=models.BooleanField(default=False)
    userName=models.CharField(max_length=255, blank=True, null=True)
    user=models.ForeignKey(Users, on_delete=models.CASCADE, related_name='transactions',null=True)

    def __str__(self):
        return f"{self.type} - {self.amount} on {self.day.name}"
    
    
    
    