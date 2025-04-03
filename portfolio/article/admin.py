from django.contrib import admin
from .models import Article, Comment, CommentLike

# Register the model
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(CommentLike)


