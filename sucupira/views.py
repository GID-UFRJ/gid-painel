from django.shortcuts import render
from django.shortcuts import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'sucupira/index.html')

def posgrad_ufrj(request):
    return HttpResponse('Página em construção')

def ppgs(request):
    return HttpResponse('Página em construção')