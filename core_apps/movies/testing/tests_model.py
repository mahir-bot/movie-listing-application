from datetime import date
from django.test import TestCase
from movies.models import Movie, Cast, Category, User


class MovieTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",  release_date=date(2024, 4, 26), budget=666999969)
        self.cast = Cast.objects.create(name="Test Cast", movie=self.movie)
        self.category = Category.objects.create(
            name="Test Category", movie=self.movie)
        self.movie.casts.add(self.cast)
        self.movie.category.add(self.category)

    def test_movie_creation(self):
        self.assertTrue(isinstance(self.movie, Movie))
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(str(self.movie.release_date), "2024-04-26")
        self.assertEqual(self.movie.budget, 666999969)
        self.assertEqual(self.movie.slug, "test-movie")

        self.assertIn(self.cast, self.movie.casts.all())
        self.assertIn(self.category, self.movie.category.all())

    def test_movie_slug(self):
        yet_another_movie = Movie.objects.create(
            title="Test Movie",
            release_date=date(2024, 4, 26),
            budget=123
        )
        self.assertEqual(yet_another_movie.slug, "test-movie-1")


class CastTestCase(TestCase):
    def setUp(self):
        self.cast = Cast.objects.create(name="Test Cast")

    def test_cast_creation(self):
        self.assertTrue(isinstance(self.cast, Cast))
        self.assertEqual(self.cast.name, "Test Cast")
        self.assertEqual(str(self.cast), "Test Cast")


class CategoryTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_category_creation(self):
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(str(self.category), "Test Category")


class FavoriteMoviesTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_date=date(2024, 4, 26),
            budget=666999969
        )
        self.cast = Cast.objects.create(name="Test Cast")
        self.category = Category.objects.create(name="Test Category")
        self.movie.casts.add(self.cast)
        self.movie.category.add(self.category)
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password"
        )

    def test_favorite_movies_creation(self):
        self.assertTrue(isinstance(self.movie, Movie))
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(str(self.movie.release_date), "2024-04-26")
        self.assertEqual(self.movie.budget, 666999969)
        self.assertEqual(self.movie.slug, "test-movie")

        self.assertIn(self.cast, self.movie.casts.all())
        self.assertIn(self.category, self.movie.category.all())

        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password"))

        self.assertEqual(str(self.user), "testuser")

        self.assertEqual(str(self.movie), "test-movie")


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password"
        )

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password"))
        self.assertEqual(str(self.user), "testuser")
