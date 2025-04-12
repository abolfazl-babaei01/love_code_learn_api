from django.db.models import Q
from rest_framework import permissions, generics, views, status
from rest_framework.response import Response

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


class CourseDetailView(views.APIView):
    """
    API view for retrieving course details.
    - Public users can only see published courses.
    - Teachers can see their own courses even if unpublished.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        user = request.user

        if user.is_authenticated:
            course = Course.objects.filter(
                Q(slug=slug) & (Q(release_status="published") | Q(teacher=user))
            ).first()
        else:
            course = Course.objects.filter(slug=slug, release_status="published").first()

        if not course:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDetailSerializer(instance=course)
        return Response(serializer.data, status=status.HTTP_200_OK)