from django.contrib import admin
from .models import User, Otp, TeacherSocialAccount

# Register your models here.

@admin.register(TeacherSocialAccount)
class TeacherSocialAccountAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'name', 'link']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'role']
    list_filter = ['role']


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code']