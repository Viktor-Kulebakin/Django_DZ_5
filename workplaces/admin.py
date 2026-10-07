from django.contrib import admin
from .models import Workplace


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'is_occupied', 'equipment_info')
    list_filter = ('is_occupied',)
    search_fields = ('table_number',)
