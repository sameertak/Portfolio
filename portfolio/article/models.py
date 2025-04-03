from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='articles/images/')
    markdown_file = models.FileField(upload_to='articles/md/')
    youtube_link = models.URLField(blank=True, null=True)  # Optional YouTube URL
    github_link = models.URLField(blank=True, null=True)   # Optional GitHub URL

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    client_id = models.CharField(max_length=36, blank=True, null=True)  # To identify the author on this client

    def __str__(self):
        return f'Comment on {self.article.title} by Anonymous'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    client_id = models.CharField(max_length=36)

    class Meta:
        unique_together = ('comment', 'client_id')  # ensure one like per client per comment


class ArticleLike(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    client_id = models.CharField(max_length=36)

    class Meta:
        unique_together = ('article', 'client_id')

class ChatQuery(models.Model):
    question = models.TextField()
    response = models.TextField()