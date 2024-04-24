from django.db import models

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    release_date = models.DateField()
    budget = models.IntegerField()
    
    def __str__(self):
        return self.title

class Cast(models.Model):
    name = models.CharField(max_length=100)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    

class User(models.Model):
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(max_length=100,unique=True,null=False,blank=False)
    password = models.CharField(max_length=100,null=False,blank=False)
    last_login = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.username
    
class FavoriteMovies(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


