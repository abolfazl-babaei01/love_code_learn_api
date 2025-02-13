from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create-course/', views.CreateCourseAPIView.as_view(), name='create'),

    path('create-headline/', views.CreateHeadLineAPIView.as_view(), name='create_headline'),

    path('create-video/', views.CreateSeasonVideoAPIView.as_view(), name='create_video'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),

]
