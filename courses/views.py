from rest_framework import permissions, generics
from .models import Course
from .serializers import CourseListSerializer, CourseDetailSerializer

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
