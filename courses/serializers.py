from rest_framework import serializers
from django.db.models import Sum
from .models import Category, Course, CourseSubDescription, CourseHeadlines, SeasonVideos
from moviepy import VideoFileClip
import tempfile
import os


class SeasonVideosSerializer(serializers.ModelSerializer):
    """
      Serializer for SeasonVideos model.
      Converts SeasonVideos instances into JSON format and vice versa.
    """

    class Meta:
        model = SeasonVideos
        fields = ['video_title', 'video_file', 'description', 'attached_file', 'duration', 'is_free']


class CourseHeadlineSerializer(serializers.ModelSerializer):
    """
    Serializer for CourseHeadlines model.
    Includes related SeasonVideos and provides course headline details.
    """

    videos = SeasonVideosSerializer(many=True)  # headline videos
    duration = serializers.SerializerMethodField()

    class Meta:
        model = CourseHeadlines
        fields = ['headline_title', 'chapter_number', 'videos', 'duration']

    def get_duration(self, obj):
        duration = str(obj.duration ).replace('.', ':')
        return f'{duration} min'


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    Provides category name and slug information.
    """

    class Meta:
        model = Category
        fields = ['name', 'slug']


class CourseSubDescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseSubDescription model.
    Handles course sub-title, image, and sub-description fields.
    """

    class Meta:
        model = CourseSubDescription
        fields = ['sub_title', 'image', 'sub_description']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses with essential details.
    """
    category = serializers.StringRelatedField()  # Course category name
    teacher = serializers.StringRelatedField()  # Course instructor name

    # URL to course details
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='courses:course_detail',
        lookup_field='slug'
    )

    class Meta:
        model = Course
        fields = [
            'category', 'title', 'thumbnail', 'teacher', 'price', 'final_price', 'detail_url',
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed course information.
    """
    sub_descriptions = CourseSubDescriptionSerializer(many=True)  # Additional course descriptions
    headlines = serializers.SerializerMethodField()  # Active course sections
    teacher = serializers.StringRelatedField()  # Course instructor name
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_duration(self, obj):
        duration = str(obj.duration).replace('.', ':')
        return f'{duration} min'

    def get_headlines(self, obj):
        obj.duration = obj.headlines.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        result = obj.headlines.filter(is_active=True)
        return CourseHeadlineSerializer(instance=result, many=True).data


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class CreateCourseSerializer(serializers.ModelSerializer):
    """
     Serializer for creating a new course. It associates the course with the current teacher (user).
    """

    class Meta:
        model = Course
        fields = ['category', 'title', 'description', 'slug', 'price', 'off', 'status']

    def create(self, validated_data):
        teacher = self.context['request'].user
        # set course teacher
        course = Course.objects.create(teacher=teacher, **validated_data)
        return course


class CreateHeadlineSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new headline for a course.
    It ensures that the user is the teacher of the course before allowing the creation.
    """

    class Meta:
        model = CourseHeadlines
        fields = ['course', 'headline_title', 'chapter_number', 'is_active']

    def validate(self, data):
        teacher = self.context['request'].user
        course = data['course']

        # checks authenticated user is the teacher of the course
        if course.teacher != teacher:
            raise serializers.ValidationError({'error : ': 'You are not the instructor of this course'})
        return data


class CreateSeasonVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new video in a course's season. It ensures that the user is the instructor
    of the course associated with the headline, and also calculates the video's duration.
    """

    class Meta:
        model = SeasonVideos
        fields = ['headline', 'video_title', 'video_file', 'description', 'attached_file']

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
        duration = 0
        video_file = validated_data.get('video_file')

        if video_file:
            try:
                # create temporary file
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

        # save duration video
        season_video = SeasonVideos.objects.create(duration=duration, **validated_data)
        return season_video
