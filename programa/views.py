from django.shortcuts import render
from .scripts_graficos import Grafico_programa


def view_analise_ppg(request):
    g = Grafico_programa()

    return render(request, r'programa/relatorio_ppg.html', {
        'grafl1_1':g.graf_kpi_programa(),
        'grafl1_2':g.graf_kpi_programa_academicos(),
        'grafl1_3':g.graf_kpi_programa_profissionais(),

        'grafl2_1':g.programas_modalidade(),
        'grafl2_2':g.programas_modalidade(),
        'grafl2_3':g.programas_modalidade(),

        'grafl3_1':g.programas_modalidade_plotly(),
        'grafl3_2':g.programas_centro_plotly(),
        'grafl3_3':g.programas_rede_plotly(),
        'grafl3_4':g.programasAcademicos_conceito_plotly(),
        'grafl3_5':g.programasProfissionais_conceito_plotly(),
        'grafl3_6':g.programas_unidade_plotly(),
        'grafl3_7':g.programas_areaAvaliacao_plotly(),
    })


