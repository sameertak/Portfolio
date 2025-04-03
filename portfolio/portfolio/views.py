from django.http import FileResponse
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import JsonResponse
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from .langchain_helper import get_response_from_langchain
import os
import json
import time
from .settings import EMAIL_HOST_USER

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        history = data.get('history')
        time_remaining = data.get('time_remaining')
        article_id = data.get('currentPage').split('/')
        if len(article_id) > 2:
            article_id = article_id[-2]
        print(article_id)
        # Use the Langchain helper to get a response from the resume PDF
        response = get_response_from_langchain(user_message, history, time_remaining, article_id)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def download_resume(request):
    file_path = os.path.join(settings.BASE_DIR, 'static/resume', 'Samir_Tak-Resume.pdf')  # Adjust the path to your CV
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Samir_Tak-Resume.pdf"'
    return response

def send_confirmation_email(name, email, subject, message):
    # This will run in the background
    send_mail(
        f"Confirmation: {subject}",
        f"Hi {name},\n\nThank you for your message! We will get back to you shortly.\n\nYour message:\n{message}",
        f'{EMAIL_HOST_USER}',  # Replace with your email
        [email],  # Sender's email
        fail_silently=False,
    )

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email to yourself
        send_mail(
            subject,
            f"Message from {name} <{email}>\n\n{message}",
            f'{EMAIL_HOST_USER}',  # Replace with your email
            [f'{EMAIL_HOST_USER}'],  # Add your email here
            fail_silently=False,
        )

        # Return a JSON response immediately after the first email
        response = JsonResponse({'status': 'success'})

        # Send confirmation email in the background
        thread = Thread(target=send_confirmation_email, args=(name, email, subject, message))
        thread.start()

        return response

    return JsonResponse({'status': 'fail'})
