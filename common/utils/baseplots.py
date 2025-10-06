# common/utils/baseplots.py - VERSÃO CORRIGIDA

import re
import unicodedata
from django.db.models import Count, Sum, Avg
import pandas as pd
import plotly.express as px
from pandas.api.types import CategoricalDtype

class BasePlots:
    # ... (propriedades e métodos _get_mapeamento, _get_base_queryset, _formatar_alias_de_coluna sem alterações) ...
    @property
    def MAPEAMENTOS(self):
        raise NotImplementedError("Subclasses devem implementar o atributo MAPEAMENTOS")
    CATEGORY_ORDERS = {"sexo": ["M", "F", "D"],}
    PLOT_FUNCS = {"barra": px.bar,"linha": px.line,"pizza": px.pie,}
    PLOT_CONFIGS = {"barra": {"text_auto": True, "barmode": "group"},"linha": {"markers": True},}
    def _get_mapeamento(self, tipo_entidade: str):
        mapeamento = self.MAPEAMENTOS.get(tipo_entidade)
        if not mapeamento:
            raise ValueError(f"Tipo de entidade '{tipo_entidade}' não encontrado nos MAPEAMENTOS.")
        return mapeamento
    def _get_base_queryset(self, tipo_entidade: str, filtros_usuario: dict):
        mapeamento = self._get_mapeamento(tipo_entidade)
        modelo = mapeamento["modelo"]
        mapa_filtros = mapeamento["filtros"]
        filtros_finais = mapeamento.get("filtros_padrao", {}).copy()
        filtros_finais.update(filtros_usuario)
        queryset = modelo.objects.all()
        for chave, valor in filtros_finais.items():
            if valor is None or (isinstance(valor, str) and valor.lower() in ["total", ""]):
                continue
            campo_real = mapa_filtros.get(chave)
            if campo_real:
                queryset = queryset.filter(**{campo_real: valor})
        order_by_fields = mapeamento.get('queryset_order_by')
        if order_by_fields:
            if isinstance(order_by_fields, str):
                order_by_fields = [order_by_fields]
            queryset = queryset.order_by(*order_by_fields)
        distinct_on_fields = mapeamento.get('queryset_distinct_on')
        if distinct_on_fields:
            if not order_by_fields:
                print(f"AVISO: Usando 'queryset_distinct_on' para '{tipo_entidade}' sem 'queryset_order_by' pode gerar resultados imprevisíveis.")
            if isinstance(distinct_on_fields, str):
                distinct_on_fields = [distinct_on_fields]
            queryset = queryset.distinct(*distinct_on_fields)
        return queryset, mapeamento, filtros_finais
    def _formatar_alias_de_coluna(self, nome_exibicao: str) -> str:
        s = unicodedata.normalize('NFD', nome_exibicao)
        s_ascii = s.encode('ascii', 'ignore')
        s = s_ascii.decode('utf-8')
        s = s.lower()
        s = re.sub(r'[\s-]+', '_', s)
        s = re.sub(r'[^\w_]', '', s)
        return s

    def _gerar_grafico_agregado(
        self,
        tipo_entidade: str,
        tipo_grafico: str,
        filtros_selecionados: dict,
        agrupamento: str | None = None,
        titulo_override: str | None = None,
        **kwargs,
    ):
        # ... (código de extração de configs, agregação e criação do DataFrame inicial sem alterações) ...
        queryset, mapeamento, filtros_finais = self._get_base_queryset(tipo_entidade, filtros_selecionados)
        eixo_x_campo = mapeamento["eixo_x_campo"]
        eixo_x_nome = mapeamento["eixo_x_nome"]
        eixo_x_tipo = mapeamento.get("eixo_x_tipo", "categorico")
        eixo_y_campo = mapeamento.get("eixo_y_campo", "id")
        eixo_y_nome = mapeamento.get("eixo_y_nome", "Total")
        agregacao_str = mapeamento.get("eixo_y_agregacao", "count")
        distinct = 'distinct' in agregacao_str.lower()
        agregacao_base = agregacao_str.split('_')[0]
        if distinct and agregacao_base != 'count':
            raise ValueError(f"A agregação 'distinct' só é suportada para 'count', não para '{agregacao_base}'. Verifique o 'eixo_y_agregacao' no mapeamento '{tipo_entidade}'.")
        agg_map = {"count": Count(eixo_y_campo, distinct=distinct), "sum": Sum(eixo_y_campo), "avg": Avg(eixo_y_campo)}
        agg_func = agg_map.get(agregacao_base.lower())
        if not agg_func:
            raise ValueError(f"Agregação '{agregacao_base}' não suportada.")
        campo_grupo = mapeamento.get("agrupamentos", {}).get(agrupamento)
        valores_a_buscar = [eixo_x_campo]
        if campo_grupo:
            valores_a_buscar.append(campo_grupo)
        alias_coluna_y = self._formatar_alias_de_coluna(eixo_y_nome)
        dados = queryset.values(*valores_a_buscar).annotate(**{alias_coluna_y: agg_func}).order_by(eixo_x_campo)
        df = pd.DataFrame(list(dados))
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
        df.rename(columns={eixo_x_campo: eixo_x_nome, alias_coluna_y: eixo_y_nome}, inplace=True)

        # Lógica de preenchimento e agrupamento
        grupo_plotly = None
        if campo_grupo:
            grupo_plotly = agrupamento
            df.rename(columns={campo_grupo: grupo_plotly}, inplace=True)
            df[grupo_plotly] = df[grupo_plotly].fillna("Não informado")

        if eixo_x_tipo == 'numerico_continuo':
            try:
                inicio = int(filtros_finais.get('ano_inicial', df[eixo_x_nome].min()))
                fim = int(filtros_finais.get('ano_final', df[eixo_x_nome].max()))
                if campo_grupo:
                    df_pivot = df.pivot_table(index=eixo_x_nome, columns=grupo_plotly, values=eixo_y_nome, fill_value=0)
                    df_pivot = df_pivot.reindex(range(inicio, fim + 1), fill_value=0)
                    df = df_pivot.reset_index().melt(id_vars=eixo_x_nome, value_name=eixo_y_nome, var_name=grupo_plotly)
                else:
                    eixo_completo = pd.DataFrame({eixo_x_nome: range(inicio, fim + 1)})
                    df = eixo_completo.merge(df, on=eixo_x_nome, how="left").fillna(0)
            except (ValueError, TypeError):
                pass
        
        # ======================================================================
        # CÓDIGO DE ORDENAÇÃO DE CATEGORIA (REINSERIDO AQUI)
        # ======================================================================
        if campo_grupo:
            sort_order = [eixo_x_nome, grupo_plotly]
            if grupo_plotly in self.CATEGORY_ORDERS:
                cat_dtype = CategoricalDtype(categories=self.CATEGORY_ORDERS[grupo_plotly], ordered=True)
                df[grupo_plotly] = df[grupo_plotly].astype(cat_dtype)
            df.sort_values(by=sort_order, inplace=True)
        else:
            df.sort_values(by=[eixo_x_nome], inplace=True)
        # ======================================================================

        # Constrói o título
        titulo_base = titulo_override if titulo_override is not None else mapeamento['titulo_base']
        titulo_final = f"{titulo_base} por {eixo_x_nome}"
        if agrupamento:
             titulo_final = f"{titulo_base} por {agrupamento.replace('_', ' ').capitalize()}"

        params = {"x": eixo_x_nome, "y": eixo_y_nome, "color": grupo_plotly, "title": titulo_final}
        return self._gerar_grafico(df, tipo_grafico, params, **kwargs)

    # ... (os métodos _gerar_grafico_direto e _gerar_grafico permanecem os mesmos) ...
    def _gerar_grafico_direto(self, tipo_entidade: str, tipo_grafico: str, filtros_selecionados: dict, titulo_override: str | None = None, **kwargs,):
        queryset, mapeamento, filtros_finais = self._get_base_queryset(tipo_entidade, filtros_selecionados)
        eixo_x_campo = mapeamento["eixo_x_campo"]
        eixo_x_nome = mapeamento["eixo_x_nome"]
        eixo_x_tipo = mapeamento.get("eixo_x_tipo", "categorico")
        eixo_y_campo = mapeamento.get("eixo_y_campo")
        eixo_y_nome = mapeamento.get("eixo_y_nome", "Valor")
        if not eixo_y_campo:
            raise KeyError(f"Mapeamento '{tipo_entidade}' precisa da chave 'eixo_y_campo'.")
        dados = queryset.values(eixo_x_campo, eixo_y_campo).order_by(eixo_x_campo)
        df = pd.DataFrame(list(dados))
        if df.empty:
            return "<p class='text-center text-muted mt-4'>Nenhum dado encontrado para os filtros selecionados.</p>"
        df.rename(columns={eixo_x_campo: eixo_x_nome, eixo_y_campo: eixo_y_nome}, inplace=True)
        if eixo_x_tipo == 'numerico_continuo':
            try:
                inicio = int(filtros_finais.get('ano_inicial', df[eixo_x_nome].min()))
                fim = int(filtros_finais.get('ano_final', df[eixo_x_nome].max()))
                eixo_completo = pd.DataFrame({eixo_x_nome: range(inicio, fim + 1)})
                df = eixo_completo.merge(df, on=eixo_x_nome, how="left")
            except (ValueError, TypeError):
                pass
        titulo_base = titulo_override if titulo_override is not None else mapeamento['titulo_base']
        titulo_final = f"{titulo_base} por {eixo_x_nome}"
        params = {"x": eixo_x_nome, "y": eixo_y_nome, "title": titulo_final}
        return self._gerar_grafico(df, tipo_grafico, params, **kwargs)

    def _gerar_grafico(
        self,
        df: pd.DataFrame,
        tipo_grafico: str,
        params: dict,
        pronto_para_plot: bool = True,
        **kwargs
    ):
        """
        Gera um gráfico Plotly com base nas configurações e retorna
        o HTML ou o objeto bruto, dependendo da flag 'pronto_para_plot'.

        Parâmetros:
        -----------
        df : pd.DataFrame
            Dados de entrada.
        tipo_grafico : str
            Tipo de gráfico (ex: 'barra', 'linha').
        params : dict
            Parâmetros específicos do gráfico (x, y, color, title, etc.).
        pronto_para_plot : bool
            Se True, retorna o HTML pronto para renderização.
            Se False, retorna o objeto Plotly Figure para personalização.
        """

        func = self.PLOT_FUNCS.get(tipo_grafico)
        if not func:
            raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não suportado.")

        # Combina configurações padrão e parâmetros passados
        plot_args = self.PLOT_CONFIGS.get(tipo_grafico, {}).copy()
        plot_args.update({k: v for k, v in params.items() if v is not None})

        # Cria a figura
        fig = func(df, **plot_args)

        # Layout padrão
        fig.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=60, b=40),
            title_text=params.get("title", ""),
            xaxis_title=params.get("x", ""),
            yaxis_title=params.get("y", ""),
            legend_title_text=params.get("color", ""),
            xaxis=dict(type="category"),
        )

        # Ajuste específico para gráficos de barra
        if tipo_grafico == "barra":
            fig.update_traces(textposition="outside")

        # Se o gráfico for para renderização imediata, converte para HTML
        if pronto_para_plot:
            return fig.to_html(
                full_html=False,
                include_plotlyjs="cdn",
                config={"responsive": True},
            )

        # Caso contrário, retorna o objeto Plotly para customizações
        return fig
