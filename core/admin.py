from django.contrib import admin
from .models import User, Pet, Doctor, MedicalRecord
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email","password")}),
        ("Personal", {"fields": ("first_name","last_name","phone_number")}),
        ("Permissions", {"fields": ("is_active","is_staff","is_superuser","role")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email","password1","password2","role")}),
    )
    list_display = ("email","first_name","last_name","role","is_staff")
    ordering = ("email",)

admin.site.register([Pet, Doctor, MedicalRecord])