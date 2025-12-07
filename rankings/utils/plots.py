# rankings/utils/plots.py
from common.utils.baseplots import BasePlots
from .mapeamentos import MAPEAMENTOS

class PlotsRankings(BasePlots):
    MAPEAMENTOS = MAPEAMENTOS

    def evolucao_academico(self, **kwargs):
        return self.generate_plot_html("academico_faixa", kwargs)

    def evolucao_sustentabilidade(self, **kwargs):
        return self.generate_plot_html("sustentabilidade_faixa", kwargs)
