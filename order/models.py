from django.db import models
from courses.models import Course
from accounts.models import User


# Create your models here.

class Order(models.Model):
    """
    Represents an order made by a student.
    Each order is associated with a student, a payment status, and a creation date.
    Provides a property method to calculate the total cost of the order.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student)

    class Meta:
        """
        Orders are ordered by the creation date.
        """
        ordering = ['created']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    @property
    def get_total_cost(self):
        """
        Calculates the total cost of the order by summing the final prices of all items.
        """
        total = sum(item.price for item in self.items.all())
        return total


class OrderItem(models.Model):
    """
    Represents an item in an order, linking a course to a specific order.
    Each item is associated with an order and a course.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='orders', on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()


    def __str__(self):
        return str(self.order)

    class Meta:
        """
        Meta options for the OrderItem model.
        """
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'


