from django.http import Http404
from django.contrib import messages
from movies.models import FavoriteMovies, Movie
from django.test import Client
from movies.models import Movie
from django.db.models import Q
from movies.models import Movie, Category, Cast
from django.core.files.uploadedfile import SimpleUploadedFile
from movies.models import Movie, FavoriteMovies
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import transaction
from django.test import TestCase, Client
from django.urls import reverse
from movies.models import Cast, Category, FavoriteMovies, Movie
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.paginator import Paginator
from movies.forms import MovieForm
from django.contrib.auth import get_user_model
User = get_user_model()


User = get_user_model()


class UserAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "testpass"
        }

    def test_user_registration_success(self):
        response = self.client.post(reverse("signup"), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("signin"))
        self.assertTrue(User.objects.filter(
            username="testuser").exists())

    def test_user_login_success(self):
        user = User.objects.create_user(**self.user_data)
        response = self.client.post(
            reverse("signin"), {
                "email": user.email, "password": "testpass"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_user_login_invalid_credentials(self):
        response = self.client.post(
            reverse("signin"), {
                "email": "wrong@example.com", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)

    def test_user_logout_success(self):
        user = User.objects.create_user(**self.user_data)
        self.client.login(username=user.email, password="testpass")

        response = self.client.get(reverse("signout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        self.movie1 = Movie.objects.create(
            title="Favorite Movie 1",
            release_date="2024-05-01",
            budget=5000000
        )

        self.movie2 = Movie.objects.create(
            title="Favorite Movie 2",
            release_date="2025-06-15",
            budget=6000000
        )

        FavoriteMovies.objects.create(user=self.user, movie=self.movie1)
        FavoriteMovies.objects.create(user=self.user, movie=self.movie2)

        self.client = Client()
        self.client.login(username='test@example.com', password='testpass')

    def test_user_profile(self):
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.movie1.title)
        self.assertContains(response, self.movie2.title)
        favorite_movies = response.context['favorite_movies']
        self.assertEqual(favorite_movies.count(), 2,
                         "Expected 2 favorite movies.")


class HomePageTestCase(TestCase):
    def setUp(self):
        for i in range(45):
            Movie.objects.create(
                title=f"Movie {i}",
                release_date="2024-05-01",
                budget=10000000
            )

    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200,
                         "Home page should render successfully.")

    def test_pagination_first_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        page_movies = response.context["movies"]
        self.assertEqual(len(page_movies), 30,
                         "First page should contain 30 movies.")
        self.assertContains(response, "Movie 0")
        self.assertContains(response, "Movie 29")

    def test_pagination_second_page(self):
        response = self.client.get(reverse("home"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        page_movies = response.context["movies"]
        self.assertEqual(len(page_movies), 15,
                         "Second page should contain 15 movies.")

        movie_titles = [movie.title for movie in page_movies]
        self.assertNotIn("Movie 30", movie_titles,
                         "Expected 'Movie 30' on the second page")
        self.assertIn("Movie 44", movie_titles)

    def test_no_movies(self):
        Movie.objects.all().delete()
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200,
                         "Home page should render without errors even if no movies.")

        page_movies = response.context["movies"]
        self.assertEqual(len(page_movies), 0, "No movies should be displayed.")


class SearchMoviesTestCase(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Action")
        self.category2 = Category.objects.create(name="Drama")
        self.cast1 = Cast.objects.create(name="Actor One")
        self.cast2 = Cast.objects.create(name="Actor Two")

        self.movie1 = Movie.objects.create(
            title="Action Story", release_date="2024-05-01", budget=50000000)
        self.movie2 = Movie.objects.create(
            title="Dramatic Story", release_date="2024-06-01", budget=30000000)

        self.movie1.category.add(self.category1)
        self.movie2.category.add(self.category2)

        self.movie1.casts.add(self.cast1)
        self.movie2.casts.add(self.cast2)

    def test_search_with_valid_query(self):
        response = self.client.get(reverse("search_movies"), {"q": "Action"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Action Story")

    def test_search_by_category(self):
        response = self.client.get(reverse("search_movies"), {"q": "Drama"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dramatic Story")

    def test_search_by_cast(self):
        response = self.client.get(
            reverse("search_movies"), {"q": "Actor One"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Actor One")

    def test_no_query_redirects_to_home(self):
        response = self.client.get(reverse("search_movies"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_empty_search_results(self):
        response = self.client.get(reverse("search_movies"), {
                                   "q": "Nonexistent Movie"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Action Story")
        self.assertNotContains(response, "Dramatic Story")
        self.assertNotContains(response, "Actor One")
        self.assertNotContains(response, "Actor Two")


class CreateMovieTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com', password='testpass')
        self.client.login(username='test@example.com', password='testpass')

        self.category1 = Category.objects.create(name='Action')
        self.category2 = Category.objects.create(name='Drama')
        self.cast1 = Cast.objects.create(name='Actor One')
        self.cast2 = Cast.objects.create(name='Actor Two')

    def test_create_movie_valid(self):
        valid_data = {
            'title': 'Test Movie',
            'release_date': '2024-04-26',
            'budget': 50000000,
            'category': [self.category1.id, self.category2.id],
            'casts': [self.cast1.id, self.cast2.id],
            'poster': SimpleUploadedFile('test_poster.jpg', b'file_content', content_type='image/jpeg')
        }

        response = self.client.post(
            reverse('create_movie'),
            data=valid_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        movie = Movie.objects.filter(title='Test Movie').first()
        self.assertIsNotNone(movie, "Movie should be created with valid data.")

        self.assertEqual(set(movie.category.all()), {
                         self.category1, self.category2})
        self.assertEqual(set(movie.casts.all()), {self.cast1, self.cast2})

    def test_create_movie_invalid(self):
        invalid_data = {
            'title': '',
            'release_date': '2024-04-26',
            'budget': 50000000,
            'category': [self.category1.id, self.category2.id],
            'casts': [self.cast1.id, self.cast2.id]
        }

        response = self.client.post(
            reverse('create_movie'),
            data=invalid_data,
            follow=True
        )
        form = response.context.get('form', None)
        # if form and not form.is_valid():
        #     print("Form Errors:", form.errors)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_create_movie_get(self):
        response = self.client.get(reverse('create_movie'))

        self.assertEqual(response.status_code, 200)

        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'movies/create_movie.html')


class MovieDetailsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com', password='testpass')
        self.movie = Movie.objects.create(
            title='Test Movie',
            release_date='2024-04-26',
            budget=50000000
        )
        FavoriteMovies.objects.create(user=self.user, movie=self.movie)

    def test_movie_details_authenticated(self):
        self.client.login(username='test@example.com', password='testpass')

        response = self.client.get(
            reverse('movie_detail', args=[self.movie.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('movie', response.context)
        self.assertEqual(response.context['movie'], self.movie)
        self.assertTrue(response.context['is_favorite'])

    def test_movie_details_unauthenticated(self):
        response = self.client.get(
            reverse('movie_detail', args=[self.movie.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('movie', response.context)
        self.assertEqual(response.context['movie'], self.movie)
        self.assertFalse(response.context['is_favorite'])


class DeleteMovieTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_date="2024-04-26",
            budget=666999969,
        )

    def test_delete_movie(self):
        response = self.client.post(
            reverse("movie_delete", args=[self.movie.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Movie.objects.filter(slug="test-movie").exists())


class FavoriteMoviesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass')
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_date="2024-04-26",
            budget=666999969,
        )
        self.category = Category.objects.create(name="Test Category")
        self.cast = Cast.objects.create(name="Test Cast")
        self.movie.category.add(self.category)
        self.movie.casts.add(self.cast)
        self.client.login(username='testuser@example.com', password='testpass')

    def test_favorite_movies_view(self):
        FavoriteMovies.objects.create(user=self.user, movie=self.movie)
        response = self.client.get(reverse('favorite_movies'))
        # 302 might indicate a redirect
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/favorite_movies.html')

    def test_add_favorite_movie(self):
        response = self.client.post(
            reverse('add_favorite_movie', args=[self.movie.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'movie_detail', args=[self.movie.slug]))
        self.assertTrue(FavoriteMovies.objects.filter(
            user=self.user, movie=self.movie).exists())

    def test_search_favorite_movies(self):
        FavoriteMovies.objects.create(user=self.user, movie=self.movie)
        response = self.client.get(
            reverse('search_favorites'), {'q': 'Test Movie'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movies/search_favorites.html')

    def test_delete_favorite_movie(self):
        FavoriteMovies.objects.create(user=self.user, movie=self.movie)
        response = self.client.post(
            reverse('delete_favorite_movie', args=[self.movie.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'movie_detail', args=[self.movie.slug]))
        self.assertFalse(FavoriteMovies.objects.filter(
            user=self.user, movie=self.movie).exists())


class CastViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cast = Cast.objects.create(name="Test Cast")

    def test_cast_view(self):
        response = self.client.post(
            reverse('add_cast'), {'name': 'Test Cast 2'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Cast.objects.count(), 2)
        self.assertEquals(Cast.objects.last().name, 'Test Cast 2')
        self.assertRedirects(response, reverse('create_movie'))

    def test_cast_view_empty(self):
        response = self.client.post(reverse('add_cast'), {'name': ''})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Cast.objects.count(), 1)
        self.assertTemplateUsed(response, 'movies/add_cast.html')


class CategoryViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")

    def test_category_view(self):
        response = self.client.post(reverse('add_category'), {
                                    'name': 'Test Category 2'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Category.objects.count(), 2)
        self.assertEquals(Category.objects.last().name, 'Test Category 2')
        self.assertRedirects(response, reverse('create_movie'))

    def test_category_view_empty(self):
        response = self.client.post(reverse('add_category'), {'name': ''})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Category.objects.count(), 1)
        self.assertTemplateUsed(response, 'movies/add_category.html')
