from django.db import models
from accounts.models import User
from courses.models import Course

# Create your models here.


class Cart(models.Model):
    """
    Cart Model
    This Model is used to store the cart
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    def is_empty(self):
        return not self.items.exists()

    @property
    def cart_total_price(self):
        """
        The sum total of the cart prices
        """
        return sum(item.course.final_price for item in self.items.all())


class CartItem(models.Model):
    """
    CartItem Model
    This Model is used the cart item
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cart_courses')