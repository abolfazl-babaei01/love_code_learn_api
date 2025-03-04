from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.auth import password_validation
from utils.validators import phone_regex
from .models import Otp, User, TeacherSocialAccount
# other module
from moviepy import VideoFileClip
import tempfile
import os
# courses module
from courses.models import Course, CourseHeadlines, SeasonVideos


class OtpRequestSerializer(serializers.Serializer):
    """
    OtpRequestSerializer checks the entered phone number and sends the otp code.
    """
    # receive the phone number
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])

    def create(self, validated_data):
        otp, created = Otp.objects.get_or_create(phone_number=validated_data.get('phone_number'))

        # checks otp delay
        if otp.valid_delay():
            otp.regenerate_otp()
            otp.send_sms_otp()
        else:
            raise serializers.ValidationError({'message': 'Otp code has not expired'})
        return otp


class BaseOtpVerificationSerializer(serializers.Serializer):
    """
    Base OTP verification serializer for validate otp and entered phone number.
    Adds the valid OTP code in the self object
    """
    phone_number = serializers.CharField(max_length=11, validators=[phone_regex])
    otp = serializers.CharField(max_length=6)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.otp_verification = None

    def validate(self, data):
        otp = data.get('otp')
        phone_number = data.get('phone_number')
        try:
            # finds the otp code
            otp_code = Otp.objects.get(phone_number=phone_number)
        except Otp.DoesNotExist:
            raise serializers.ValidationError('Invalid phone number or otp code')

        if not otp_code.is_otp_valid(otp) or not otp.isdigit():
            raise serializers.ValidationError('Invalid otp code or expired')
        self.otp_verification = otp_code  # adds the correct otp code in self obj
        return data


class OtpVerificationSerializer(BaseOtpVerificationSerializer):
    """
    This serializer returns the user if it is already found, otherwise it creates a user
    """

    password = serializers.CharField(
        write_only=True,
        max_length=8,
        required=False
    )

    def create(self, validated_data):
        password = validated_data.get('password', None)
        phone_number = validated_data.get('phone_number')

        # get user
        user = User.objects.filter(phone_number=phone_number).first()

        # if the user does not exist
        if not user:
            if not password:
                raise serializers.ValidationError({'Error': 'Password is required for registration'})

            user = User.objects.create_user(
                phone_number=phone_number, password=password)  # the password is encrypted in the manager

        self.otp_verification.delete()
        return user


class ResetPasswordSerializer(BaseOtpVerificationSerializer):
    """
    Serializer for resetting a user's password after OTP verification.
    Ensures old password correctness and validates the new password before updating.
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def get_user(self, data):
        """
        It finds and returns the user based on the mobile number
        """
        user = User.objects.get(phone_number=data.get('phone_number'))
        if not user:
            raise serializers.ValidationError({'Error': 'User does not exist'})
        return user

    def validate(self, data):
        data = super().validate(data)
        user = self.get_user(data)

        # Checks the entered new password
        password_validation.validate_password(data.get('new_password'))

        # Checks the old password
        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError({'Error': 'old password is incorrect'})

        return data

    def save(self):
        # find user
        user = self.get_user(self.validated_data)

        # set new password for user
        user.set_password(self.validated_data.get('new_password'))
        user.save()
        self.otp_verification.delete()  # delete user otp code
        return user


class ChangePhoneNumberSerializer(BaseOtpVerificationSerializer):
    """
    Serializer for changing a user's phone number after OTP verification.
    Ensures the new phone number is not already in use before updating.
    """

    def save(self):
        new_phone_number = self.validated_data.get('phone_number')
        user = self.context['request'].user

        # Checks already exist phone number or no
        if User.objects.filter(phone_number=new_phone_number).exists():
            raise serializers.ValidationError({'Error': 'Phone number already exists'})

        # set new phone number
        user.phone_number = new_phone_number
        user.save()
        self.otp_verification.delete()
        return user


# --------------------------------------------teachers panel------------------------------------------------------

class CourseSerializer(serializers.ModelSerializer):
    """
     Serializer for creating a new course. It associates the course with the current teacher (user).
    """

    class Meta:
        model = Course
        fields = ['category', 'title', 'thumbnail', 'description', 'slug', 'price', 'off', 'status', 'is_free']
        extra_kwargs = {
            'price': {'required': True},
        }

    def create(self, validated_data):
        teacher = self.context['request'].user
        # set course teacher
        course = Course.objects.create(teacher=teacher, **validated_data)
        return course


class HeadlineSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new headline for a course.
    It ensures that the user is the teacher of the course before allowing the creation.
    """

    class Meta:
        model = CourseHeadlines
        fields = ['course', 'headline_title', 'chapter_number', 'is_active', 'duration']

    def validate(self, data):
        teacher = self.context['request'].user
        course = data['course']

        # checks authenticated user is the teacher of the course
        if course.teacher != teacher:
            raise serializers.ValidationError({'error : ': 'You are not the instructor of this course'})
        return data


class SeasonVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new video in a course's season. It ensures that the user is the instructor
    of the course associated with the headline, and also calculates the video's duration.
    """

    class Meta:
        model = SeasonVideos
        fields = ['headline', 'video_title', 'video_file', 'description', 'attached_file', 'duration']

    def validate(self, data):
        """
        Validates that the authenticated user is the instructor of the course associated with the headline.
        """
        teacher = self.context['request'].user
        headline = data['headline']

        if headline.course.teacher != teacher:
            raise serializers.ValidationError({'error : ': 'You are not the instructor of this course'})

        return data

    def create(self, validated_data):
        """
        Creates a new season video, calculates the video duration, and deletes the temporary video file.
        """
        return self._set_video_duration(validated_data)

    def update(self, instance, validated_data):
        """
        Updates an existing season video, recalculates the video duration if the video file is changed.
        """
        video_file = validated_data.get('video_file', None)
        if video_file:
            validated_data['duration'] = self._calculate_video_duration(video_file)
        return super().update(instance, validated_data)

    def _set_video_duration(self, validated_data):
        """
        Sets the video duration during creation.
        """
        video_file = validated_data.get('video_file')
        duration = 0

        if video_file:
            duration = self._calculate_video_duration(video_file)

        # save video with calculated duration
        season_video = SeasonVideos.objects.create(duration=duration, **validated_data)
        return season_video

    def _calculate_video_duration(self, video_file):
        """
        Calculates the duration of the video file and returns it.
        """
        duration = 0
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(video_file.read())  # write file in temporary memory
                temp_video_path = temp_video.name  # get the temporary file path

            # calculate video duration
            clip = VideoFileClip(temp_video_path)
            duration = clip.duration
            clip.close()
            # delete file from temporary memory
            os.remove(temp_video_path)

            duration = round(duration / 60, 2)
        except Exception as e:
            print(f"Error processing video file: {e}")

        return duration


class TeacherSocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSocialAccount
        fields = ['name', 'link']

    def create(self, validated_data):
        teacher = self.context['request'].user
        return TeacherSocialAccount.objects.create(teacher=teacher, **validated_data)


class TeacherEditAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'first_name', 'last_name', 'bio']
