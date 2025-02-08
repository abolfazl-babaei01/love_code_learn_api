from rest_framework.response import Response
from rest_framework import views, status, permissions
from .serializers import OtpRequestSerializer, OtpVerificationSerializer, ResetPasswordSerializer, \
    ChangePhoneNumberSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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