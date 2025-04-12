from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'headlines', views.HeadLineViewSet, basename='headlines')
router.register(r'videos', views.SeasonVideoViewSet, basename='videos')


app_name = 'accounts'

urlpatterns = [
    # auth and accesses
    path('otp-request/', views.OtpRequestView.as_view(), name='otp_request'),
    path('otp-verify/', views.OtpVerificationView.as_view(), name='otp_verify'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-phone-number/', views.ChangePhoneNumberView.as_view(), name='change_phone_number'),

    # teacher dashboard
    path('teacher/edit-profile/', views.TeacherEditProfileView.as_view(), name='edit_profile'),
    path('teacher/social-media/', views.ChangeSocialAccountView.as_view(), name='change_social_account'),
    path('teacher/courses/', views.TeacherCoursesListView.as_view(), name='teacher_courses'),


    # user dashboard
    path('user/info/', views.UserInfoView.as_view(), name='user_info'),
    path('user/enrollments/', views.UserEnrollmentsView.as_view(), name='user_enrollments'),
    path('user/orders/', views.UserOrdersView.as_view(), name='user_orders'),

]

urlpatterns += router.urls