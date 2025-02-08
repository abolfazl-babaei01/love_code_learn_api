from django.contrib import admin
from .models import Course, CourseSubDescription, CourseHeadlines, SeasonVideos

# Register your models here.

class SubDescriptionInline(admin.StackedInline):
    model = CourseSubDescription
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'status']
    inlines = [SubDescriptionInline]


class SeasonVideosInline(admin.StackedInline):
    model = SeasonVideos
    extra = 1

@admin.register(CourseHeadlines)
class CourseHeadlinesAdmin(admin.ModelAdmin):
    list_display = ['headline_title', 'course', 'chapter_number']
    inlines = [SeasonVideosInline]
    list_filter = ['course']
    search_fields = ['headline_title', 'course__title']