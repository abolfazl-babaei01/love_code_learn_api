from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'cart_total_price']
    inlines = [CartItemInline]
