# em common/utils/plots_tipos/agregado.py
import pandas as pd
from django.db.models import Count, Sum, Avg
from .xy_base import XYBaseStrategy

class AggregatedPlotStrategy(XYBaseStrategy):
    """
    Estratégia para plots agregados.
    """
    def get_dataframe(self) -> pd.DataFrame:
        """
        [MÉTODO ATUALIZADO]
        Agora, ao calcular uma média (avg), também calcula a contagem (count)
        e a adiciona ao DataFrame em uma nova coluna chamada 'Contagem'.
        """
        queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['__tipo_entidade__'], self.filtros)
        
        eixo_x_campo = self.mapeamento["eixo_x_campo"]
        eixo_x_nome = self.mapeamento["eixo_x_nome"]
        eixo_y_campo = self.mapeamento.get("eixo_y_campo", "id")
        eixo_y_nome = self.mapeamento.get("eixo_y_nome", "Total")
        agregacao_str = self.mapeamento.get("eixo_y_agregacao", "count")

        agrupamento = self.filtros.get("agrupamento")
        campo_grupo = self.mapeamento.get("agrupamentos", {}).get(agrupamento)
        
        valores_a_buscar = [eixo_x_campo]
        if campo_grupo:
            valores_a_buscar.append(campo_grupo)

        # --- LÓGICA DE AGREGAÇÃO APRIMORADA ---
        agregacao_base = agregacao_str.split('_')[0]
        alias_coluna_y = self.plotter._formatar_alias_de_coluna(eixo_y_nome)
        
        if agregacao_base == 'avg':
            # Se for uma média, calculamos a média E a contagem.
            dados = queryset.values(*valores_a_buscar).annotate(
                **{alias_coluna_y: Avg(eixo_y_campo)},
                Contagem=Count(eixo_y_campo) # Adiciona uma nova coluna 'Contagem'
            ).order_by(eixo_x_campo)
        else:
            # Para outros casos (count, sum), a lógica permanece a mesma.
            distinct = 'distinct' in agregacao_str.lower()
            agg_map = {"count": Count(eixo_y_campo, distinct=distinct), "sum": Sum(eixo_y_campo)}
            agg_func = agg_map.get(agregacao_base.lower())
            dados = queryset.values(*valores_a_buscar).annotate(**{alias_coluna_y: agg_func}).order_by(eixo_x_campo)
        
        df = pd.DataFrame(list(dados))

        if df.empty:
            return pd.DataFrame()

        df.rename(columns={eixo_x_campo: eixo_x_nome, alias_coluna_y: eixo_y_nome}, inplace=True)
        if campo_grupo:
            df.rename(columns={campo_grupo: agrupamento.replace('_', ' ').capitalize()}, inplace=True)

        return df