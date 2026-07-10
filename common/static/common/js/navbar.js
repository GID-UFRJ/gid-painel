// Arquivo: common/static/common/js/navbar.js
document.addEventListener("DOMContentLoaded", function() {
    // Só aplica o comportamento de hover em desktops
    if (window.innerWidth >= 992) {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const offCanvasEl = document.getElementById('offCanvasMenu');

        if (navbarToggler && offCanvasEl) {
            const bsOffcanvas = new bootstrap.Offcanvas(offCanvasEl);
            let hideTimeout;
            let menuContextoAberto = false;

            function agendarFechamento() {
                clearTimeout(hideTimeout);
                hideTimeout = setTimeout(() => {
                    // Só fecha se, de fato, o mouse não estiver mais sobre o offcanvas
                    // e nenhum menu de contexto estiver aberto
                    if (!menuContextoAberto && !offCanvasEl.matches(':hover')) {
                        bsOffcanvas.hide();
                    }
                }, 250);
            }

            // 1. Detecta a ABERTURA do menu de contexto em QUALQUER lugar dentro
            //    do offcanvas (delegação: cobre parents e sub-items automaticamente)
            offCanvasEl.addEventListener('contextmenu', function() {
                menuContextoAberto = true;
                clearTimeout(hideTimeout);
            });

            // 2. O menu de contexto nativo do SO tira o foco da janela.
            //    Isso é muito mais confiável entre navegadores do que rastrear
            //    manualmente mousedown/mouseup do botão direito.
            window.addEventListener('blur', function() {
                if (menuContextoAberto) {
                    clearTimeout(hideTimeout);
                }
            });

            // 3. Quando o foco volta (menu fechado via Esc, clique fora, ou
            //    seleção de uma opção do menu), reavaliamos o estado real do
            //    mouse antes de decidir se fecha ou não.
            window.addEventListener('focus', function() {
                setTimeout(() => {
                    menuContextoAberto = false;
                    if (!offCanvasEl.matches(':hover')) {
                        agendarFechamento();
                    }
                }, 50);
            });

            // 4. Abre o menu ao passar o mouse
            navbarToggler.addEventListener('mouseenter', function() {
                clearTimeout(hideTimeout);
                bsOffcanvas.show();
            });

            // Evita fechamento se o mouse estiver transitando dentro do menu
            offCanvasEl.addEventListener('mouseenter', function() {
                clearTimeout(hideTimeout);
            });

            // 5. Tenta fechar o menu ao sair
            offCanvasEl.addEventListener('mouseleave', function() {
                if (menuContextoAberto) return;
                agendarFechamento();
            });
        }
    }
});