from django.shortcuts import render

def index(request):
    return render(request, "api_test2/index.html")
