/**
 * ========================================
 * SEARCH COMPONENT - Jornal do Commercio
 * ========================================
 */

class Search {
    constructor() {
        this.searchForm = document.querySelector('.search-bar form');
        this.searchInput = document.querySelector('.search-bar input');
        this.init();
    }

    init() {
        if (!this.searchForm || !this.searchInput) return;

        this.setupSearch();
        this.setupAutocomplete();
    }

    setupSearch() {
        this.searchForm.addEventListener('submit', (e) => {
            const query = this.searchInput.value.trim();

            if (!query) {
                e.preventDefault();
                this.showError('Digite algo para buscar');
                return;
            }

            if (query.length < 3) {
                e.preventDefault();
                this.showError('Digite pelo menos 3 caracteres');
                return;
            }
        });
    }

    setupAutocomplete() {
        // Implementar autocomplete no futuro se necessário
        // Por enquanto, apenas debounce para evitar muitas requisições

        let timeout = null;

        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);

            timeout = setTimeout(() => {
                const query = e.target.value.trim();
                if (query.length >= 3) {
                    // Aqui pode implementar busca em tempo real
                    console.log('Buscar:', query);
                }
            }, 500);
        });
    }

    showError(message) {
        if (typeof showAlert === 'function') {
            showAlert(message, 'warning', 2000);
        } else {
            alert(message);
        }
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new Search());
} else {
    new Search();
}
