// Arquivo: common/static/common/js/exibicao_condicional.js

function configurarExibicaoCondicional(seletorGatilho, idAlvo, valorGatilho) {
    const elementoGatilho = document.querySelector(seletorGatilho);
    const elementoAlvo = document.getElementById(idAlvo);

    // Segurança: se não encontrar os elementos na tela, encerra a função
    if (!elementoGatilho || !elementoAlvo) return;

    function alternarVisibilidade() {
        if (elementoGatilho.value === valorGatilho) {
            elementoAlvo.style.display = 'block';
        } else {
            elementoAlvo.style.display = 'none';
        }
    }

    // Executa imediatamente para garantir o estado inicial correto
    alternarVisibilidade();
    
    // Adiciona o listener para reagir às mudanças do usuário
    elementoGatilho.addEventListener('change', alternarVisibilidade);
}