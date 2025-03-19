from django.shortcuts import get_object_or_404
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart
from .serializers import CartSerializer, UpdateCartSerializer, PurchaseCartSerializer
from courses.models import Enrollment, Course


# Create your views here.


class CartItemsListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class UpdateCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = UpdateCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(cart, serializer.validated_data)
        return Response({'message': 'action successfully.'}, status=status.HTTP_200_OK)


class PurchaseCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PurchaseCartSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {"detail": "Courses successfully purchased!", "courses": [c.title for c in result["purchased_courses"]]},
            status=status.HTTP_201_CREATED)
