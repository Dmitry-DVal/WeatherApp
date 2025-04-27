from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. This is weathersite mainpage.")

def search_weather(request):
    return HttpResponse("Here you will find locations and up-to-date weather.")