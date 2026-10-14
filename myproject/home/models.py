# home/models.py
from django.db import models
from django.contrib.auth.models import User

# DELETE this line - it's causing circular import
# from .models import HealthProfile, BarcodeHistory, DietPlan  # DELETE THIS LINE

class HealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Make sure field names are correct
    health_conditions = models.TextField(blank=True, null=True)  # Note: plural 'conditions'
    allergies = models.TextField(blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Not 'generated_at'
    
    def __str__(self):
        return f"{self.user.username}'s Health Profile"

class BarcodeHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product_name}"

class DietPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Correct field name
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Diet Plan for {self.user.username} - {self.created_at.date()}"

# Add ScannedProduct model if you need it
class ScannedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    nutritional_info = models.TextField(blank=True, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} scanned by {self.user.username}"