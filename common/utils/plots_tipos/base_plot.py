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

    @abstractmethod
    def _get_raw_dataframe(self) -> pd.DataFrame:
        """
        MÉTODO INTERNO: As classes filhas implementam as queries e retornam um 
        DataFrame do Pandas com os dados processados conforme os filtros e o mapeamento.
        """
        pass

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

        return df

    @abstractmethod
    def generate_plot(self, df: pd.DataFrame, **kwargs):
        """
        Recebe o DataFrame e retorna a representação visual do gráfico
        (geralmente um JSON para Plotly/Chart.js ou HTML).
        """
        pass