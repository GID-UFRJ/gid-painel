# common/utils/plots_tipos/topn.py

import pandas as pd
from django.db.models import Count, Sum
from .base_plot import BasePlotStrategy

class TopNStrategy(BasePlotStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA GRÁFICOS DO TIPO "TOP N"

    Sabe como fazer queries que ordenam por um valor agregado e pegam os N
    primeiros resultados para exibição em um gráfico de barras.
    """

    def get_dataframe(self) -> pd.DataFrame:
        """
        Busca e prepara os dados para um gráfico Top N.
        """
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        # Extrai as configurações de ranking da "receita" (mapeamento)
        try:
            campo_categoria = self.mapeamento["ranking_campo_categoria"]
            campo_valor = self.mapeamento.get("ranking_campo_valor", "id")
            agregacao_str = self.mapeamento.get("ranking_agregacao", "count")
            limite_padrao = self.mapeamento.get("ranking_limite_padrao", 10)
        except KeyError as e:
            raise KeyError(f"Mapeamento '{self.mapeamento['__tipo_entidade__']}' não possui a chave obrigatória para gráficos Top N: {e}")

        # Constrói a função de agregação
        distinct = 'distinct' in agregacao_str.lower()
        agregacao_base = agregacao_str.split('_')[0]
        agg_map = {"count": Count(campo_valor, distinct=distinct), "sum": Sum(campo_valor)}
        agg_func = agg_map.get(agregacao_base)

        # Pega o limite do filtro da URL, ou usa o padrão
        limite = int(self.filtros.get('limite', limite_padrao))

        # Executa a query, ordenando e limitando os resultados
        dados = queryset.values(campo_categoria).annotate(total=agg_func).order_by('-total')[:limite]
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()
        
        # Para gráficos de ranking, a ordem importa. Invertemos para que o maior fique no topo do gráfico.
        df = df.iloc[::-1]

        eixo_x_nome = self.mapeamento.get("eixo_x_nome", "Total")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", campo_categoria)

        df.rename(columns={
                    "total": eixo_x_nome,
                    campo_categoria: eixo_y_nome
                }, inplace=True)

        return df

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        """
        Gera o HTML do gráfico Top N.
        """
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"


        # Resgata os nomes já definidos
        eixo_x_nome = self.mapeamento.get("eixo_x_nome", "Total")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", self.mapeamento["ranking_campo_categoria"])

        # Prepara os parâmetros para um gráfico de barras horizontal, ideal para Top N
        params = {
            "x": eixo_x_nome,
            "y": eixo_y_nome,
            "orientation": 'h', # Gráfico "deitado"
            "title": kwargs.get('titulo_override') or self.mapeamento.get("titulo_base", ""),
            "text": eixo_x_nome, # Exibe os valores nas barras
        }

        # Delega a renderização final para o método auxiliar do "artesão" (BasePlots)
        return self.plotter._gerar_grafico(df, tipo_grafico, params, **kwargs)