# common/utils/plots_tipos/base_kpi.py
from django.db.models import Max
from django.template.loader import render_to_string

class BaseKPIStrategy:
    def __init__(self, mapeamento, filtros, plotter):
        self.mapeamento = mapeamento
        self.filtros = filtros or {}
        self.plotter = plotter

    def get_common_data(self):
            m = self.mapeamento
            campo_periodo = m.get("mostrar_periodo")
            
            # 1. PEÇA AO DISPATCHER O TRABALHO SUJO (Tradução de filtros e Q objects)
            queryset, _, _ = self.plotter._get_base_queryset(
                m['__tipo_entidade__'], 
                self.filtros
            )
    
            # 2. Se for para filtrar o último ano, fazemos sobre o queryset JÁ FILTRADO
            if m.get("filtrar_ultimo_ano") and campo_periodo:
                res_max = queryset.aggregate(m=Max(campo_periodo))
                ultimo_valor = res_max['m']
                if ultimo_valor:
                    queryset = queryset.filter(**{campo_periodo: ultimo_valor})
            
            # Retornamos o QuerySet pronto. Não precisamos mais passar 'filtros' separadamente.
            return queryset, campo_periodo

    def get_base_context(self, valor, periodo=None):
        m = self.mapeamento
        rotulo = f"{m.get('titulo_base')} ({periodo})" if periodo else m.get('titulo_base')
        return {
            "valor": valor,
            "rotulo": rotulo,
            "icone": m.get("icone", "fas fa-chart-bar"),
            "cor": m.get("cor", "#4169E1"),
        }

    def render(self):
        context = self.get_kpi_data()
        return render_to_string("common/partials/_card_kpi.html", context)