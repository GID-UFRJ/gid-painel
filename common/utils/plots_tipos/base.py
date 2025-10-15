# common/utils/plots_tipos/base.py

import pandas as pd
from abc import ABC, abstractmethod

class BasePlotStrategy(ABC):
    """
    CLASSE BASE ABSTRATA (O CONTRATO)

    Define a estrutura e os métodos que toda classe de estratégia de plotagem
    deve implementar. Ela garante que o "artesão" (BasePlots) possa usar qualquer
    "ferramenta" (estratégia) da mesma maneira.
    """
    def __init__(self, mapeamento: dict, filtros: dict, plotter_instance: object):
        """
        O construtor armazena as informações essenciais para a estratégia funcionar.

        :param mapeamento: A "receita" específica do gráfico, vinda do MAPEAMENTOS.
        :param filtros: Os filtros selecionados pelo usuário (ex: {'ano_inicial': 2020}).
        :param plotter_instance: A instância da classe orquestradora (ex: PlotsPessoal),
                                 para que a estratégia possa usar seus métodos auxiliares.
        """
        self.mapeamento = mapeamento
        self.filtros = filtros
        self.plotter = plotter_instance

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        """
        Método obrigatório para buscar, filtrar e preparar os dados brutos.
        Deve retornar um DataFrame do Pandas.
        Esta é a "fonte da verdade" dos dados.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        """
        Método obrigatório para pegar um DataFrame já processado e gerar o HTML do gráfico.
        Deve retornar uma string contendo o HTML.
        """
        raise NotImplementedError