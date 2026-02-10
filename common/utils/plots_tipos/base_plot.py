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
    def get_dataframe(self) -> pd.DataFrame:
        """
        Deve retornar um DataFrame do Pandas com os dados processados 
        conforme os filtros e o mapeamento.
        """
        pass

    @abstractmethod
    def generate_plot(self, df: pd.DataFrame, **kwargs):
        """
        Recebe o DataFrame e retorna a representação visual do gráfico
        (geralmente um JSON para Plotly/Chart.js ou HTML).
        """
        pass