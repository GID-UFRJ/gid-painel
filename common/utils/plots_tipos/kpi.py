import pandas as pd
from django.db.models import Count, Sum, Avg
from django.template.loader import render_to_string
from .base import BasePlotStrategy
from common.utils.plot_helpers import formatar_magnitude, formatar_percentual

class KPIStrategy(BasePlotStrategy):
    """
    Estratégia para renderização de Cards de KPI (Indicadores-Chave).
    Calcula um valor único baseado em agregações do Django ORM e 
    retorna o HTML formatado de um card.
    """

    def get_dataframe(self) -> pd.DataFrame:
        """
        Retorna o dado em formato DataFrame. 
        Útil para manter compatibilidade com exportações (CSV/Excel).
        """
        data = self.get_kpi_data()
        return pd.DataFrame([data])

    def get_kpi_data(self) -> dict:
        """
        Executa a query no banco de dados, aplica os filtros 
        dinâmicos e prepara o dicionário de dados do card.
        """
        # Obtém o queryset base já filtrado pelo motor do BasePlots
        queryset, mapeamento, _ = self.plotter._get_base_queryset(
            self.mapeamento['__tipo_entidade__'], 
            self.filtros
        )

        # Extrai definições do mapeamento
        campo_y = mapeamento.get("eixo_y_campo", "id")
        agregacao_raw = mapeamento.get("eixo_y_agregacao", "count").lower()
        
        # Identifica se a contagem deve ser distinta (ex: count_distinct)
        distinct = 'distinct' in agregacao_raw
        # Pega o prefixo da agregação (count, sum, avg)
        metodo_agregacao = agregacao_raw.split('_')[0]

        # Mapeia para funções do Django ORM
        agg_functions = {
            "count": Count(campo_y, distinct=distinct),
            "sum": Sum(campo_y),
            "avg": Avg(campo_y)
        }
        
        # Executa a agregação no banco de dados
        func = agg_functions.get(metodo_agregacao, Count(campo_y))
        resultado = queryset.aggregate(total=func)
        valor_bruto = resultado['total'] or 0

        # Formatação baseada no mapeamento usando os helpers
        formato = mapeamento.get("formatacao")
        if formato == "magnitude":
            valor_exibicao = formatar_magnitude(valor_bruto)
        elif formato == "percentual":
            valor_exibicao = formatar_percentual(valor_bruto)
        else:
            valor_exibicao = str(valor_bruto)

        return {
            "valor": valor_exibicao,
            "rotulo": mapeamento.get("titulo_base", "Indicador"),
            "icone": mapeamento.get("icone", "fas fa-chart-bar"),
            "cor": mapeamento.get("cor", "#4169E1"),
            "sufixo": mapeamento.get("sufixo", ""),
        }

    def generate_plot(self, df: pd.DataFrame = None, **kwargs) -> str:
        """
        Transforma os dados obtidos em HTML final.
        Sobrescreve o comportamento padrão de gerar gráficos Plotly.
        """
        context = self.get_kpi_data()
        
        # Renderiza o partial HTML que utiliza Bootstrap 5
        return render_to_string("common/partials/_card_kpi.html", context)