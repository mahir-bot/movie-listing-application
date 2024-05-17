from django.urls import path
from . import views

urlpatterns = [

    # Home and Search
    path('', views.home_page, name='home'),
    path('search/', views.search_movies, name='search_movies'),

    # Movie-Related Operations
    path('movies/create/', views.create_movie, name='create_movie'),
    path('movies/<slug:movie_slug>/', views.movie_details, name='movie_detail'),
    path('movies/<slug:movie_slug>/update/',
         views.update_movie, name='movie_update'),
    path('movies/<slug:movie_slug>/delete/',
         views.delete_movie, name='movie_delete'),

    # Favorites Management
    path("add-favorite/<slug:movie_slug>/",
         views.add_favorite_movie, name="add_favorite_movie"),
    path('favorite-movies/', views.favorite_movies, name='favorite_movies'),
    path('search-favorites/', views.search_favorite_movies, name='search_favorites'),
    path('delete-favorite/<slug:movie_slug>/',
         views.delete_favorite_movie, name='delete_favorite_movie'),

    # Additional Cast Operations
    path('add-cast/', views.add_cast, name='add_cast'),
    path('add-category/', views.add_category, name='add_category'),
]
