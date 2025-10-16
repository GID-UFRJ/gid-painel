# common/utils/baseplots.py

import pandas as pd
import plotly.express as px
import unicodedata
import re
from django.db.models import Count, Sum, Avg


# Importamos as "ferramentas" da nossa "caixa de ferramentas" (o pacote plots_tipos)
# Certifique-se de que o __init__.py em plots_tipos está exportando essas classes.
from .plots_tipos import AggregatedPlotStrategy, HierarchicalPlotStrategy, TopNStrategy, DirectPlotStrategy


class BasePlots:
    """
    O ORQUESTRADOR DE PLOTAGEM (O "ARTESÃO")

    Esta classe orquestra a geração de gráficos e a extração de dados.
    Ela escolhe a "estratégia" (ferramenta) correta com base na configuração
    do mapeamento e delega o trabalho pesado, além de fornecer métodos auxiliares comuns.
    """
    # ==========================================================
    # PROPRIEDADES DE CONFIGURAÇÃO
    # ==========================================================
    
    # O "catálogo de ferramentas": mapeia o nome da estratégia para a sua classe.
    STRATEGY_MAPPING = {
        'aggregated': AggregatedPlotStrategy,
        'hierarchical': HierarchicalPlotStrategy,
        'topn': TopNStrategy,
        'direct': DirectPlotStrategy, # <-- REGISTRE A NOVA ESTRATÉGIA
    }

    CATEGORY_ORDERS = {
        'sexo': ['M', 'F', 'D'],
        'faixa_etaria': [
            '19 OU MENOS',
            '20 A 24 ANOS',
            '25 A 29 ANOS',
            '30 A 34 ANOS',
            '35 A 39 ANOS',
            '40 A 44 ANOS',
            '45 A 49 ANOS',
            '50 A 54 ANOS',
            '55 A 59 ANOS',
            '60 A 64 ANOS',
            '65 A 69 ANOS',
            '70 OU MAIS'
        ]
    }

    # Funções de plotagem do Plotly.
    PLOT_FUNCS = {
        "barra": px.bar, "linha": px.line, "pizza": px.pie,
        "sunburst": px.sunburst, "treemap": px.treemap,
    }
    PLOT_CONFIGS = {"barra": {"text_auto": True, "barmode": "group"}, "linha": {"markers": True}}

    # As classes filhas (PlotsPessoal, etc.) devem fornecer este mapa de receitas.
    @property
    def MAPEAMENTOS(self):
        raise NotImplementedError("Subclasses devem implementar o atributo MAPEAMENTOS.")

    # ==========================================================
    # MÉTODOS ORQUESTRADORES (A LÓGICA PRINCIPAL)
    # ==========================================================

    def _get_mapeamento_by_public_name(self, nome_plot: str) -> dict | None:
        """
        Busca a "receita" de mapeamento correta iterando sobre todos os mapeamentos
        e comparando o valor da chave 'nome_plot'.
        """
        for tipo_entidade, mapeamento in self.MAPEAMENTOS.items():
            if mapeamento.get('nome_plot') == nome_plot:
                # Adicionamos o 'tipo_entidade' (a chave interna do dicionário) ao
                # mapeamento para que a estratégia possa usá-lo.
                mapeamento['__tipo_entidade__'] = tipo_entidade
                return mapeamento
        return None

    def _get_strategy_for_plot(self, nome_plot: str, filtros: dict) -> object:
        """
        O cérebro do orquestrador.
        Escolhe e instancia a estratégia correta para um determinado plot.
        """
        # 1. Encontra a "receita" correta usando o 'nome_plot' da URL.
        mapeamento = self._get_mapeamento_by_public_name(nome_plot)
        if not mapeamento:
            raise ValueError(f"Nenhum mapeamento encontrado com nome_plot='{nome_plot}'.")
        
        # 2. Descobre qual estratégia usar a partir da receita (ou usa 'aggregated' como padrão).
        strategy_name = mapeamento.get('estrategia_plot', 'aggregated')
        StrategyClass = self.STRATEGY_MAPPING.get(strategy_name)

        if not StrategyClass:
            raise ValueError(f"Estratégia de plot '{strategy_name}' desconhecida ou não registrada no STRATEGY_MAPPING.")
            
        # 3. Retorna a "ferramenta" (estratégia) pronta para ser usada.
        return StrategyClass(mapeamento, filtros, self)


    # ==========================================================
    # INTERFACE PÚBLICA (USADA PELAS VIEWS)
    # ==========================================================

    def generate_plot_html(self, nome_plot: str, filtros_selecionados: dict, **kwargs) -> str:
        """
        Ponto de entrada único para gerar o HTML de um gráfico.
        """
        strategy = self._get_strategy_for_plot(nome_plot, filtros_selecionados)
        df = strategy.get_dataframe()
        tipo_grafico = filtros_selecionados.get(
            'tipo_grafico',  # Prioridade 1: A escolha explícita do usuário nos filtros da URL.
            strategy.mapeamento.get(
                'tipo_grafico',  # Prioridade 2: O tipo fixo definido na receita (ex: "sunburst").
                strategy.mapeamento.get(
                    'tipo_grafico_padrao',  # Prioridade 3: O padrão para gráficos flexíveis (ex: "linha").
                    'barra'  # Prioridade 4: O fallback final se nada for definido.
                )
            )
        )
        return strategy.generate_plot(df, tipo_grafico=tipo_grafico, **kwargs)

    def get_dataframe_for_plot(self, nome_plot: str, filtros: dict) -> pd.DataFrame:
        """
        Ponto de entrada único para obter os dados para download (CSV).
        """
        strategy = self._get_strategy_for_plot(nome_plot, filtros)
        return strategy.get_dataframe()


    # ==========================================================
    # MÉTODOS AUXILIARES INTERNOS (USADOS PELAS ESTRATÉGIAS)
    # ==========================================================

    def _get_mapeamento(self, tipo_entidade: str):
        """Método auxiliar para buscar uma receita específica."""
        mapeamento = self.MAPEAMENTOS.get(tipo_entidade)
        if not mapeamento:
            raise ValueError(f"Tipo de entidade '{tipo_entidade}' não encontrado nos MAPEAMENTOS.")
        mapeamento['__tipo_entidade__'] = tipo_entidade
        return mapeamento

    def _get_base_queryset(self, tipo_entidade: str, filtros_usuario: dict):
        """
        [CORPO COMPLETO] Constrói o queryset base do Django, aplicando filtros.
        Este método é usado pelas estratégias para obter a query inicial.
        """
        mapeamento = self._get_mapeamento(tipo_entidade)
        modelo = mapeamento["modelo"]
        mapa_filtros_config = mapeamento["filtros"]

        filtros_finais = mapeamento.get("filtros_padrao", {}).copy()
        filtros_finais.update(filtros_usuario)

        queryset = modelo.objects.all()

        # ==================================================================
        # INÍCIO DOS PRINTS DE DEPURAÇÃO
        # ==================================================================
        print("\n" + "="*50)
        print("--- DEPURAÇÃO EM _get_base_queryset ---")
        print(f"[INFO] Tipo de Entidade: '{tipo_entidade}'")
        print(f"[INFO] Filtros recebidos da view (filtros_usuario): {filtros_usuario}")
        print(f"[INFO] Filtros FINAIS a serem aplicados: {filtros_finais}")
        print("-" * 20)
        
        for chave_filtro, valor in filtros_finais.items():
            if valor is None or (isinstance(valor, str) and valor.lower() in ["total", ""]):
                continue
            
            campo_real = mapa_filtros_config.get(chave_filtro)
            
            print(f"-> Processando filtro: '{chave_filtro}' = '{valor}'")
            if campo_real:
                print(f"   - Mapeado para o campo do DB: '{campo_real}'")
                queryset = queryset.filter(**{campo_real: valor})
                print(f"   - Filtro APLICADO.")
            else:
                print(f"   - ⚠️ AVISO: Chave de filtro '{chave_filtro}' não encontrada no mapa de filtros da receita. Ignorando.")
        
        # O print mais importante: mostra a query SQL que o Django vai executar.
        print("\n[SQL] Query final construída:")
        print(queryset.query)
        print("="*50 + "\n")
        # ==================================================================
        # FIM DOS PRINTS DE DEPURAÇÃO
        # ==================================================================

        for chave_filtro, valor in filtros_finais.items():
            if valor is None or (isinstance(valor, str) and valor.lower() in ["total", ""]):
                continue
            
            campo_real = mapa_filtros_config.get(chave_filtro)
            if campo_real:
                queryset = queryset.filter(**{campo_real: valor})
        
        return queryset, mapeamento, filtros_finais

    def _formatar_alias_de_coluna(self, nome_exibicao: str) -> str:
        """[CORPO COMPLETO] Cria um nome seguro para usar como alias em anotações SQL."""
        s = unicodedata.normalize('NFD', nome_exibicao)
        s_ascii = s.encode('ascii', 'ignore')
        s = s_ascii.decode('utf-8')
        s = s.lower()
        s = re.sub(r'[\s-]+', '_', s)
        s = re.sub(r'[^\w_]', '', s)
        return s

    def _gerar_grafico(self, df: pd.DataFrame, tipo_grafico: str, params: dict, pronto_para_plot: bool = True, **kwargs):
        """
        [CORPO COMPLETO] O passo final: pega um DataFrame e os parâmetros e chama o Plotly.
        Retorna o HTML ou o objeto Figure bruto.
        """
        func = self.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não suportado.")

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

        config = {
            "responsive": True,
            "displaylogo": False,
        }
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)