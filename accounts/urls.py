from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# teacher router
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'headlines', views.HeadLineViewSet, basename='headlines')
router.register(r'videos', views.SeasonVideoViewSet, basename='videos')

router.register('teacher-social-accounts', views.TeacherSocialAccountViewSet, basename='teacher-social-accounts')

app_name = 'accounts'

urlpatterns = [
    # auth and accesses
    path('otp-request/', views.OtpRequestView.as_view(), name='otp_request'),
    path('otp-verify/', views.OtpVerificationView.as_view(), name='otp_verify'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-phone-number/', views.ChangePhoneNumberView.as_view(), name='change_phone_number'),

    # teacher dashboard
    path('teacher/info/', views.TeacherInfoView.as_view(), name='teacher_info'),

    path('teacher/courses/', views.TeacherCoursesListView.as_view(), name='teacher_courses'),


    # user dashboard
    path('user/info/', views.UserInfoView.as_view(), name='user_info'),
    path('user/enrollments/', views.UserEnrollmentsView.as_view(), name='user_enrollments'),
    path('user/orders/', views.UserOrdersView.as_view(), name='user_orders'),

]

urlpatterns += router.urls