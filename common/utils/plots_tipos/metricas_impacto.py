import pandas as pd
from .xy_base import XYBaseStrategy
from common.utils.plot_helpers import calculate_h_index 

class MetricasImpactoStrategy(XYBaseStrategy):
    """
    Estratégia dedicada a cálculos bibliométricos complexos (Média, Acumulado, H-Index)
    que exigem processamento em memória via Pandas.
    """

    def _get_raw_dataframe(self) -> pd.DataFrame:
            queryset, _, _ = self.plotter._get_base_queryset(self.mapeamento['nome_plot'], self.filtros)

            # --- 1. SETUP DE VARIÁVEIS ---
            eixo_x = self.mapeamento["eixo_x_campo"]
            campo_valor = self.mapeamento["campo_valor"] 
            agrupamento = self.filtros.get("agrupamento")
            campo_grupo = self.mapeamento.get("agrupamentos", {}).get(agrupamento)

            # Monta a lista de colunas sem IFs usando concatenação de listas
            campos_busca = [eixo_x, campo_valor] + ([campo_grupo] if campo_grupo else [])
            df = pd.DataFrame(list(queryset.values(*campos_busca)))

            if df.empty:
                return pd.DataFrame()

            grupo_cols = [eixo_x] + ([campo_grupo] if campo_grupo else [])
            metrica = self.filtros.get('metrica', 'total_citacoes')

            # ==========================================================
            # 2. CÁLCULOS
            # ==========================================================
            # Em vez de um bloco if/elif gigante, mapeamos a métrica diretamente 
            # para a função correspondente do Pandas (Lambdas avaliadas preguiçosamente).

            operacoes = {
                'total_citacoes': lambda: df.groupby(grupo_cols)[campo_valor].sum(),
                'media': lambda: df.groupby(grupo_cols)[campo_valor].mean().round(2),
                'hindex': lambda: df.groupby(grupo_cols)[campo_valor].apply(calculate_h_index),
                'total_citacoes_acumuladas': lambda: df.groupby(grupo_cols)[campo_valor].sum().groupby(level=campo_grupo).cumsum() if campo_grupo else df.groupby(grupo_cols)[campo_valor].sum().cumsum()
            }

            # Aciona a função escolhida (ou a soma por padrão) e limpa o índice
            df_final = operacoes.get(metrica, operacoes['total_citacoes'])().reset_index()


            # ==========================================================
            # 3. TRADUÇÃO E RENOMEAÇÃO (Puramente Declarativo e Vetorizado)
            # ==========================================================
            labels_dict = self.mapeamento.get('labels_customizadas', {})

            if campo_grupo and labels_dict:
                # Adeus Lambda e IsInstance!
                # Convertendo os dados da coluna para string, o Pandas mapeia os booleanos ("True") 
                # diretamente para o dicionário numa velocidade absurda usando C++ por baixo dos panos.
                df_final[campo_grupo] = df_final[campo_grupo].astype(str).replace(labels_dict)


            # 1. Pega os dicionários de nomes e a métrica atual
            nomes_dinamicos = self.mapeamento.get("nomes_das_metricas", {})
            metrica_atual = self.filtros.get('metrica', 'total_citacoes')
        
            # 2. Tenta pegar o nome dinâmico. Se não achar, usa o eixo_y_nome padrão.
            nome_eixo_y = nomes_dinamicos.get(metrica_atual, self.mapeamento.get("eixo_y_nome", "Valor"))

            # 3. Prepara o dicionário de renomeação de X e Y
            colunas_renomear = {
                eixo_x: self.mapeamento["eixo_x_nome"], 
                campo_valor: nome_eixo_y  # <-- Injeta o nome dinâmico aqui!
            }

            if campo_grupo:
                # Anexa o nome bonito da legenda ao dicionário de renomeação
                colunas_renomear[campo_grupo] = labels_dict.get(agrupamento, agrupamento.replace('_', ' ').capitalize())

            # Aplica toda a renomeação de uma só vez
            return df_final.rename(columns=colunas_renomear)

    def generate_plot(self, df: pd.DataFrame, tipo_grafico: str, **kwargs) -> str:
            """
            Intercepta a renderização para avisar a classe pai (XYBase) 
            qual é o nome dinâmico correto do Eixo Y.
            """
            # 1. Descobre qual nome dinâmico foi usado no DataFrame
            nomes_dinamicos = self.mapeamento.get("nomes_das_metricas", {})
            metrica_atual = self.filtros.get('metrica', 'total_citacoes')
            nome_eixo_y = nomes_dinamicos.get(metrica_atual, self.mapeamento.get("eixo_y_nome", "Valor"))
            
            # 2. Injeta o aviso (override) nos kwargs
            kwargs["eixo_y_override"] = nome_eixo_y
            
            # 3. Chama o garçom (a classe pai XYBaseStrategy) passando o recado!
            return super().generate_plot(df, tipo_grafico, **kwargs)