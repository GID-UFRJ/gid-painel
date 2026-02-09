# common/utils/baseplots.py

import pandas as pd
import plotly.express as px
import unicodedata
import re
from django.db.models import Q, Count, Sum, Avg, Max

# Importamos as estratégias (ferramentas)
from .plots_tipos.agregado import AggregatedPlotStrategy
from .plots_tipos.hierarquico import HierarchicalPlotStrategy
from .plots_tipos.topn import TopNStrategy
from .plots_tipos.direto import DirectPlotStrategy
from .plots_tipos.faixa import RangeAreaStrategy
from .plots_tipos.kpi import KPIStrategy 
from .plots_tipos.ranking_kpi import RankingKPIStrategy

class BasePlots:
    """
    O ORQUESTRADOR DE PLOTAGEM (O "ARTESÃO")
    Orquestra a geração de gráficos, KPIs e a extração de dados.
    """
    
    # Mapeamento global de estratégias disponíveis
    STRATEGY_MAPPING = {
        'aggregated': AggregatedPlotStrategy,
        'hierarchical': HierarchicalPlotStrategy,
        'topn': TopNStrategy,
        'direct': DirectPlotStrategy, 
        'faixa': RangeAreaStrategy,
        'kpi': KPIStrategy,
        'ranking_kpi': RankingKPIStrategy,
    }

    # Configurações de cores e ordens para consistência visual
    CATEGORY_ORDERS = {
        'sexo': ['M', 'F', 'D'],
        'faixa_etaria': [
            '19 OU MENOS', '20 A 24 ANOS', '25 A 29 ANOS', '30 A 34 ANOS',
            '35 A 39 ANOS', '40 A 44 ANOS', '45 A 49 ANOS', '50 A 54 ANOS',
            '55 A 59 ANOS', '60 A 64 ANOS', '65 A 69 ANOS', '70 OU MAIS'
        ]
    }

    # Funções de renderização do Plotly
    PLOT_FUNCS = {
        "barra": px.bar, "linha": px.line, "pizza": px.pie,
        "sunburst": px.sunburst, "treemap": px.treemap,
    }
    PLOT_CONFIGS = {
        "barra": {"text_auto": True, "barmode": "group"}, 
        "linha": {"markers": True}
    }

    @property
    def MAPEAMENTOS(self):
        """As subclasses (ex: HomePlotter) devem implementar este atributo."""
        raise NotImplementedError("Subclasses devem implementar o atributo MAPEAMENTOS.")

    # ==========================================================
    # INTERFACE PÚBLICA (VIEWS E TEMPLATE TAGS)
    # ==========================================================

    def generate_plot_html(self, nome_plot: str, filtros_selecionados: dict, **kwargs) -> str:
        """Gera o HTML final para um gráfico ou KPI."""
        strategy = self._get_strategy_for_plot(nome_plot, filtros_selecionados)
        df = strategy.get_dataframe()
        
        # Determina o tipo de gráfico (HTMX > Receita > Padrão)
        tipo_grafico = filtros_selecionados.get(
            'tipo_grafico',
            strategy.mapeamento.get(
                'tipo_grafico',
                strategy.mapeamento.get('tipo_grafico_padrao', 'barra')
            )
        )
        return strategy.generate_plot(df, tipo_grafico=tipo_grafico, **kwargs)

    def get_dataframe_for_plot(self, nome_plot: str, filtros: dict) -> pd.DataFrame:
        """Retorna os dados brutos em DataFrame (útil para CSV)."""
        strategy = self._get_strategy_for_plot(nome_plot, filtros)
        return strategy.get_dataframe()

    # ==========================================================
    # LÓGICA DE ORQUESTRAÇÃO INTERNA
    # ==========================================================

    def _get_strategy_for_plot(self, nome_plot: str, filtros: dict):
        """Instancia a estratégia correta com base no mapeamento."""
        mapeamento = self._get_mapeamento_by_public_name(nome_plot)
        if not mapeamento:
            raise ValueError(f"Nenhum mapeamento encontrado para '{nome_plot}'.")
        
        strategy_name = mapeamento.get('estrategia_plot', 'aggregated')
        StrategyClass = self.STRATEGY_MAPPING.get(strategy_name)

        if not StrategyClass:
            raise ValueError(f"Estratégia '{strategy_name}' não registrada.")
            
        return StrategyClass(mapeamento, filtros, self)

    def _get_mapeamento_by_public_name(self, nome_plot: str) -> dict | None:
        """Busca a receita pelo nome público definido no dicionário."""
        for tipo_entidade, mapeamento in self.MAPEAMENTOS.items():
            if mapeamento.get('nome_plot') == nome_plot:
                mapeamento['__tipo_entidade__'] = tipo_entidade
                return mapeamento
        return None

    def _get_base_queryset(self, tipo_entidade: str, filtros_usuario: dict):
        """
        Constrói o QuerySet aplicando filtros de segurança e resolvendo 
        campos dinâmicos.
        """
        mapeamento = self.MAPEAMENTOS.get(tipo_entidade)
        if not mapeamento:
            raise ValueError(f"Entidade '{tipo_entidade}' não mapeada.")
            
        modelo = mapeamento["modelo"]
        mapa_filtros_config = mapeamento.get("filtros", {})

        # Merge de filtros padrão da receita com filtros da requisição
        filtros_finais = mapeamento.get("filtros_padrao", {}).copy()
        filtros_finais.update(filtros_usuario)

        queryset = modelo.objects.all()

        for chave_filtro, valor in filtros_finais.items():
            # Ignora valores nulos ou vazios
            if valor is None or (isinstance(valor, str) and valor.lower() in ["total", ""]):
                continue
            
            # --- SUPORTE A OBJETOS Q (LÓGICA COMPLEXA) ---
            # Se o valor já for um objeto Q, aplicamos direto no filter()
            if isinstance(valor, Q):
                queryset = queryset.filter(valor)
                continue # Pula para o próximo filtro do loop
            # ---------------------------------------------

            # --- TRATAMENTO DE LISTA (Proteção contra TypeError) ---
            # Se o valor for uma lista de 1 elemento (comum em QueryDict), achatamos.
            # Se for > 1, mantemos a lista para filtros do tipo __in.
            if isinstance(valor, (list, tuple)):
                if len(valor) == 1:
                    valor = valor[0]
                elif len(valor) == 0:
                    continue

            # --- RESOLUÇÃO DE CAMPO ---
            # 1. Tenta buscar o apelido no dicionário de filtros
            campo_real = mapa_filtros_config.get(chave_filtro)
            
            # 2. Se não houver apelido, verifica se a chave já é um campo do modelo (ou relação __)
            # Isso permite que filtros gerados dinamicamente (como no KPI) passem.
            if not campo_real:
                try:
                    # Verifica se o prefixo da chave existe no modelo
                    modelo._meta.get_field(chave_filtro.split('__')[0])
                    campo_real = chave_filtro
                except Exception:
                    campo_real = None

            if campo_real:
                queryset = queryset.filter(**{campo_real: valor})
            else:
                # Log opcional para depuração em desenvolvimento
                # print(f"[AVISO] Filtro '{chave_filtro}' ignorado por não estar mapeado.")
                pass
        
        return queryset, mapeamento, filtros_finais

    # ==========================================================
    # UTILITÁRIOS INTERNOS
    # ==========================================================

    def _formatar_alias_de_coluna(self, nome_exibicao: str) -> str:
        """Cria um slug seguro para aliases SQL."""
        s = unicodedata.normalize('NFD', nome_exibicao).encode('ascii', 'ignore').decode('utf-8')
        s = s.lower()
        s = re.sub(r'[\s-]+', '_', s)
        s = re.sub(r'[^\w_]', '', s)
        return s

    def _gerar_grafico(self, df: pd.DataFrame, tipo_grafico: str, params: dict, pronto_para_plot: bool = True, **kwargs):
        """Invoca o Plotly Express e aplica o layout padrão."""
        func = self.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Gráfico '{tipo_grafico}' não suportado.")

        plot_args = self.PLOT_CONFIGS.get(tipo_grafico, {}).copy()
        plot_args.update({k: v for k, v in params.items() if v is not None})

        fig = func(df, **plot_args)

        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            title_text=params.get("title", ""),
            xaxis_title=params.get("x", ""),
            yaxis_title=params.get("y", ""),
            legend_title_text=params.get("color", ""),
            xaxis=dict(type="category"),
        )

        if tipo_grafico == "barra":
            fig.update_traces(textposition="outside")

        if not pronto_para_plot:
            return fig

        return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True, "displaylogo": False})