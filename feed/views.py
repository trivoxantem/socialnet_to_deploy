from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ProfileEditForm
from django.db.models import Q


def feed_view(request):
    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")
        comment_content = request.POST.get("comment_content")
        post_id = request.POST.get("post_id")

        if comment_content and post_id:
            post = Post.objects.get(id=post_id)
            Comment.objects.create(user=request.user, post=post, content=comment_content)
        elif content or image:
            Post.objects.create(user=request.user, content=content, image=image)

        return redirect("feeds")

    posts = Post.objects.all().order_by("-created_at")
    return render(request, "feed.html", {"posts": posts})


@login_required
@csrf_exempt
def add_comment_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        content = data.get("content")

        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(user=request.user, post=post, content=content)

        html = render_to_string("comment.html", {"comment": comment})
        return HttpResponse(html)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)  # Automatically log the user in
        return redirect('feeds')


    return render(request, 'signup.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('feeds')
        else:
            messages.error(request, "USERNAME or PASSWORD is not Valid")
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url='login')
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes()
        })
    

@login_required
def profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile = user_profile.profile
    posts = Post.objects.filter(user=user_profile).order_by('-created_at')
    is_following = False
    if profile.followers.filter(id=request.user.id).exists():
        is_following = True

    context = {
        'user_profile': user_profile,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'profile.html', context)

@login_required
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    profile = user_to_follow.profile

    if profile.followers.filter(id=request.user.id).exists():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)

    return redirect('profile', username=username)


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})



def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Post.objects.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        ).order_by('-created_at')
    return render(request, 'search_results.html', {'results': results, 'query': query})

