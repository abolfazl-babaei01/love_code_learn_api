from django.contrib import admin
from .models import Course, CourseSubDescription, CourseHeadlines, SeasonVideos, Category, Enrollment
# Register your models here.

class SubDescriptionInline(admin.StackedInline):
    model = CourseSubDescription
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'status']
    inlines = [SubDescriptionInline]


@admin.register(CourseHeadlines)
class CourseHeadlinesAdmin(admin.ModelAdmin):
    list_display = ['headline_title', 'course', 'chapter_number']
    list_filter = ['course']
    search_fields = ['headline_title', 'course__title']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

@admin.register(SeasonVideos)
class SeasonVideosAdmin(admin.ModelAdmin):
    list_display = ['video_title', 'duration', 'is_free']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course']
