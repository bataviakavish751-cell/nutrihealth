# home/admin.py
from django.contrib import admin
from .models import HealthProfile, BarcodeHistory, DietPlan, ScannedProduct
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    # Use correct field name or create a method
    list_display = ['user', 'get_health_conditions', 'age', 'weight', 'height', 'created_at']
    
    # Create a method to display health_conditions
    def get_health_conditions(self, obj):
        return obj.health_conditions[:50] + "..." if obj.health_conditions else "None"
    get_health_conditions.short_description = 'Health Conditions'

@admin.register(BarcodeHistory)
class BarcodeHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'barcode', 'product_name', 'scanned_at']
    list_filter = ['user', 'scanned_at']
    search_fields = ['product_name', 'barcode']

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    # Use 'created_at' not 'generated_at'
    list_display = ['user', 'get_plan_preview', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']  # Use 'created_at' here too
    search_fields = ['user__username', 'plan_content']
    
    def get_plan_preview(self, obj):
        return obj.plan_content[:100] + "..." if len(obj.plan_content) > 100 else obj.plan_content
    get_plan_preview.short_description = 'Plan Preview'

@admin.register(ScannedProduct)
class ScannedProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_name', 'barcode', 'scanned_at']
    list_filter = ['user', 'scanned_at']
    search_fields = ['product_name', 'barcode']

# Allow HealthProfile inside User page
class HealthProfileInline(admin.StackedInline):
    model = HealthProfile
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [HealthProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
