from rest_framework import serializers
from .models import Category, Course, CourseSubDescription, CourseHeadlines, SeasonVideos


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
            'category', 'title', 'thumbnail', 'teacher', 'price', 'final_price', 'detail_url', 'is_free'
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
        result = obj.headlines.filter(is_active=True)
        return CourseHeadlineSerializer(instance=result, many=True).data