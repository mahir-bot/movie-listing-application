from django.test import TestCase
from . models import Movie, Cast, User, FavoriteMovies
# Create your tests here.

class MovieTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(title="Test Movie", category="Test Category", release_date="2022-01-01", budget=100000)
        self.cast = Cast.objects.create(name="Test Cast", movie=self.movie)

    def test_movie_creation(self):
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.category, "Test Category")
        self.assertEqual(self.movie.release_date, "2022-01-01")
        self.assertEqual(self.movie.budget, 100000)

    def test_cast_creation(self):
        self.assertEqual(self.cast.name, "Test Cast")
        self.assertEqual(self.cast.movie, self.movie)

    def test_movie(self):
        self.assertEqual(str(self.movie), "Test Movie")

    def test_cast(self):
        self.assertEqual(str(self.cast), "Test Cast")

    def test_user(self):
        user = User.objects.create(username="testuser", first_name="Test", last_name="User", email="p3KZK@example.com", password="testpassword")
        self.assertEqual(str(user), "testuser")

    def test_favorite_movies(self):
        user = User.objects.create(username="testuser", first_name="Test", last_name="User", email="p3KZK@example.com", password="testpassword")
        movie = Movie.objects.create(title="Test Movie", category="Test Category", release_date="2022-01-01", budget=100000)
        favorite_movie = FavoriteMovies.objects.create(user=user, movie=movie)
        self.assertEqual(str(favorite_movie), "testuser")
        
    


