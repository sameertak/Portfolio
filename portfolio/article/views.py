from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Comment, ArticleLike, CommentLike
from .forms import CommentForm
import markdown
from django.views.decorators.http import require_POST
import re

def article_list(request):
    articles = Article.objects.all().order_by('-id')  # latest first, for example
    paginator = Paginator(articles, 6)  # 6 articles per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # If AJAX request, render only the articles partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        articles_html = render_to_string('articles/_article_list.html', 
                                          {'articles': page_obj.object_list}, 
                                          request=request)
        return JsonResponse({
            'articles_html': articles_html,
            'has_next': page_obj.has_next()
        })
    
    # Initial page load
    return render(request, 'articles/article_list.html', {
        'articles': page_obj.object_list,
        'has_next': page_obj.has_next()
    })

def get_liked_comments(request):
    client_id = request.GET.get('client_id')
    if client_id:
        # Retrieve all comment IDs liked by this client
        liked_comment_ids = CommentLike.objects.filter(client_id=client_id)\
                                .values_list('comment_id', flat=True)
        liked_comment_ids = list(liked_comment_ids)
        return JsonResponse({'liked_comments': liked_comment_ids})
    return JsonResponse({'liked_comments': []})

def extract_youtube_video_id(url):
    # This regex should match common YouTube URL formats, such as:
    # https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    md_content = article.markdown_file.read().decode('utf-8')
    html_content = markdown.markdown(md_content, extensions=['extra'])
    comments = article.comments.filter(parent__isnull=True).order_by('-created_at')
    comment_form = CommentForm()
    
    youtube_video_id = None
    if article.youtube_link:
        youtube_video_id = extract_youtube_video_id(article.youtube_link)
    
    context = {
        'article': article,
        'html_content': html_content,
        'comments': comments,
        'comment_form': comment_form,
        'youtube_video_id': youtube_video_id,
    }
    return render(request, 'articles/article_detail.html', context)

def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.client_id = request.POST.get('client_id')  # provided from the client side
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.filter(id=parent_id).first()
            comment.save()
    return redirect('article_detail', pk=article.pk)

from django.http import JsonResponse


def toggle_like_comment(request, comment_id):
    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Client id required'}, status=400)
    comment = get_object_or_404(Comment, id=comment_id)
    like_qs = CommentLike.objects.filter(comment=comment, client_id=client_id)
    if like_qs.exists():
        # Unlike: remove the like
        like_qs.delete()
        liked = False
    else:
        # Like: create the like record
        CommentLike.objects.create(comment=comment, client_id=client_id)
        liked = True
    # Count likes from the database
    like_count = CommentLike.objects.filter(comment=comment).count()
    return JsonResponse({'likes': like_count, 'liked': liked})


@require_POST
def delete_comment(request, comment_id):
    client_id = request.POST.get('client_id')
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.client_id != client_id:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    comment.delete()
    return JsonResponse({'success': True})

def toggle_article_like(request, article_id):
    client_id = request.GET.get('client_id')
    article = get_object_or_404(Article, id=article_id)
    liked = False
    # Check if the article is already liked by this client
    like_obj = ArticleLike.objects.filter(article=article, client_id=client_id).first()
    if like_obj:
        like_obj.delete()
    else:
        ArticleLike.objects.create(article=article, client_id=client_id)
        liked = True
    count = article.likes.count()
    return JsonResponse({'liked': liked, 'likes': count})

def get_article_like_status(request, article_id):
    client_id = request.GET.get('client_id')
    article = get_object_or_404(Article, id=article_id)
    liked = False
    if client_id:
        liked = ArticleLike.objects.filter(article=article, client_id=client_id).exists()
    count = article.likes.count()
    return JsonResponse({'liked': liked, 'likes': count})
