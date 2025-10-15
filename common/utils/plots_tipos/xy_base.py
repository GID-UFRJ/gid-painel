# common/utils/plots_tipos/xy_base.py

import pandas as pd
from abc import abstractmethod
from .base import BasePlotStrategy
from pandas.api.types import CategoricalDtype

class XYBaseStrategy(BasePlotStrategy):
    """
    CLASSE BASE INTERMEDIÁRIA PARA PLOTS DE EIXOS XY (Barras, Linhas, etc.)

    Contém a lógica de GERAÇÃO DE PLOT que é compartilhada por todos os gráficos
    que usam um eixo X e um eixo Y.

    Deixa o método get_dataframe() como abstrato, pois a forma de obter os dados
    é o que diferencia as estratégias filhas (agregada vs. direta).
    """
    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        """As classes filhas devem implementar sua própria forma de buscar dados."""
        raise NotImplementedError

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        """
        [VERSÃO FINAL E ROBUSTA]
        Pega o DataFrame e gera o HTML, passando a ordenação correta diretamente para o Plotly.
        """
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado.</p>"

        agrupamento = self.filtros.get("agrupamento")
        agrupamentos_validos = self.mapeamento.get("agrupamentos", {})
        grupo_plotly = None
        if agrupamento and agrupamento in agrupamentos_validos:
            grupo_plotly = agrupamento.replace('_', ' ').capitalize()

        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", "Total")

        # ==============================================================================
        # INÍCIO DA LÓGICA DE PREENCHIMENTO DE ANOS (RESTAURADA)
        # ==============================================================================
        # Se o eixo X for numérico e contínuo, preenchemos os valores vazios com zeros
        # para garantir a continuidade em gráficos de linha.
        if self.mapeamento.get("eixo_x_tipo") == 'numerico_continuo':
            try:
                # Determina o intervalo de anos a ser exibido
                inicio = int(self.filtros.get('ano_inicial', df[eixo_x_nome].min()))
                fim = int(self.filtros.get('ano_final', df[eixo_x_nome].max()))
                
                if grupo_plotly:
                    # Se o gráfico for agrupado (ex: por sexo), o processo é mais complexo:
                    # 1. Pivot: Transforma o DataFrame para ter anos como índice e grupos como colunas.
                    df_pivot = df.pivot_table(index=eixo_x_nome, columns=grupo_plotly, values=eixo_y_nome, fill_value=0)
                    # 2. Reindex: Garante que todas as linhas (anos) no intervalo existam, preenchendo com 0.
                    df_pivot = df_pivot.reindex(range(inicio, fim + 1), fill_value=0)
                    # 3. Melt: Transforma o DataFrame de volta ao formato "longo" que o Plotly espera.
                    df = df_pivot.reset_index().melt(id_vars=eixo_x_nome, value_name=eixo_y_nome, var_name=grupo_plotly)
                else:
                    # Se não for agrupado, o processo é mais simples:
                    # 1. Cria um DataFrame "gabarito" com todos os anos no intervalo.
                    eixo_completo = pd.DataFrame({eixo_x_nome: range(inicio, fim + 1)})
                    # 2. Junta o gabarito com os dados reais, preenchendo anos faltantes com 0.
                    df = eixo_completo.merge(df, on=eixo_x_nome, how="left").fillna(0)
                    # Garante que a coluna de valor seja do tipo inteiro para uma exibição mais limpa.
                    df[eixo_y_nome] = df[eixo_y_nome].astype(int)
            except (ValueError, TypeError, KeyError):
                # Ignora silenciosamente se os dados não puderem ser convertidos
                # ou se o DataFrame estiver vazio e .min()/.max() falhar.
                pass
        # ==============================================================================
        # FIM DA LÓGICA DE PREENCHIMENTO DE ANOS
        # ==============================================================================
        
        # --- LÓGICA DE ORDENAÇÃO FINAL E CORRETA ---
        category_orders_config = {}
        if grupo_plotly:
            # Verifica se o 'agrupamento' (ex: 'sexo') tem uma ordem customizada
            # definida na configuração CATEGORY_ORDERS em BasePlots.
            custom_order = self.plotter.CATEGORY_ORDERS.get(agrupamento)
            if custom_order:
                # Prepara um dicionário que o Plotly entende.
                # Exemplo: {'Sexo': ['M', 'F', 'D']}
                category_orders_config = {grupo_plotly: custom_order}
        # --- FIM DA LÓGICA DE ORDENAÇÃO ---
        
        titulo_override = kwargs.get('titulo_override')
        titulo_base = titulo_override or self.mapeamento['titulo_base']
        titulo_final = f"{titulo_base} por {eixo_x_nome}"
        if grupo_plotly:
             titulo_final = f"{titulo_base} por {grupo_plotly}"

        # Prepara os parâmetros para o Plotly, incluindo a ordem customizada.
        params = {
            "x": eixo_x_nome, 
            "y": eixo_y_nome, 
            "color": grupo_plotly, 
            "title": titulo_final,
            "category_orders": category_orders_config # <-- O PLOTLY USARÁ ISSO DIRETAMENTE
        }
        
        # O método _gerar_grafico passará o 'category_orders' para o Plotly Express.
        return self.plotter._gerar_grafico(df, tipo_grafico, params, **kwargs)