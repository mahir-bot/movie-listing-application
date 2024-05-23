from django.contrib import admin

from .models import Cast, Category, FavoriteMovies, Movie

# Register your models here.

admin.site.register(Movie)
admin.site.register(Cast)
admin.site.register(FavoriteMovies)
admin.site.register(Category)
