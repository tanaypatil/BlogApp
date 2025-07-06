from autoslug import AutoSlugField
from django.contrib.auth.models import User, AbstractUser
from django.db import models

BLOG_CATEGORIES = [
    ("SPORTS", "SPORTS"), ("EDUCATION", "EDUCATION"), ("ENTERTAINMENT", "ENTERTAINMENT"),
    ("TECHNOLOGY", "TECHNOLOGY"), ("CURRENT AFFAIRS", "CURRENT AFFAIRS"), ("POLITICS", "POLITICS"),
    ("FINANCE", "FINANCE")
]


class BlogUser(AbstractUser):
    bio = models.TextField()
    profile_picture = models.ImageField(upload_to="images/profile_pictures")

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = "Blog User"
        verbose_name_plural = "Blog Users"


class Tag(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    slug = AutoSlugField(populate_from="title", blank=False, null=False, unique=True)
    body = models.TextField(blank=False, null=False)
    author = models.ForeignKey(BlogUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=False, null=False, choices=BLOG_CATEGORIES)
    tags = models.ManyToManyField(Tag)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        ordering = ['-created']


class Comment(models.Model):
    user = models.ForeignKey(BlogUser, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id}_{self.blog.id}_{self.id}"

    class Meta:
        ordering = ['created']
