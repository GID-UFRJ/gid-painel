from django.shortcuts import render
from .scripts_graficos import Grafico_programa


def view_analise_ppg(request):
    g = Grafico_programa()

    return render(request, r'programa\relatorio_ppg.html', {
        'grafl1_1':g.graf_kpi_programa(),
        'grafl1_2':g.graf_kpi_programa_academicos(),
        'grafl1_3':g.graf_kpi_programa_profissionais(),

        'grafl2_1':g.programas_modalidade(),
        'grafl2_2':g.programas_nivel_academico(),
        'grafl2_3':g.programas_nivel_profissional(),

        'grafl3_1':g.programas_modalidade_plotly(),
    })


