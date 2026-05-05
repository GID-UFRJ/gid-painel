import pandas as pd
from .topn import TopNStrategy 
from common.utils.plot_helpers import gerar_sigla, renomear_siglas_duplicadas 

class TopInstituicoesStrategy(TopNStrategy):
    """
    Usa toda a inteligência genérica do TopN, mas aplica a regra 
    de negócio específica de siglas de instituições no final.
    """

    def _get_raw_dataframe(self) -> pd.DataFrame:
        from django.db.models import Q

        # =======================================================
        # 1. LÓGICA DE ABRANGÊNCIA (Nacional vs Internacional)
        # =======================================================
        valor_bruto = self.filtros.pop("tipo_colaboracao", "nacional")

        if isinstance(valor_bruto, (list, tuple)):
            valor_bruto = valor_bruto[0] if valor_bruto else "nacional"

        tipo = str(valor_bruto).strip().lower()

        self.filtros.pop("country_code", None)
        self.filtros.pop("filtro_q_pais", None)

        if tipo == "internacional":
            self.filtros["filtro_q_pais"] = ~Q(country_code='BR') & Q(country_code__isnull=False)
        else:
            self.filtros["country_code"] = "BR"

        # =======================================================
        # 2. BUSCA NO BANCO DE DADOS
        # =======================================================
        df = super()._get_raw_dataframe()

        if df.empty: 
            return df

        # =======================================================
        # 3. GERAÇÃO E TRATAMENTO DE SIGLAS PARA O EIXO Y
        # =======================================================
        coluna_eixo_y = self.mapeamento.get("eixo_y_nome", "Instituição")
        nome_coluna_original = self.mapeamento.get("ranking_campo_categoria", "institution_name")
        coluna_alvo = coluna_eixo_y if coluna_eixo_y in df.columns else nome_coluna_original

        # -> NOVO: Salva o nome original em uma coluna extra antes de sobrescrever!
        df["Nome Completo"] = df[coluna_alvo]

        # Passo A: Transforma os nomes longos em siglas usando sua função
        df[coluna_eixo_y] = df[coluna_alvo].apply(gerar_sigla)

        # Passo B: Desambigua siglas repetidas
        df[coluna_eixo_y] = renomear_siglas_duplicadas(df[coluna_eixo_y])
    
        return df
        
    def _build_figure(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
        coluna_eixo_y = self.mapeamento.get("eixo_y_nome", "Instituição")
        
        # 1. Coloca o nome oficial completo no topo do hover em negrito
        kwargs['hover_name'] = 'Nome Completo'
        
        # 2. Esconde o nome duplicado e a sigla das linhas de baixo
        kwargs['hover_data'] = {
            'Nome Completo': False, 
            coluna_eixo_y: False
        }
        
        return super()._build_figure(df, tipo_grafico, **kwargs)