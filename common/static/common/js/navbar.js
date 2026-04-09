// Arquivo: common/static/common/js/navbar.js

document.addEventListener("DOMContentLoaded", function() {
    // Só aplica o comportamento de hover em telas de desktop (evita bugs no celular)
    if (window.innerWidth >= 992) {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const offCanvasEl = document.getElementById('offCanvasMenu');
        
        // Verifica se os elementos existem na página antes de tentar rodar o script
        if (navbarToggler && offCanvasEl) {
            // Inicializa a instância do Offcanvas do Bootstrap
            const bsOffcanvas = new bootstrap.Offcanvas(offCanvasEl);

            // Abre o menu lateral inteiro quando o mouse entra no botão sanduíche
            navbarToggler.addEventListener('mouseenter', function() {
                bsOffcanvas.show();
            });

            // Fecha o menu lateral inteiro quando o mouse sai de dentro do Offcanvas
            offCanvasEl.addEventListener('mouseleave', function() {
                bsOffcanvas.hide();
            });
        }
    }
});