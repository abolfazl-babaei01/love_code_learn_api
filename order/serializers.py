from rest_framework import serializers
from .models import Order, OrderItem
from courses.serializers import CourseListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying order item details including the course information.
    Each item includes the course associated with the order.
    """

    course = CourseListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['course']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying general order details including items, total cost,
    payment status, and the creation date of the order.
    """

    items = OrderItemSerializer(many=True) # get order items
    student = serializers.StringRelatedField() # display student name
    created = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['student', 'items', 'get_total_cost', 'is_paid', 'created']

    def get_created(self, obj):
        """
        the add formated created date
        """
        return obj.created.strftime('%d/%m/%Y %H:%M')
