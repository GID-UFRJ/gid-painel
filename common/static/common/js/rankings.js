function initRankingToggle() {
    // 1. Encontra todos os controles de ranking na página
    const rankingControls = document.querySelectorAll('.js-ranking-control');

    rankingControls.forEach(selectElement => {
        // 2. Obtém o seletor alvo do atributo data
        const targetSelector = selectElement.getAttribute('data-target-ods');
        if (!targetSelector) return; // Ignora se não houver alvo definido

        const targetDiv = document.querySelector(targetSelector);
        if (!targetDiv) return; // Ignora se o alvo não existe na DOM

        function toggleOdsVisibility() {
            const selectedValue = selectElement.value.toUpperCase();
            
            // Lógica: Se for 'THE IMPACT', mostra. Senão, esconde.
            if (selectedValue.includes("THE IMPACT")) {
                targetDiv.style.display = 'block';
            } else {
                targetDiv.style.display = 'none';
                
                // Opcional: Resetar o valor do ODS quando escondido
                const selectOds = targetDiv.querySelector('select');
                if (selectOds) selectOds.value = ""; 
            }
        }

        // 3. Adiciona o listener de evento
        selectElement.addEventListener('change', toggleOdsVisibility);
        
        // 4. Executa imediatamente para definir o estado inicial (importante para lazy-loading)
        toggleOdsVisibility();
    });
}

// Garante que o script roda assim que o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initRankingToggle);