from django.db import models
from django.db.models import Count
from django.db.models.functions import Lower
from django.shortcuts import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class PostView(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username



class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=220)
    reply = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_comment = models.BooleanField(default=True)

    def approve(self):
        self.approved_comment = True
        self.save()


    def __str__(self):
        return 'Comment By {} on {}'.format(str(self.user.username), self.post.title)

    class Meta:
        ordering = ['-timestamp']

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    # def comment_count(self):
    #     return self.comments.filter()

class PublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status="published")


class Category(models.Model):
    category_name   = models.CharField(max_length=20)
    timestamp       = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category_name


class Post(models.Model):

    objects             = models.Manager()  # The default manager.
    published           = PublishedManager()  # The custom manger for Published Posts

    STATUS_CHOICES = (
        ('draft', 'DRAFT'),
        ('published', 'PUBLISHED')
    )

    title               = models.CharField(max_length=100)
    slug                = models.SlugField(max_length=120, unique=True)
    author              = models.ForeignKey(User, related_name="blog_posts", on_delete=models.CASCADE)
    content             = RichTextUploadingField()
    overview            = models.TextField()
    likes               = models.ManyToManyField(User, related_name='likes', blank=True)
    created             = models.DateTimeField(default=timezone.now)
    updated             = models.DateTimeField(auto_now=True)
    category            = models.ManyToManyField(Category, related_name="categories")
    thumbnail           = models.ImageField(default='blog-default.jpg', upload_to='post_images/', blank=True)
    status              = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    favourite           = models.ManyToManyField(User, related_name='favourite', blank=True)
    restrict_comments   = models.BooleanField(default=False)
    featured            = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    def get_category_count():
        queryset = Post.objects.filter(category__isnull=False).values('category__category_name').annotate(Count('category__category_name'))
        return queryset

    def categories(self):
        return ", ".join([str(cat) for cat in self.category.all()])

    @property
    def view_count(self):
        return Comment.objects.filter(post=self).count()
    
    @property
    def comment_count(self):
        return PostView.objects.filter(post=self).count()

    class Meta:
        ordering = ['-created'] 



# Add slug field on create post
@receiver(pre_save, sender=Post)
def pre_save_slug(sender, **kwargs):
    # check slug
    if not kwargs['instance'].slug:
        kwargs['instance'].slug = get_unique_slug(kwargs['instance'])
        print(kwargs['instance'].slug)


# check slug is unique, if not add '-num' in slug
def get_unique_slug(self):
    slug = slugify(self.title)
    unique_slug = slug
    num = 1
    while Post.objects.filter(slug=unique_slug).exists():
        unique_slug = '{}-{}'.format(slug, num)
        num += 1
    return unique_slug


class Image(models.Model):
    post =  models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    def __str__(self):
        return str(self.post.id)



