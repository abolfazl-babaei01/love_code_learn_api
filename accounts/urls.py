from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('otp-request/', views.OtpRequestView.as_view(), name='otp_request'),
    path('otp-verify/', views.OtpVerificationView.as_view(), name='otp_verify'),

    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-phone-number/', views.ChangePhoneNumberView.as_view(), name='change_phone_number'),


]
