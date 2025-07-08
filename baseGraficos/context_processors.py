from . import models

def menu_items(request):
    return {
        'menu_items': models.Painel.objects.all()
    }