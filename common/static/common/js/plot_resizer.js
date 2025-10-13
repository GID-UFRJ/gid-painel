/**
 * Este script lida com o redimensionamento de gráficos Plotly em três cenários:
 * 1. No carregamento inicial da página.
 * 2. Quando uma aba do Bootstrap é trocada.
 * 3. Após uma atualização de conteúdo feita pelo HTMX.
 */
(() => {
    'use strict';

    /**
     * Função reutilizável para redimensionar todos os gráficos Plotly dentro de um elemento contêiner.
     * @param {HTMLElement} container - O elemento a ser verificado (ex: um painel de aba).
     */
    const resizePlotsInContainer = (container) => {
        if (!container) return; // Sai silenciosamente se o contêiner não for encontrado.

        const plots = container.querySelectorAll('.js-plotly-plot');
        plots.forEach(graphDiv => {
            try {
                if (typeof Plotly !== 'undefined') {
                    Plotly.Plots.resize(graphDiv);
                }
            } catch (e) { /* Ignora erros */ }
        });
    };

    // Cenário 1: Redimensionamento no carregamento inicial da página.
    // O evento 'load' espera que tudo (imagens, scripts do Plotly, etc.) seja carregado.
    window.addEventListener('load', () => {
        const activePaneOnLoad = document.querySelector('.tab-pane.active');
        resizePlotsInContainer(activePaneOnLoad);
    });

    // Cenário 2: Redimensionamento na troca de abas do Bootstrap.
    document.addEventListener('shown.bs.tab', (event) => {
        const paneId = event.target.getAttribute('data-bs-target');
        if (paneId) {
            const newlyShownPane = document.querySelector(paneId);
            resizePlotsInContainer(newlyShownPane);
        }
    });

    // Cenário 3: Redimensionamento após uma atualização do HTMX.
    document.body.addEventListener('htmx:afterSwap', () => {
        // Dá um pequeno atraso para garantir que o script do novo Plotly já executou.
        setTimeout(() => {
            const activePane = document.querySelector('.tab-pane.active');
            resizePlotsInContainer(activePane);
        }, 100);
    });

})();