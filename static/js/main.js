/**
 * ========================================
 * MAIN JAVASCRIPT - Jornal do Commercio
 * ========================================
 */

// Inicialização principal
document.addEventListener('DOMContentLoaded', function() {
    // Atualizar relógio no info bar
    updateClock();
    setInterval(updateClock, 1000);

    // Lazy loading de imagens
    setupLazyLoading();

    // Smooth scroll para links âncora
    setupSmoothScroll();

    // Botão "voltar ao topo"
    setupBackToTop();

    // Fechar mensagens automaticamente
    setupAutoCloseMessages();

    // Analytics de cliques (opcional)
    setupAnalytics();
});

/**
 * Atualiza o relógio no info bar
 */
function updateClock() {
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        clockElement.textContent = getCurrentTime();
    }
}

/**
 * Configura lazy loading para imagens
 */
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Configura smooth scroll para links âncora
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    smoothScrollTo(target, 100);
                }
            }
        });
    });
}

/**
 * Configura botão "voltar ao topo"
 */
function setupBackToTop() {
    // Criar botão se não existir
    let backToTopBtn = document.getElementById('back-to-top');

    if (!backToTopBtn) {
        backToTopBtn = document.createElement('button');
        backToTopBtn.id = 'back-to-top';
        backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background-color: var(--secondary-color, #e94560);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(backToTopBtn);
    }

    // Mostrar/ocultar botão baseado no scroll
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'flex';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // Ação do clique
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Hover effect
    backToTopBtn.addEventListener('mouseenter', () => {
        backToTopBtn.style.transform = 'translateY(-5px)';
    });

    backToTopBtn.addEventListener('mouseleave', () => {
        backToTopBtn.style.transform = 'translateY(0)';
    });
}

/**
 * Fecha mensagens automaticamente após alguns segundos
 */
function setupAutoCloseMessages() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';

            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);

        // Permitir fechar manualmente
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: 5px;
            right: 10px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: inherit;
            opacity: 0.7;
        `;

        closeBtn.addEventListener('click', () => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });

        if (alert.style.position !== 'absolute') {
            alert.style.position = 'relative';
        }
        alert.appendChild(closeBtn);
    });
}

/**
 * Configura analytics básico de cliques
 */
function setupAnalytics() {
    // Rastrear cliques em notícias
    document.querySelectorAll('.news-card, .hero-item').forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('.news-title, .hero-title');
            if (title) {
                console.log('Clique em notícia:', title.textContent.trim());
                // Aqui você pode enviar para Google Analytics, etc.
            }
        });
    });

    // Rastrear buscas
    const searchForm = document.querySelector('.search-bar form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = this.querySelector('input').value;
            console.log('Busca realizada:', query);
            // Aqui você pode enviar para Google Analytics, etc.
        });
    }

    // Rastrear compartilhamentos
    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const platform = this.classList.contains('facebook') ? 'Facebook' :
                           this.classList.contains('twitter') ? 'Twitter' :
                           this.classList.contains('whatsapp') ? 'WhatsApp' : 'Outro';
            console.log('Compartilhado via:', platform);
            // Aqui você pode enviar para Google Analytics, etc.
        });
    });
}

/**
 * Função auxiliar para verificar se o usuário está em um dispositivo móvel
 */
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Função para copiar link da notícia
 */
function copyNewsLink() {
    const url = window.location.href;
    copyToClipboard(url).then(success => {
        if (success) {
            showAlert('Link copiado para a área de transferência!', 'success');
        } else {
            showAlert('Erro ao copiar link', 'error');
        }
    });
}

// Expor funções globalmente se necessário
window.copyNewsLink = copyNewsLink;
window.isMobile = isMobile;
