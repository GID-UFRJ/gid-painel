# common/middleware/maintenance.py
from django.http import HttpResponse
from django.core.cache import cache
from django.template.loader import render_to_string

#DEPENDE DO REDIS
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Opcional: Permite acesso livre ao painel administrativo do Django
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Verifica no Redis se o modo de manutenção está ativado
        if cache.get('modo_manutencao', False):
            # Renderiza um template simples de 503
            try:
                html = render_to_string('manutencao.html', request=request)
            except Exception:
                html = "<h1>Sistema em atualização. Volte em alguns minutos.</h1>"
            
            return HttpResponse(html, status=503)

        return self.get_response(request)