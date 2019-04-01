from django.contrib import admin
from .models import Post, Image, Comment, Category, PostView
# from ckeditor.widgets import CKEditorWidget


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'status', 'categories') # display on post all
    list_filter = ('status', 'created', 'updated', 'status', 'category') # filters for post
    search_fields = ('title', 'author__username')   # search by
    prepopulated_fields = {'slug':('title',)}   # populate field data
    list_editable = ('status',)
    date_hierarchy = ('created')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image')

admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(PostView)