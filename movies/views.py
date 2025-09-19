from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, Vote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
    {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
    {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
        {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

def petitions(request):
    petitions = Petition.objects.all().order_by('-created_at')
    # Add user vote status to each petition
    for petition in petitions:
        petition.user_has_voted = petition.has_user_voted(request.user)

    template_data = {}
    template_data['title'] = 'Movie Petitions'
    template_data['petitions'] = petitions
    return render(request, 'movies/petitions.html', {'template_data': template_data})

@login_required
def create_petition(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        movie_title = request.POST.get('movie_title', '').strip()
        movie_year = request.POST.get('movie_year', '').strip()

        if title and description and movie_title:
            petition = Petition()
            petition.title = title
            petition.description = description
            petition.movie_title = movie_title
            petition.creator = request.user
            if movie_year:
                try:
                    petition.movie_year = int(movie_year)
                except ValueError:
                    pass  # Keep as None if invalid year
            petition.save()
            messages.success(request, 'Petition created successfully!')
            return redirect('movies.petitions')
        else:
            messages.error(request, 'Please fill in all required fields.')

    template_data = {}
    template_data['title'] = 'Create Petition'
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

@login_required
def vote_petition(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)

    if request.method == 'POST':
        # Check if user already voted
        if petition.has_user_voted(request.user):
            messages.warning(request, 'You have already voted on this petition.')
        else:
            vote = Vote()
            vote.petition = petition
            vote.user = request.user
            vote.save()
            messages.success(request, f'Your vote for "{petition.movie_title}" has been recorded!')

    return redirect('movies.petitions')
