from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return render(request, r'homepage/index.html')

def creditos(request):
    return render(request, r'homepage/creditos.html')