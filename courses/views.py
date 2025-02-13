from rest_framework import status, permissions, generics
from rest_framework.response import Response
from .models import Course, CourseHeadlines, SeasonVideos
from .serializers import (CourseListSerializer, CourseDetailSerializer, CreateCourseSerializer,
                          CreateSeasonVideoSerializer, CreateHeadlineSerializer)

from utils.permissions import IsTeacher
# Create your views here.


class CourseListView(generics.ListAPIView):
    """
    API view for listing all published courses.
    """
    permission_classes = [permissions.AllowAny]  # Accessible to all users
    serializer_class = CourseListSerializer  # Serializer for course listing
    queryset = Course.objects.filter(release_status='published')  # Only published courses



class CourseDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving the details of a published course by its slug.

    """
    permission_classes = [permissions.AllowAny]  # Accessible to all users
    serializer_class = CourseDetailSerializer  # Serializer for course details
    queryset = Course.objects.filter(release_status='published')  # Only published courses
    lookup_field = 'slug'  # Lookup by slug field
    lookup_url_kwarg = 'slug'  # URL parameter for lookup



class BaseCreateAPIView(generics.CreateAPIView):

    """
    Base class for creating objects with a custom success message.
    Inherits from `CreateAPIView` and provides a standardized way to create new objects.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Override to add the request context to the serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create an object and return a success message.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message ': f' {self.success_message}'}, status=status.HTTP_201_CREATED)

class CreateCourseAPIView(BaseCreateAPIView):
    """
    API View to create a new course.
    """
    serializer_class = CreateCourseSerializer
    queryset = Course.objects.all()
    success_message = 'Successfully created a new course.'



class CreateHeadLineAPIView(BaseCreateAPIView):
    """
    API View to create a new headline for a course.
    """
    serializer_class = CreateHeadlineSerializer
    queryset = CourseHeadlines.objects.all()
    success_message = 'Successfully created a new headline for this course.'




class CreateSeasonVideoAPIView(BaseCreateAPIView):
    """
    API View to create a new video for a headline.
    """
    serializer_class = CreateSeasonVideoSerializer
    queryset = SeasonVideos.objects.all()
    success_message = 'Successfully created a new video for this headlines.'