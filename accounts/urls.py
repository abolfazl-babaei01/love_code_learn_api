from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'headlines', views.HeadLineViewSet, basename='headlines')
router.register(r'videos', views.SeasonVideoViewSet, basename='videos')


app_name = 'accounts'

urlpatterns = [
    path('otp-request/', views.OtpRequestView.as_view(), name='otp_request'),
    path('otp-verify/', views.OtpVerificationView.as_view(), name='otp_verify'),

    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-phone-number/', views.ChangePhoneNumberView.as_view(), name='change_phone_number'),

    # teacher account info

    path('edit-account/', views.TeacherEditAccountView.as_view(), name='edit_account'),
    path('change-social-account/', views.ChangeSocialAccountView.as_view(), name='change_social_account'),
]

urlpatterns += router.urls