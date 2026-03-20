# common/utils/dispatcher.py
import pandas as pd
import plotly.express as px
import unicodedata
import re
from django.db.models import Q, Count, Sum, Avg, Max
from django.utils.text import slugify

# Importação das Estratégias
from .plots_tipos.agregado import AggregatedPlotStrategy
from .plots_tipos.hierarquico import HierarchicalPlotStrategy
from .plots_tipos.topn import TopNStrategy
from .plots_tipos.direto import DirectPlotStrategy 
from .plots_tipos.faixa import RangeAreaStrategy
from .plots_tipos.kpi import KPIStrategy 
from .plots_tipos.ranking_kpi import RankingKPIStrategy


class Dispatcher:
    STRATEGY_MAPPING = {
        'aggregated': AggregatedPlotStrategy,
        'hierarchical': HierarchicalPlotStrategy,
        'topn': TopNStrategy,
        'direct': DirectPlotStrategy, 
        'faixa': RangeAreaStrategy,
        'kpi': KPIStrategy,
        'ranking_kpi': RankingKPIStrategy,
    }

    CATEGORY_ORDERS = {
        'sexo': ['M', 'F', 'D'],
        'faixa_etaria': [
            '19 OU MENOS', '20 A 24 ANOS', '25 A 29 ANOS', '30 A 34 ANOS',
            '35 A 39 ANOS', '40 A 44 ANOS', '45 A 49 ANOS', '50 A 54 ANOS',
            '55 A 59 ANOS', '60 A 64 ANOS', '65 A 69 ANOS', '70 OU MAIS'
        ]
    }

    PLOT_FUNCS = {
        "barra": px.bar, "linha": px.line, "pizza": px.pie,
        "sunburst": px.sunburst, "treemap": px.treemap,
    }

    PLOT_CONFIGS = {"barra": {"text_auto": True, "barmode": "relative"}, "linha": {"markers": True}}

    # Dicionário que registra os querysets presentes no models.py de cada app
    QUERYSET_HOOKS = {
        'openalex': {
            'autor_correspondente': 'autor_correspondente_ufrj',
            'distribuicao_tematica': 'com_topico_principal',
        },
        'sucupira': {
            # 'bolsistas': 'apenas_bolsistas', (Exemplo futuro)
        }
    }

    PALETAS = {
        # Uma paleta "qualitativa" (para categorias distintas)
        'default': px.colors.qualitative.Plotly, # Cores padrão do Plotly
        
        # Uma paleta "sequencial" (ótima para True/False, Sim/Não, Escalas)
        # O UFRJ usa azul, então podemos usar um gradiente de azul e cinza/vermelho
        'openalex': ['#004a80', '#b0bec5', '#d32f2f'], # Azul UFRJ, Cinza, Vermelho
        
        # Outras paletas para o futuro
        'sucupira': px.colors.qualitative.G10,
        'impacto': px.colors.sequential.Blues,
    }

    # PALETAS DE CORES
    # Central de paletas por tipo de visualização
    #PALETAS_POR_TIPO = {
    #    'barra': ['#004a80', '#d32f2f', '#b0bec5'], # Azul UFRJ, Vermelho, Cinza
    #    'linha': ['#004a80', '#2ca02c', '#ff7f0e'], # Azul, Verde, Laranja
    #    'pizza': px.colors.qualitative.Safe,
    #    'sunburst': px.colors.qualitative.Pastel,
    #    'default': px.colors.qualitative.Plotly,    # Fallback caso o tipo não exista
    #}

    def __init__(self, entidade=None):
        self.entidade = entidade

    @property
    def MAPEAMENTOS(self):
        return getattr(self, 'MAPEAMENTOS', getattr(self, 'mapeamentos', {}))

    def generate_plot_html(self, nome_plot: str, filtros_selecionados: dict = None, **kwargs) -> str:
        print(f"2. Dispatcher tentando o plot: {nome_plot}")
        filtros = filtros_selecionados or {}
        mapeamento = self._get_mapeamento_by_public_name(nome_plot)
        print(f"3. Estratégia identificada: {mapeamento['estrategia_plot']}")
        if not mapeamento:
            return ""

        strategy_name = mapeamento.get('estrategia_plot', 'aggregated')
        StrategyClass = self.STRATEGY_MAPPING.get(strategy_name)
        
        if not StrategyClass:
            raise ValueError(f"Estratégia '{strategy_name}' não registrada.")

        strategy_instance = StrategyClass(mapeamento, filtros, self)

        if hasattr(strategy_instance, 'render'):
            return strategy_instance.render()
        
        df = strategy_instance.get_dataframe()
        tipo_grafico = filtros.get('tipo_grafico', mapeamento.get('tipo_grafico', mapeamento.get('tipo_grafico_padrao', 'barra')))
        return strategy_instance.generate_plot(df, tipo_grafico=tipo_grafico, **kwargs)

    # ==========================================================
    # LÓGICA DE FILTROS E QUERIES (UNIFICADA E ROBUSTA)
    # ==========================================================

    def _get_mapeamento_by_public_name(self, nome_plot: str) -> dict | None:
        for tipo_entidade, mapeamento in self.MAPEAMENTOS.items():
            if mapeamento.get('nome_plot') == nome_plot:
                mapeamento['__tipo_entidade__'] = tipo_entidade
                return mapeamento
        return None

    def _get_mapeamento(self, tipo_entidade: str):
        mapeamento = self.MAPEAMENTOS.get(tipo_entidade)
        if not mapeamento:
            raise ValueError(f"Tipo de entidade '{tipo_entidade}' não encontrado.")
        mapeamento['__tipo_entidade__'] = tipo_entidade
        return mapeamento

    def _get_base_queryset(self, tipo_entidade: str, filtros_usuario: dict):
        """
        Versão unificada: Suporta objetos Q, listas e possui logs de depuração.
        """
        mapeamento = self._get_mapeamento(tipo_entidade)
        modelo = mapeamento["modelo"]
        mapa_filtros_config = mapeamento.get("filtros", {}) # Proteção contra KeyError

        filtros_finais = mapeamento.get("filtros_padrao", {}).copy()
        filtros_finais.update(filtros_usuario or {})

        queryset = modelo.objects.all()

        # 1. Identificamos o app (ex: 'openalex' ou 'sucupira')
        # Podemos inferir pelo caminho do modelo ou passar explicitamente
        app_label = modelo._meta.app_label 
    
        # 2. Buscamos o valor do agrupamento enviado pela UI
        agrupamento_slug = (filtros_usuario or {}).get('agrupamento')

        # 3. LÓGICA DE HOOK GLOBAL
        # Verifica se existe um hook registrado para este APP e este AGRUPAMENTO
        hooks_do_app = self.QUERYSET_HOOKS.get(app_label, {})
        metodo_customizado = hooks_do_app.get(agrupamento_slug)

        if metodo_customizado:
            # Tenta disparar o método dinamicamente no QuerySet
            func = getattr(queryset, metodo_customizado, None)
            if func:
                queryset = func() # Executa o Case/When que você criou
                print(f"[Dispatcher] Hook '{metodo_customizado}' aplicado para o app '{app_label}'")



        print("\n" + "="*50)
        print("--- DEPURAÇÃO EM _get_base_queryset ---")
        print(f"[INFO] Tipo de Entidade: '{tipo_entidade}'")
        
        for chave_filtro, valor in filtros_finais.items():
            if valor is None or (isinstance(valor, str) and valor.lower() in ["total", ""]):
                continue
            
            print(f"-> Processando filtro: '{chave_filtro}' = '{valor}'")
            
            # Suporte a Objetos Q
            if isinstance(valor, Q):
                queryset = queryset.filter(valor)
                print("   - Filtro Q APLICADO.")
                continue

            # Tratamento de listas (QueryDict)
            if isinstance(valor, (list, tuple)):
                valor = valor[0] if len(valor) == 1 else valor
                if not valor: continue

            # Resolução do Campo
            campo_real = mapa_filtros_config.get(chave_filtro)
            if not campo_real:
                try:
                    modelo._meta.get_field(chave_filtro.split('__')[0])
                    campo_real = chave_filtro
                except: campo_real = None

            if campo_real:
                print(f"   - Mapeado para o campo do DB: '{campo_real}'")
                queryset = queryset.filter(**{campo_real: valor})
                print("   - Filtro APLICADO.")
            else:
                print(f"   - ⚠️ AVISO: Chave '{chave_filtro}' não mapeada. Ignorando.")
        
        print(f"\n[SQL] Query final construída:\n{queryset.query}")
        print("="*50 + "\n")
        
        return queryset, mapeamento, filtros_finais

    # ==========================================================
    # UTILITÁRIOS (ALIAS E PLOTLY)
    # ==========================================================

    def _formatar_alias_de_coluna(self, nome_exibicao: str) -> str:
        s = unicodedata.normalize('NFD', nome_exibicao).encode('ascii', 'ignore').decode('utf-8')
        s = s.lower()
        s = re.sub(r'[\s-]+', '_', s)
        s = re.sub(r'[^\w_]', '', s)
        return s

    def _gerar_grafico(self, df: pd.DataFrame, tipo_grafico: str, params: dict, pronto_para_plot: bool = True, **kwargs):
        func = self.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Gráfico '{tipo_grafico}' não suportado.")
    
        mapeamento = params.get('mapeamento_completo', {})
        paleta = mapeamento.get('paleta_cores')
    
        print(f"--- DEBUG PLOT ---")
        print(f"Tipo: {tipo_grafico}")
        print(f"Paleta encontrada no mapeamento: {paleta}")


        plot_args = self.PLOT_CONFIGS.get(tipo_grafico, {}).copy()
        plot_args.update({k: v for k, v in params.items() if v is not None})
    
        ## --- INJEÇÃO DE PALETAS (O que estava faltando) ---
        #if params.get('color'):
        #    # 1. Tenta pegar o mapeamento que foi passado no dispatcher
        #    mapeamento = params.get('mapeamento_completo', {}) or kwargs.get('mapeamento', {})
        #    
        #    # 2. Define a paleta seguindo a hierarquia: Mapeamento > Tipo > Default
        #    paleta_final = (
        #        mapeamento.get('paleta_cores') or 
        #        self.PALETAS.get(tipo_grafico) or 
        #        self.PALETAS.get('default')
        #    )
        #    
        #    # 3. Injeta a paleta antes de criar a figura
        #    plot_args['color_discrete_sequence'] = paleta_final
        ## --------------------------------------------------
    
        fig = func(df, **plot_args)
        
        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            title_text=params.get("title", ""),
            xaxis_title=params.get("x", ""),
            yaxis_title=params.get("y", ""),
            legend_title_text=params.get("color", ""),
            xaxis=dict(type="category",
                        categoryorder="category ascending"),
        )
    
        if tipo_grafico == "barra":
            fig.update_traces(textposition="outside")
    
        if not pronto_para_plot:
            return fig
    
        return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True, "displaylogo": False})


    # ==========================================================
    # EXPORTACAO CSV
    # ==========================================================


    def get_dataframe_for_plot(self, nome_plot: str, filtros_selecionados: dict = None) -> pd.DataFrame:
        """
        Interface unificada para exportação de CSV. 
        Reutiliza a lógica da Strategy para garantir que o CSV tenha os mesmos dados do gráfico.
        """
        filtros = filtros_selecionados or {}
    
        # 1. Busca as configurações do plot (modelo, campos, etc)
        mapeamento = self._get_mapeamento_by_public_name(nome_plot)
        if not mapeamento:
            print(f"DEBUG: Mapeamento não encontrado para {nome_plot}")
            return pd.DataFrame()

        # 2. Identifica qual Strategy usar (ex: 'aggregated', 'hierarchical')
        strategy_name = mapeamento.get('estrategia_plot', 'aggregated')
        StrategyClass = self.STRATEGY_MAPPING.get(strategy_name)
    
        if not StrategyClass:
            raise ValueError(f"Estratégia '{strategy_name}' não encontrada no Dispatcher.")

        # 3. Instancia a Strategy (ela aplicará os filtros de ano, liderança, etc)
        strategy_instance = StrategyClass(mapeamento, filtros, self)

        # 4. Retorna o DataFrame bruto processado
        return strategy_instance.get_dataframe()