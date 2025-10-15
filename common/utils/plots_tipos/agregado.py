# common/utils/plots_tipos/agregado.py

import pandas as pd
from django.db.models import Count, Sum, Avg
from .xy_base import XYBaseStrategy # Importa a classe base do mesmo pacote

class AggregatedPlotStrategy(XYBaseStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA PLOTS AGREGADOS (Barras, Linhas, etc.)

    Sabe como fazer queries com agregação (Count, Sum, Avg) e como preparar
    o DataFrame para visualizações baseadas em eixos X e Y.
    """

    def get_dataframe(self) -> pd.DataFrame:
        """
        Implementação para buscar e agregar dados.
        Esta é a lógica que extraímos da antiga `_get_dataframe_agregado`.
        """
        # Usa o método auxiliar do "artesão" (BasePlots) para obter o queryset inicial
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        # Extrai as configurações da "receita" (mapeamento)
        eixo_x_campo = self.mapeamento["eixo_x_campo"]
        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        eixo_y_campo = self.mapeamento.get("eixo_y_campo", "id")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", "Total")
        agregacao_str = self.mapeamento.get("eixo_y_agregacao", "count")

        # Constrói a função de agregação do Django
        distinct = 'distinct' in agregacao_str.lower()
        agregacao_base = agregacao_str.split('_')[0]
        agg_map = {"count": Count(eixo_y_campo, distinct=distinct), "sum": Sum(eixo_y_campo), "avg": Avg(eixo_y_campo)}
        agg_func = agg_map.get(agregacao_base.lower())
        if not agg_func:
            raise ValueError(f"Agregação '{agregacao_base}' não suportada.")

        # Lida com o agrupamento (série 'color' do Plotly)
        agrupamento = self.filtros.get("agrupamento")
        campo_grupo = self.mapeamento.get("agrupamentos", {}).get(agrupamento)
        
        valores_a_buscar = [eixo_x_campo]
        if campo_grupo:
            valores_a_buscar.append(campo_grupo)

        # Executa a query no banco de dados
        alias_coluna_y = self.plotter._formatar_alias_de_coluna(eixo_y_nome)
        dados = queryset.values(*valores_a_buscar).annotate(**{alias_coluna_y: agg_func}).order_by(eixo_x_campo)
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        # Renomeia as colunas para nomes amigáveis que serão usados no gráfico e no CSV
        df.rename(columns={eixo_x_campo: eixo_x_nome, alias_coluna_y: eixo_y_nome}, inplace=True)
        if campo_grupo:
            df.rename(columns={campo_grupo: agrupamento.replace('_', ' ').capitalize()}, inplace=True)

        return df