# common/utils/plots_tipos/ranking_kpi.py
import pandas as pd
from .base_kpi import BaseKPIStrategy
from django.template.loader import render_to_string

class RankingKPIStrategy(BaseKPIStrategy):
    def get_kpi_data(self):
        # 1. Agora recebemos o queryset pronto e filtrado (América Latina + Último Ano)
        queryset, campo_periodo = self.get_common_data()
        
        # 2. Busca o primeiro registro do resultado filtrado
        entrada = queryset.first()
        
        if not entrada:
            return self.get_base_context("N/A")

        # 3. Lógica de Rankings (3-3 vira 3º)
        p_min, p_max = entrada.posicao_minima, entrada.posicao_maxima
        valor_final = f"{p_min}º" if p_min == p_max else f"{p_min}º - {p_max}º"
        
        # 4. Busca o ano do campo definido (ex: 'ano')
        ano = getattr(entrada, campo_periodo, None) if campo_periodo else None
        
        return self.get_base_context(valor_final, ano)

    def generate_plot(self, **kwargs):
        context = self.get_kpi_data()
        return render_to_string("common/partials/_card_kpi.html", context)