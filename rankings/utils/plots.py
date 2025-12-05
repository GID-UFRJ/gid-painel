# rankings/utils/plots.py
from common.utils.baseplots import BasePlots
from .mapeamentos import MAPEAMENTOS

class PlotsRankings(BasePlots):
    MAPEAMENTOS = MAPEAMENTOS

    def evolucao_academico(self, **kwargs):
        # Invertemos o eixo Y porque em ranking, quanto menor o número, melhor.
        # O Plotly permite isso passando 'autorange': 'reversed' no update_layout (via trace_updates ou customização)
        # Por simplicidade, vamos gerar o padrão primeiro.
        return self._gerar_grafico_agregado(
            "ranking_academico_evolucao", "linha", kwargs, 
            agrupamento=kwargs.get("agrupamento", "ranking")
        )

    def evolucao_sustentabilidade(self, **kwargs):
        return self._gerar_grafico_agregado(
            "ranking_sustentabilidade_evolucao", "linha", kwargs,
            agrupamento=kwargs.get("agrupamento", "ods")
        )