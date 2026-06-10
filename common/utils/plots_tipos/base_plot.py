# common/utils/plots_tipos/base_plots.py
from abc import ABC, abstractmethod
import pandas as pd

class BasePlotStrategy(ABC):
    """
    Interface abstrata para todas as estratégias que geram gráficos.
    Exige processamento de dados via Pandas e renderização visual.
    """

    def __init__(self, mapeamento, filtros=None, plotter=None):
        self.mapeamento = mapeamento
        self.filtros = filtros if filtros is not None else {}
        self.plotter = plotter

    # ==========================================================
    # PIPELINE DE DADOS (DATAFRAME)
    # ==========================================================
    def get_processed_dataframe(self) -> pd.DataFrame:
        """
        MÉTODO PÚBLICO: Retorna o dado processado. É este método que será chamado para a exportação de CSV e geracao dos plots.
        """
        df = self._get_raw_dataframe()

        if df.empty:
            return df

        # Aplica APENAS as traduções estruturais definidas no dicionário (ex: domínios, áreas)
        traducoes_especificas = self.mapeamento.get('substituicoes')
        if traducoes_especificas:
            df.replace(traducoes_especificas, inplace=True)

            if self.mapeamento.get('reagrupar_apos_substituicao', False):
                
                nome_y_agregado = self.mapeamento.get('eixo_y_nome')
                nome_y_ranking = self.mapeamento.get('ranking_campo_valor_alias')
                nome_y_hierarquico = self.mapeamento.get('grafico_hierarquico_values_nome', 'Total')
                
                tipo_agregacao = self.mapeamento.get('eixo_y_agregacao', self.mapeamento.get('grafico_hierarquico_agregacao', 'count')).lower()
                
                possiveis_metricas = [nome_y_agregado, nome_y_ranking, nome_y_hierarquico, 'Contagem', 'total']
                colunas_para_somar = [col for col in possiveis_metricas if col and col in df.columns]
                
                if colunas_para_somar:
                    colunas_agrupamento = [col for col in df.columns if col not in colunas_para_somar]
                    
                    try:
                        for col in colunas_para_somar:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                            
                        if 'avg' in tipo_agregacao and 'Contagem' in df.columns and nome_y_agregado:
                            df['_soma_bruta'] = df[nome_y_agregado] * df['Contagem']
                            df = df.groupby(colunas_agrupamento, as_index=False)[['_soma_bruta', 'Contagem']].sum()
                            df[nome_y_agregado] = df['_soma_bruta'] / df['Contagem']
                            df.drop(columns=['_soma_bruta'], inplace=True)
                        else:
                            df = df.groupby(colunas_agrupamento, as_index=False)[colunas_para_somar].sum()
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao tentar reagrupar DataFrame: {e}")

        return df

    @abstractmethod
    def _get_raw_dataframe(self) -> pd.DataFrame:
        """
        MÉTODO INTERNO: As classes filhas implementam as queries e retornam um 
        DataFrame do Pandas com os dados processados conforme os filtros e o mapeamento.
        """
        pass

    # ==========================================================
    # PIPELINE VISUAL (PLOTS)
    # ==========================================================

    def _inject_color_mapping(self, df: pd.DataFrame, kwargs: dict) -> dict:
        """
        MÉTODO INTERNO: Descobre a coluna de cor e constrói o mapa de cores 
        injetando no dicionário de parâmetros do Plotly.

        - Alguns plots (como o sunburst) colorem com base no total de ocorrências. Aqui, normalizamos isso ao colorir por uma coluna ordenada alfabeticamente.
        """
        # Para plots como o Hierarchical, geralmente a cor é por categoria com maior 
        # número de ocorrências. Isso normaliza para ordem alfabética.
        coluna_cor = self.mapeamento.get('colorir_alfabeticamente_por') 
        
        # Se não for fixa, descobre pelo agrupamento do HTMX
        if not coluna_cor and self.filtros.get('agrupamento'):
            agrupamento = self.filtros.get('agrupamento')
            labels = self.mapeamento.get('labels_customizadas', {})
            coluna_cor = labels.get(agrupamento, agrupamento.replace('_', ' ').capitalize())

        if coluna_cor and coluna_cor in df.columns:
            kwargs['color'] = coluna_cor

            # 1. Verifica se existe um mapa FIXO no mapeamento (ex: {'Sim': 'azul'})
            paleta_global = self.mapeamento.get('usar_paleta_oficial')
            
            if paleta_global and coluna_cor in paleta_global:
                kwargs['color_discrete_map'] = paleta_global[coluna_cor]
            else:
                # ======================================================
                # 2. SE NÃO TEM MAPA FIXO, GERA O DINÂMICO ALFABÉTICO GLOBAL
                # ======================================================
                nome_paleta = self.mapeamento.get('paleta', 'tableau_10')
                if hasattr(self.plotter, 'PALETAS'):
                    paleta = self.plotter.PALETAS.get(nome_paleta, self.plotter.PALETAS['tableau_10'])
                    
                    # Ordena alfabeticamente ignorando maiúsculas/minúsculas
                    categorias = sorted(
                        df[coluna_cor].dropna().astype(str).unique(),
                        key=lambda x: x.lower()
                    )
                    
                    # Cria o dicionário
                    mapa_cores = {
                        categoria: paleta[i % len(paleta)]
                        for i, categoria in enumerate(categorias)
                    }
                    
                    # Mantém cores globais do Dispatcher sobrescrevendo se necessário
                    if hasattr(self.plotter, 'COLOR_MAP'):
                        mapa_cores.update(self.plotter.COLOR_MAP)
                        
                    kwargs['color_discrete_map'] = mapa_cores
                # ======================================================
        
        return kwargs

    def generate_plot(self, df: pd.DataFrame, **kwargs):
            """
            MÉTODO PÚBLICO: Orquestra a injeção de cores e configurações globais
            antes de mandar a classe filha renderizar o gráfico.
            """
            # kwargs a serem passados para o método interno
            kwargs = self._inject_color_mapping(df, kwargs)

            return self._build_figure(df, **kwargs)

    @abstractmethod
    def _build_figure(self, df: pd.DataFrame, **kwargs):
        """
        MÉTODO INTERNO: Recebe o DataFrame e os parâmetros enriquecidos pela 
        BasePlotStrategy e retorna a representação visual final.
        """
        pass
