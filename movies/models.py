from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Cast(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    release_date = models.DateField(blank=False, null=False)
    budget = models.IntegerField(blank=False, null=False)
    slug = models.SlugField(unique=True, blank=True)
    thumbnail = models.ImageField(default='default.png', blank=True)
    casts = models.ManyToManyField(Cast, blank=True)
    category = models.ManyToManyField(Category, blank=True)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Movie.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug


class User(AbstractUser):

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(
        max_length=100, unique=True, null=False, blank=False)
    password = models.CharField(max_length=100, null=False, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class FavoriteMovies(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.movie.slug
