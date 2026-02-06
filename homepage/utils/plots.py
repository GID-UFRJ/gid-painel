# homepage/utils/plots.py
from common.utils.baseplots import BasePlots
from .mapeamentos import MAPEAMENTOS

class HomePlotter(BasePlots):
    @property
    def MAPEAMENTOS(self):
        return MAPEAMENTOS