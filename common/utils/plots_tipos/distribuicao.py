# common/utils/plots_tipos/distribuicao.py
import pandas as pd
import numpy as np
from .xy_base import XYBaseStrategy

class DistribuicaoStrategy(XYBaseStrategy):
    """
    Estratégia universal para criar Histogramas categóricos baseados em Bins definidos no mapeamento.
    """

    def _get_raw_dataframe(self) -> pd.DataFrame:
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['nome_plot'], self.filtros)

        campo_fatiar = self.mapeamento["eixo_x_campo"]
        agrupamento = self.filtros.get("agrupamento")
        campo_grupo = self.mapeamento.get("agrupamentos", {}).get(agrupamento)

        campos_busca = [campo_fatiar] + ([campo_grupo] if campo_grupo else [])
        df = pd.DataFrame(list(queryset.values(*campos_busca)))

        if df.empty:
            return pd.DataFrame()

        # ==========================================================
        # BUSCA DOS LIMITES DINÂMICOS NO MAPEAMENTO
        # ==========================================================
        # Pega os limites do dicionário (ou usa um fallback bem genérico se o programador esquecer)
        limites = self.mapeamento.get("distribuicao_bins", [-1, 0, 10, 50, 100, np.inf])
        rotulos = self.mapeamento.get("distribuicao_labels", ['0', '1-10', '11-50', '51-100', '> 100'])

        # Validação de segurança crucial para o pd.cut não explodir
        if len(limites) != len(rotulos) + 1:
            raise ValueError(
                f"Erro de Mapeamento em '{self.mapeamento['nome_plot']}': "
                f"A lista 'distribuicao_bins' ({len(limites)} itens) deve ter exatamente "
                f"1 item a mais que a 'distribuicao_labels' ({len(rotulos)} itens)."
            )

        # O Pandas fatia a coluna usando as regras extraídas do mapeamento
        nome_eixo_x = self.mapeamento["eixo_x_nome"]
        df[nome_eixo_x] = pd.cut(df[campo_fatiar], bins=limites, labels=rotulos, right=True)

        # ==========================================================
        # AGRUPAMENTO E CONTAGEM (Soma as ocorrências em cada Bin)
        # ==========================================================
        nome_eixo_y = self.mapeamento["eixo_y_nome"]
        colunas_agrupamento = [nome_eixo_x] + ([campo_grupo] if campo_grupo else [])

        df_final = df.groupby(colunas_agrupamento, as_index=False).size()
        df_final.rename(columns={'size': nome_eixo_y}, inplace=True)

        if campo_grupo:
            labels_dict = self.mapeamento.get('labels_customizadas', {})
            if labels_dict:
                df_final[campo_grupo] = df_final[campo_grupo].astype(str).replace(labels_dict)
                
            nome_grupo_bonito = labels_dict.get(agrupamento, agrupamento.replace('_', ' ').capitalize())
            df_final.rename(columns={campo_grupo: nome_grupo_bonito}, inplace=True)

        return df_final