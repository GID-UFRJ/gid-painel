# homepage/utils/plots.py
from common.utils.dispatcher import Dispatcher
from .mapeamentos import MAPEAMENTOS

class HomePlotter(Dispatcher):
    @property
    def MAPEAMENTOS(self):
        return MAPEAMENTOS