# Em evolucao_colaboracao.py

import pandas as pd
from .agregado import AggregatedPlotStrategy

class EvolucaoColaboracaoStrategy(AggregatedPlotStrategy):
        
    def get_dataframe(self) -> pd.DataFrame:
        valor_bruto = self.filtros.pop("tipo_colaboracao", "nacional")
        if isinstance(valor_bruto, (list, tuple)):
            valor_bruto = valor_bruto[0] if valor_bruto else "nacional"
            
        tipo = str(valor_bruto).strip().lower()
        self._tipo_selecionado = tipo

        # A MÁGICA: Agora apenas filtramos pelos booleanos do nosso novo Hook!
        if tipo == "internacional":
            self.filtros["tem_colab_internacional"] = True
        else:
            self.filtros["tem_colab_nacional"] = True

        df = super().get_dataframe()

        if df.empty:
            return df

        agrupamento = self.filtros.get("agrupamento")
        if agrupamento == "acesso_aberto":
            coluna_grupo = self.mapeamento.get('labels_customizadas', {}).get("acesso_aberto", "Acesso Aberto")
            if coluna_grupo in df.columns:
                df[coluna_grupo] = df[coluna_grupo].map({
                    True: 'Acesso Aberto', False: 'Acesso Fechado',
                    'True': 'Acesso Aberto', 'False': 'Acesso Fechado'
                })

        return df

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        tipo = getattr(self, '_tipo_selecionado', 'nacional')
        kwargs['titulo_override'] = "Colaborações Internacionais por Ano" if tipo == 'internacional' else "Colaborações Nacionais por Ano"
        return super().generate_plot(df, tipo_grafico, **kwargs)