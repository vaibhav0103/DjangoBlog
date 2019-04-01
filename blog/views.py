from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q, Count
from .models import Post, Image, Comment, PostView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostCreateForm
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.contrib.messages.views import SuccessMessageMixin
from .forms import CommentForm


def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.published.order_by('-created')[0:3]

    # if request.method == "POST":
    #     email = request.POST["email"]
    #     new_signup = Signup()
    #     new_signup.email = email
    #     new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'blog/index.html', context)

class PostListView(ListView):
    # model = Post
    # queryset = Post.published.all()  # Post.objects.filter(status="published")
    # query = self.request.GET.get('q')
    context_object_name = 'posts'
    # template_name = 'blog/post_list.html'
    template_name = 'blog/blog.html'
    # ordering = ['-created']
    paginate_by = 4

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            queryset = Post.published.filter(
                Q(title__icontains=query)|
                Q(author__username=query)|
                Q(content__icontains=query)
            )
        else:
            queryset = Post.published.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_posts'] = Post.objects.annotate(likes_count=Count('likes')).filter(likes_count__gt=0)
        context['most_recent'] = Post.published.order_by('-created')[:3]
        context['category_count'] = Post.get_category_count()
        print(context['category_count'])
        return context


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_liked'] = False
        context['is_favourite'] = False
        context['form'] = CommentForm()
        user = self.request.user
        slug = self.kwargs.get("slug")
        post = get_object_or_404(Post, slug=slug)
        # Post View for view count
        print(user)
        if user.is_authenticated:
            PostView.objects.get_or_create(user=user, post=post)

        context['most_recent'] = Post.published.order_by('-created')[:3]
        context['category_count'] = Post.get_category_count()
        comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
        context['comments'] = comments
        context['total_likes'] = post.total_likes()
        if user in post.favourite.all():
            context['is_favourite'] = True
        if user in post.likes.all():
            context['is_liked'] = True
        return context


def favourite_post_list(request):
    user = request.user
    favourite_posts = user.favourite.all()
    context = {
        'favourite_posts': favourite_posts,
    }
    return render(request, 'blog/favourite_post_list.html', context)


def favourite_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
        is_favourite = False
    else:
        post.favourite.add(request.user)
        is_favourite = True

    context = {
        'post': post,
        'is_favourite': is_favourite,
    }
    return HttpResponseRedirect(post.get_absolute_url())


def like_post(request):
    post = get_object_or_404(Post, id=int(request.POST.get('post_id')))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True

    context = {
        'post': post,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }

    if request.is_ajax():
        html = render_to_string('blog/like_section.html', context, request=request)
        return JsonResponse({'form':html})
    # return HttpResponseRedirect(post.get_absolute_url())


def popular_posts(request):
    popular_posts = Post.objects.annotate(likes_count=Count('likes')).filter(likes_count__gt=1)
    print(popular_posts)
    context = {
        'popular_posts': popular_posts,
    }

    return render(request, 'blog/popular_posts.html', context)


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  #default way: <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    # check if user is author
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.published.filter(author=user).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_posts'] = Post.objects.annotate(likes_count=Count('likes')).filter(likes_count__gt=0)
        return context


def post_create(request):
    ImageFormset = modelformset_factory(Image, fields=('image',), extra=4)
    if request.method == "POST":
        form = PostCreateForm(request.POST)
        formset = ImageFormset(request.POST or None, request.FILES or None)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            for f in formset:
                try:
                    img = Image(post=post, image=f.cleaned_data['image'])
                    img.save()
                except Exception as e:
                    break
            messages.success(request, f'Your Post has been created succesfully !')
            return redirect('post-detail', slug=post.slug)
    else:
        form = PostCreateForm()
        formset = ImageFormset(queryset=Image.objects.none())
    context = {
        'form': form,
        'formset': formset,
    }

    return render(request, 'blog/post_create.html', context)


class PostUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    # fields = ['title', 'body', 'content', 'status', 'restrict_comments',]
    success_message = "Post Updated Successfully!"
    # override to save author
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    success_message = "Post Deleted Successfully!"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            reply_id = request.POST.get('comment_id')
            print(reply_id)
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
                comment.reply = comment_qs
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, f'Your Comment has been added succesfully !')
            # return redirect('post-detail', slug=post.slug)
    else:
        form = CommentForm()
        # return render(request, 'post-detail', {'form': form})
        # print(form)
    if request.is_ajax():

        html = render_to_string('blog/comment_section.html', {'post':post, 'form':form, 'comments':comments, }, request)
        # return HttpResponse(html)
        return JsonResponse({'html': html})

    return render(request, 'post-detail', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    messages.success(request, f'Your Comment has been added succesfully !')
    return redirect('post-detail', slug=comment.post.slug)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    messages.error(request, f'Your Comment has been removed succesfully !')
    return redirect('post-detail', slug=comment.post.slug)