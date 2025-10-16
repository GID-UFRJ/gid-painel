# em sucupira/tests.py

from django.test import TestCase
from .models import Programa, Discente, Ano # Importe os modelos que você vai usar
from .utils.plots import PlotsPpgDetalhe

class PlotDataGenerationTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """
        Esta função é executada uma vez para configurar o banco de dados de teste.
        Criamos um cenário simples e conhecido.
        """
        # Criamos dois programas para garantir que nosso filtro funciona
        prog1 = Programa.objects.create(id=1, cd_programa="PROG01")
        prog2 = Programa.objects.create(id=2, cd_programa="PROG02")

        # Criamos dois anos
        ano2020 = Ano.objects.create(ano_valor=2020)
        ano2021 = Ano.objects.create(ano_valor=2021)

        # Criamos discentes de teste
        # Programa 1: 2 discentes em 2020, 1 em 2021
        Discente.objects.create(programa=prog1, ano=ano2020)
        Discente.objects.create(programa=prog1, ano=ano2020)
        Discente.objects.create(programa=prog1, ano=ano2021)

        # Programa 2: 3 discentes em 2020
        Discente.objects.create(programa=prog2, ano=ano2020)
        Discente.objects.create(programa=prog2, ano=ano2020)
        Discente.objects.create(programa=prog2, ano=ano2020)

    def test_ppg_discentes_por_ano_dataframe(self):
        """
        Testa se o DataFrame para o gráfico de discentes por ano é gerado corretamente
        para um programa específico.
        """
        # ETAPA 1: SETUP
        # Instancia o plotter para o Programa 1
        plotter = PlotsPpgDetalhe(programa_id=1)
        
        # Define os filtros que um usuário aplicaria
        filtros = {
            'programa_id': 1,
            'ano_inicial': 2020,
            'ano_final': 2021,
        }

        # ETAPA 2: AÇÃO
        # Chama o método que queremos testar
        df = plotter.get_dataframe_for_plot('ppg_discentes_por_ano', filtros)

        # ETAPA 3: VERIFICAÇÃO (ASSERT)
        # Verificamos se o DataFrame tem as propriedades que esperamos

        # 1. Ele deve ter 2 linhas (uma para 2020, uma para 2021)
        self.assertEqual(len(df), 2)
        
        # 2. As colunas devem ter os nomes corretos
        self.assertListEqual(list(df.columns), ['Ano', 'Número de Discentes'])

        # 3. Verificamos os valores específicos
        # A linha para 2020 deve ter 2 discentes
        linha_2020 = df[df['Ano'] == 2020]
        self.assertEqual(linha_2020['Número de Discentes'].iloc[0], 2)

        # A linha para 2021 deve ter 1 discente
        linha_2021 = df[df['Ano'] == 2021]
        self.assertEqual(linha_2021['Número de Discentes'].iloc[0], 1)

        print("\n✅ Teste de dados para 'ppg_discentes_por_ano' passou com sucesso!")