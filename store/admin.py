from django.contrib import admin
from .models import Users, Days, Transactions


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


@admin.register(Days)
class DaysAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date', 'benefit', 'operationsR', 'operationsV', 'Balance')
    search_fields = ('name',)
    list_filter = ('date',)
    ordering = ('-date',)


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'amount', 'comission', 'before', 'after', 'day', 'userName', 'created_at')
    search_fields = ('userName', 'type')
    list_filter = ('type', 'created_at', 'day')
    ordering = ('-created_at',)
