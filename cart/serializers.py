from rest_framework import serializers
from .models import Cart, CartItem

from courses.models import Course


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['course']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Cart
        fields = ['user', 'items', 'cart_total_price']


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
