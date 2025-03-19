from rest_framework import generics, permissions
from order.models import Order
from order.serializers import OrderListSerializer
from utils.permissions import IsAuthAndOwner


# Create your views here.


class OrderListView(generics.ListCreateAPIView):
    """
    API view to list all orders for the authenticated user order.
    Only orders belonging to the current user are returned.
    """
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthAndOwner]

    def get_queryset(self):
        """
        Restrict the queryset to only orders associated with the authenticated user.
        """
        return Order.objects.filter(student=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve detailed information about a specific order for the authenticated user.
    Only allows access to orders belonging to the current user.
    """
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthAndOwner]
