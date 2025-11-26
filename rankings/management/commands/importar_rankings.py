import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from rankings.models import (
    RankingTipo, Ranking, Escopo, ODS, RankingEntrada
)


class Command(BaseCommand):
    help = "Importa a tabela de staging e popula as tabelas normalizadas usando o ORM do Django."

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            type=str,
            required=True,
            help="Caminho para o arquivo CSV ou XLSX contendo a tabela de staging."
        )

    def handle(self, *args, **options):
        caminho = options["arquivo"]

        # Carregar arquivo
        if caminho.endswith(".csv"):
            df = pd.read_csv(caminho)
        else:
            df = pd.read_excel(caminho)

        # Padronizar nome das colunas
        df.columns = [
            c.strip().lower().replace(" ", "_")
            for c in df.columns
        ]

        df = df.rename(columns={
            "posição_mínima": "posicao_minima",
            "posição_máxima": "posicao_maxima",
            "year": "ano"
        })

        # Criar tipos de ranking
        for tipo in df["tipo"].dropna().unique():
            RankingTipo.objects.get_or_create(nome=tipo)

        with transaction.atomic():

            # Criar rankings
            for _, row in df[["ranking", "tipo"]].drop_duplicates().iterrows():
                tipo_obj = RankingTipo.objects.get(nome=row["tipo"])
                Ranking.objects.get_or_create(
                    nome=row["ranking"],
                    tipo=tipo_obj
                )

            # Criar escopos (somente quando não é ODS)
            for esc in df.loc[df["ods"].isna(), "escopo"].dropna().unique():
                Escopo.objects.get_or_create(nome=esc)

            # Criar ODS
            for ods in df["ods"].dropna().unique():
                ODS.objects.get_or_create(codigo=ods)

            # Criar entradas
            for _, row in df.iterrows():
                tipo_obj = RankingTipo.objects.get(nome=row["tipo"])
                ranking_obj = Ranking.objects.get(
                    nome=row["ranking"],
                    tipo=tipo_obj
                )

                if pd.isna(row["ods"]):
                    ods_obj = None
                    escopo_obj, _ = Escopo.objects.get_or_create(nome=row["escopo"])
                else:
                    escopo_obj = None
                    ods_obj, _ = ODS.objects.get_or_create(codigo=row["ods"])

                RankingEntrada.objects.create(
                    ranking=ranking_obj,
                    escopo=escopo_obj,
                    ods=ods_obj,
                    ano=int(row["ano"]),
                    posicao_minima=int(row["posicao_minima"]),
                    posicao_maxima=int(row["posicao_maxima"]),
                )

        self.stdout.write(self.style.SUCCESS("Importação concluída com sucesso!"))
