from django.shortcuts import render
from django.views import View

def handle(request):
    return render(request, 'JacksonWebApp/logs.html')