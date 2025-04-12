from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import views, status, permissions, viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken

# this app serializers
from .serializers import OtpRequestSerializer, OtpVerificationSerializer, ResetPasswordSerializer, \
    ChangePhoneNumberSerializer, CourseSerializer, HeadlineSerializer, SeasonVideoSerializer, \
    TeacherProfileSerializer, TeacherSocialAccountSerializer, EnrollmentSerializer, UserInfoSerializer
from .models import User
# utils
from utils.permissions import IsTeacher

# courses
from courses.models import Course, CourseHeadlines, SeasonVideos, Enrollment
from courses.serializers import CourseDetailSerializer, CourseListSerializer

# orders
from order.models import Order
from order.serializers import OrderListSerializer


# Create your views here.


class OtpRequestView(views.APIView):
    def post(self, request):
        serializer = OtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Otp code sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerificationView(views.APIView):

    def create_token_response(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def post(self, request):
        serializer = OtpVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(self.create_token_response(user), status=status.HTTP_200_OK)


class ResetPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'reset password has been successfully'}, status=status.HTTP_200_OK)


class ChangePhoneNumberView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'phone number change has been successfully'}, status=status.HTTP_200_OK)

# - - - - - - - - - - - - - - - - - - - - - - Teacher views - - - - - - - - - - - - - - - - - - - - - - - - -

class BaseViewSet(viewsets.ModelViewSet):
    """
        A base viewset providing standard CRUD operations with custom messages and permission handling.
    """

    create_message = 'successfully created!'
    update_message = 'successfully updated!'
    destroy_message = 'successfully deleted!'

    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': self.create_message}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': self.update_message}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # the find object teacher
        teacher = None
        if isinstance(instance, Course):
            teacher = instance.teacher
        elif isinstance(instance, CourseHeadlines):
            teacher = instance.course.teacher
        elif isinstance(instance, SeasonVideos):
            teacher = instance.headline.course.teacher

        # check permission
        if teacher and teacher != request.user:
            raise PermissionDenied("You do not have permission to delete this.")

        instance.delete()
        return Response({'message': self.destroy_message}, status=status.HTTP_200_OK)


class CourseViewSet(BaseViewSet):
    """
    ViewSet for managing courses. Supports creation, update, and retrieval of courses.
    """

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(teacher=user)


class HeadLineViewSet(BaseViewSet):
    """
    ViewSet for managing course headlines. Supports creation, update, and retrieval of headlines for a course.
    """
    serializer_class = HeadlineSerializer
    queryset = CourseHeadlines.objects.all()


class SeasonVideoViewSet(BaseViewSet):
    """
    ViewSet for managing season videos. Supports creation, update, and retrieval of videos for course headlines.
    """
    serializer_class = SeasonVideoSerializer
    queryset = SeasonVideos.objects.all()



class TeacherEditProfileView(views.APIView):
    """
    Handles editing teacher profile information.
    """

    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeSocialAccountView(views.APIView):
    """
    Allows teachers to update their social media accounts.
    """
    serializer_class = TeacherSocialAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherCoursesListView(views.APIView):
    """
    Returns a list of courses created by the authenticated teacher.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseListSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)




# - - - - - - - - - - - - - - - - - - - - - - - - user views  - - - - - - - - - - - - - - - - - - - - - - - - - -
class UserInfoView(views.APIView):
    """
    Returns basic information of the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEnrollmentsView(views.APIView):
    """
    Retrieves a list of the user's course enrollments.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get(self, request, *args, **kwargs):
        enrollments = Enrollment.objects.filter(student_id=request.user.id)
        serializer = self.serializer_class(enrollments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserOrdersView(views.APIView):
    """
    Fetches the list of orders made by the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderListSerializer
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(student_id=request.user.id)
        serializer = self.serializer_class(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
