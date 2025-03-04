from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.validators import phone_regex
from .managers import UserManager

from django.utils.timezone import now
from datetime import timedelta
import random
import string

# Create your models here.

def generate_random_otp_code():
    return ''.join(random.choices(string.digits, k=6))

class Otp(models.Model):
    phone_number = models.CharField(max_length=11, validators=[phone_regex, ])
    otp_code = models.CharField(max_length=6, default=generate_random_otp_code())
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Otp for {self.phone_number}'

    def regenerate_otp(self):
        """
        Generate new OTP code and save it to database.
        """
        self.otp_code = generate_random_otp_code()
        self.save()

    def valid_delay(self):
        """
        Checks if at least 3 minutes have passed since the last OTP generation.
        """
        if self.created_at and now() <= self.created_at + timedelta(minutes=3):
            return False

        self.created_at = now()
        self.save()
        return True

    def is_otp_valid(self, otp):
        """
        Verifies if the provided OTP matches the generated code and
        ensures it has not expired (valid for up to 5 minutes).
        """
        if self.otp_code == str(otp) and now() <= self.created_at + timedelta(minutes=5):
            return True
        return False

    def send_sms_otp(self):
        """
        send sms to user phone number
        """
        print(f"Otp code {self.otp_code} To {self.phone_number}")


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_regex])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.username

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class TeacherSocialAccount(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    name = models.CharField(max_length=50)
    link = models.URLField()

    def __str__(self):
        return self.name

    def clean(self):
        if not self.teacher.is_teacher():
            raise ValidationError({'teacher': f'This account `{self.teacher}` is not a teacher'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Teacher Social Account'
        verbose_name_plural = 'Teachers Social Accounts'

