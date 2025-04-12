from rest_framework import serializers
from .models import Cart, CartItem

from courses.models import Course, Enrollment
from order.models import Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['course']

    def get_course(self, obj):
        return obj.course.title


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'cart_total_price']


class UpdateCartSerializer(serializers.Serializer):
    """
    Serializer for updating cart.
    Supported add and remove actions.
    """
    course_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['add', 'remove'])

    def validate(self, data):
        course_id = data.get('course_id')

        try:
            Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError({'message': 'Course Not Found'})

        return data

    def update(self, instance, validated_data):
        cart = instance
        course_id = validated_data['course_id']
        action = validated_data['action']

        if action == 'add':
            # check exist cart item
            if CartItem.objects.filter(cart=cart, course_id=course_id).exists():
                raise serializers.ValidationError({'message': 'Course already exists in cart'})
            CartItem.objects.create(cart=cart, course_id=course_id)

        elif action == 'remove':
            try:
                cart_item = CartItem.objects.get(cart=cart, course_id=course_id)
                cart_item.delete()
                # check empty cart and delete it
                if cart.is_empty():
                    cart.delete()
            except CartItem.DoesNotExist:
                raise serializers.ValidationError({'message': 'Course not found in cart'})

        return cart


class PurchaseCartSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()

    def validate_cart_id(self, cart_id):
        user = self.context['request'].user
        try:
            cart = Cart.objects.get(id=cart_id, user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("cart does not exist")

        if not cart.items.exists():
            raise serializers.ValidationError("cart is empty")

        return cart

    def create(self, validated_data):
        user = self.context['request'].user
        cart = validated_data['cart_id']
        # create order
        order = Order.objects.create(student=user)


        purchased_courses = []

        # check and buy cart courses
        for item in cart.items.all():
            course = item.course
            if not Enrollment.objects.filter(student=user, course=course).exists():
                Enrollment.objects.create(student=user, course=course)
                # add to order item
                OrderItem.objects.create(order=order, course=item.course, price=item.course.final_price)
                # append to list
                purchased_courses.append(course)
        # delete cart after buy
        cart.delete()

        # set True for order is_paid field
        order.is_paid = True
        order.save()

        return {"purchased_courses": purchased_courses}
