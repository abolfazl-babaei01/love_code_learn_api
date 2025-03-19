from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from django.db.models import Sum


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=155)
    slug = models.SlugField(max_length=155, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Course(models.Model):
    """
    Course model.
    for creating new course.
    """

    class CourseStatus(models.TextChoices):
        """
        choices a status of the course
        """
        completed = ('completed', 'Completed')
        in_progress = ('in_progress', 'In Progress')

    class CourseReleaseStatus(models.TextChoices):
        """
        choices a Course release status
        """
        published = ('published', 'Published')
        draft = ('draft', 'Draft')
        rejected = ('rejected', 'Rejected')

    # Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')

    # image
    thumbnail = models.ImageField(upload_to="courses/images/thumbnail/")
    # title
    title = models.CharField(max_length=100)
    # description
    description = models.TextField()
    # teacher
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    # slug
    slug = models.SlugField(max_length=100, unique=True)
    # rate
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])

    number_of_students = models.PositiveIntegerField(default=0)

    # prices
    price = models.PositiveBigIntegerField(default=0)
    off = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    final_price = models.PositiveBigIntegerField(default=0)
    # sum course time
    duration = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    status = models.CharField(max_length=11, choices=CourseStatus.choices, default=CourseStatus.in_progress)
    release_status = models.CharField(max_length=10, choices=CourseReleaseStatus.choices,
                                      default=CourseReleaseStatus.draft)
    is_free = models.BooleanField(default=False)
    # date time
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.teacher}'

    def save(self, *args, **kwargs):

        if self.off == 0:
            self.final_price = self.price

        if self.final_price == 0:
            self.is_free = True
        else:
            self.is_free = False
        self.final_price = self.price - self.off

        super().save(*args, **kwargs)

    def update_duration(self):
        """
        Updates the total duration of the course based on its videos.
        """
        total_duration = SeasonVideos.objects.filter(headline__course=self).aggregate(
            total_duration=Sum('duration')
        )['total_duration'] or 0
        self.duration = total_duration
        self.save()


class CourseSubDescription(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sub_descriptions')
    sub_title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="courses/images/sub_descriptions/", null=True, blank=True)
    sub_description = models.TextField()

    def __str__(self):
        return f'{self.course} - {self.sub_title}'


class CourseHeadlines(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='headlines')
    headline_title = models.CharField(max_length=200)
    chapter_number = models.PositiveIntegerField()
    duration = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.headline_title

    def update_duration(self):
        total_duration = SeasonVideos.objects.filter(headline=self).aggregate(
            total_duration=Sum('duration'))['total_duration'] or 0
        self.duration = total_duration
        self.save()

    class Meta:
        ordering = ['chapter_number']
        constraints = [
            models.UniqueConstraint(fields=['course', 'chapter_number'], name='unique_chapter_per_course')
        ]
        verbose_name = 'Headline'
        verbose_name_plural = 'Headlines'


def video_upload_path(instance, filename):
    path = instance.headline.headline_title.replace(' ', '_')
    return f"courses/videos/{path}/{filename}"


def attached_file_upload_path(instance, filename):
    path = instance.video_title.replace(' ', '_')
    return f"attached_files/{path}/{filename}"


class SeasonVideos(models.Model):
    headline = models.ForeignKey(CourseHeadlines, on_delete=models.CASCADE, related_name='videos')
    video_title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to=video_upload_path)
    description = models.TextField(null=True, blank=True)
    attached_file = models.FileField(upload_to=attached_file_upload_path, null=True, blank=True)
    duration = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    is_free = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Update the course duration when a new video is added or modified.
        """
        super().save(*args, **kwargs)
        self.headline.update_duration()
        self.headline.course.update_duration()

    def delete(self, *args, **kwargs):
        """
        Update the course duration when a video is deleted.
        """
        headline = self.headline
        course = headline.course
        headline.update_duration()
        course.update_duration()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.headline} - {self.video_title}'


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.phone_number} -> {self.course.title}"