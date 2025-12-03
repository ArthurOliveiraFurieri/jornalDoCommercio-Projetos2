// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Menu mobile (se necessário no futuro)
    initMobileMenu();
    
    // Busca em tempo real (opcional)
    initSearch();
    
    // Animações suaves
    initAnimations();
});

function initMobileMenu() {
    // Implementação futura para menu mobile
    console.log('Mobile menu initialized');
}

function initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            // Implementar busca em tempo real se necessário
        });
    }
}

function initAnimations() {
    // Animações de entrada para cards de notícias
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observar cards de notícias
    document.querySelectorAll('.news-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Função para compartilhar notícias
function shareNews(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        });
    } else {
        // Fallback para copiar link
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copiado para a área de transferência!');
        });
    }
}