# common/utils/plots_tipos/kpi.py

import pandas as pd
from django.db import models 
from django.db.models import Count, Sum, Avg, Max
from django.template.loader import render_to_string
from .base_kpi import BaseKPIStrategy
from common.utils.plot_helpers import (
    formatar_magnitude, 
    formatar_decimal,
    formatar_percentual, 
    extrair_periodo
)

class KPIStrategy(BaseKPIStrategy):
    """
    Estratégia para renderização de Cards de KPI.
    Utiliza 'mostrar_periodo' como fonte para filtragem automática do último ano.
    """

    def get_dataframe(self) -> pd.DataFrame:
        data = self.get_kpi_data()
        return pd.DataFrame([data])

    def get_kpi_data(self) -> dict:
        mapeamento = self.mapeamento
        modelo = mapeamento["modelo"]
        campo_periodo = mapeamento.get("mostrar_periodo")
        
        # 1. Cópia dos filtros para manipulação dinâmica
        filtros_para_query = self.filtros.copy()

        # 2. Lógica Inteligente: Filtrar pelo Último Ano
        # Se filtrar_ultimo_ano for True, usamos o campo do mostrar_periodo
        if mapeamento.get("filtrar_ultimo_ano") is True and campo_periodo:
                # IMPORTANTE: Filtramos o modelo ANTES de pedir o Max(ano)
                # Isso garante que se o QS só tem 2023, o Max será 2023, mesmo que o THE tenha 2024
                res_max = modelo.objects.filter(**filtros_para_query).aggregate(m=models.Max(campo_periodo))
                ultimo_valor = res_max['m']

                if ultimo_valor:
                    filtros_para_query[campo_periodo] = ultimo_valor
                else:
                    # Se não achou nada com os filtros, o card retornaria vazio
                    return {"valor": 0, "periodo": "N/A"}        



        #if mapeamento.get("filtrar_ultimo_ano") is True and campo_periodo:
        #    # Só aplicamos se o usuário não estiver filtrando via UI/HTMX
        #    if not filtros_para_query:
        #        res_max = modelo.objects.aggregate(m=Max(campo_periodo))
        #        ultimo_valor = res_max['m']
        #        
        #        if ultimo_valor is not None:
        #            filtros_para_query[campo_periodo] = ultimo_valor

        # 3. Obtém o Queryset Base
        queryset, _, _ = self.plotter._get_base_queryset(
            mapeamento['__tipo_entidade__'], 
            filtros_para_query
        )

        # 4. Agregação do Valor Principal
        campo_y = mapeamento.get("eixo_y_campo", "id")
        agregacao_raw = mapeamento.get("eixo_y_agregacao", "count").lower()
        distinct = 'distinct' in agregacao_raw
        metodo_agregacao = agregacao_raw.split('_')[0]

        agg_dict = {
            "count": Count(campo_y, distinct=distinct),
            "sum": Sum(campo_y),
            "avg": Avg(campo_y)
        }
        
        func = agg_dict.get(metodo_agregacao, Count(campo_y))
        resultado = queryset.aggregate(total=func)
        valor_bruto = resultado['total'] or 0

        # 5. Formatação do Valor
        formato = mapeamento.get("formatacao")
        if formato == "magnitude":
            valor_exibicao = formatar_magnitude(valor_bruto)
        elif formato == "percentual":
            valor_exibicao = formatar_percentual(valor_bruto)
        elif formato == "decimal":
            # Aqui usamos a nova função para arredondar os meses
            valor_exibicao = formatar_decimal(valor_bruto, precisao=1)
        else:
            valor_exibicao = f"{valor_bruto:,}".replace(",", ".")

        # 6. Título com Período Dinâmico
        rotulo = mapeamento.get("titulo_base", "Indicador")
        if campo_periodo:
            periodo_str = extrair_periodo(queryset, campo_periodo)
            if periodo_str:
                rotulo = f"{rotulo} ({periodo_str})"

        return {
            "valor": valor_exibicao,
            "rotulo": rotulo,
            "icone": mapeamento.get("icone", "fas fa-chart-bar"),
            "cor": mapeamento.get("cor", "#4169E1"),
            "sufixo": mapeamento.get("sufixo", ""),
        }

    def generate_plot(self, df: pd.DataFrame = None, **kwargs) -> str:
        context = self.get_kpi_data()
        return render_to_string("common/partials/_card_kpi.html", context)