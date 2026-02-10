# common/utils/plots_tipos/direto.py

import pandas as pd
from .xy_base import XYBaseStrategy # Importa a nova classe base intermediária

class DirectPlotStrategy(XYBaseStrategy):
    """
    ESTRATÉGIA ESPECÍFICA PARA PLOTS DIRETOS

    Busca valores diretamente do modelo sem aplicar agregação (Count, Sum, Avg).
    Ideal para séries temporais simples como 'conceito por ano'.
    """
    def get_dataframe(self) -> pd.DataFrame:
        """
        Implementação para buscar valores diretos.
        """
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        eixo_x_campo = self.mapeamento["eixo_x_campo"]
        eixo_y_campo = self.mapeamento["eixo_y_campo"]
        
        # A query é muito mais simples: apenas seleciona os valores das duas colunas.
        dados = queryset.values(eixo_x_campo, eixo_y_campo).order_by(eixo_x_campo)
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        # Renomeia as colunas para nomes amigáveis
        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        eixo_y_nome = self.mapeamento["eixo_y_nome"]
        df.rename(columns={eixo_x_campo: eixo_x_nome, eixo_y_campo: eixo_y_nome}, inplace=True)

        return df