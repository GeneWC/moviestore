from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    movie_title = models.CharField(max_length=255, help_text="Title of the movie you want added")
    movie_year = models.IntegerField(null=True, blank=True, help_text="Year the movie was released (optional)")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_petitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Petition for {self.movie_title} by {self.creator.username}"

    def get_vote_count(self):
        return self.votes.count()

    def has_user_voted(self, user):
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()

class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'user')  # Prevent duplicate votes

    def __str__(self):
        return f"{self.user.username} voted for petition {self.petition.id}"

def __str__(self):
    return str(self.id) + ' - ' + self.name