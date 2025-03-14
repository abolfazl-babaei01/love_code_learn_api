from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartItemsListView.as_view(), name='cart_list'),
    path('update/', views.UpdateCartView.as_view(), name='update_cart')
]
