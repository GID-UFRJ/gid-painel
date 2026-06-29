// Arquivo: common/static/common/js/indice.js

document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll('.indice-link');
    const btnTopo = document.getElementById('btn-voltar-topo');
    let graficoAtivoId = null;

    if (links.length === 0) return;

    // --- 1. OBSERVADOR DE GRÁFICOS ---
    const options = {
        root: null,
        rootMargin: '-120px 0px -40% 0px', 
        threshold: 0.1 
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                graficoAtivoId = entry.target.id;
                atualizarDestaque();
            }
        });
    }, options);

    links.forEach(link => {
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) observer.observe(targetElement);
    });

    // --- 2. O JUIZ DE CORES ---
    function atualizarDestaque() {
        // ZONA 1: Se estivermos no topo (Destaque para o botão Topo)
        if (window.scrollY < 150) {
            
            links.forEach(l => {
                l.classList.remove('btn-primary');
                l.classList.add('btn-outline-primary');
            });
            
            if (btnTopo) {
                // AQUI FOI A MUDANÇA: Troca o contorno pelo cinza sólido (btn-secondary)
                btnTopo.classList.remove('btn-outline-secondary');
                btnTopo.classList.add('btn-secondary'); 
            }
        } 
        
        // ZONA 2: Rolou para baixo (Destaque para os gráficos)
        else if (graficoAtivoId) {
            
            if (btnTopo) {
                // AQUI TAMBÉM: Remove o cinza sólido e volta para o contorno vazado
                btnTopo.classList.remove('btn-secondary');
                btnTopo.classList.add('btn-outline-secondary');
            }
            
            links.forEach(l => {
                l.classList.remove('btn-primary');
                l.classList.add('btn-outline-primary');
            });
            
            const activeLink = document.querySelector(`.indice-link[href="#${graficoAtivoId}"]`);
            if (activeLink) {
                activeLink.classList.remove('btn-outline-primary');
                activeLink.classList.add('btn-primary');
            }
        }
    }

    window.addEventListener('scroll', atualizarDestaque);
    atualizarDestaque();
});