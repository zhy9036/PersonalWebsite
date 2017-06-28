from django.shortcuts import render
from django.http import JsonResponse
from .models import UserLoginInfo
# Create your views here.
def index(request):
    return render(request, 'home/index.html')

def login(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': UserLoginInfo.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)
