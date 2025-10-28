/**
 * ========================================
 * MENU COMPONENT - Jornal do Commercio
 * ========================================
 */

class Menu {
    constructor() {
        this.mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        this.categoryList = document.querySelector('.category-list');
        this.dropdown = document.querySelector('.dropdown');
        this.init();
    }

    init() {
        if (this.mobileMenuToggle) {
            this.setupMobileMenu();
        }

        if (this.dropdown) {
            this.setupDropdown();
        }

        this.setupStickyHeader();
    }

    setupMobileMenu() {
        this.mobileMenuToggle.addEventListener('click', () => {
            this.categoryList.classList.toggle('active');
        });

        // Fechar menu ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.category-bar') && !e.target.closest('.mobile-menu-toggle')) {
                this.categoryList.classList.remove('active');
            }
        });
    }

    setupDropdown() {
        const dropdownToggle = this.dropdown.querySelector('.dropdown-toggle');
        const dropdownMenu = this.dropdown.querySelector('.dropdown-menu');

        if (dropdownToggle && dropdownMenu) {
            dropdownToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            });

            // Fechar dropdown ao clicar fora
            document.addEventListener('click', () => {
                dropdownMenu.classList.remove('show');
            });
        }
    }

    setupStickyHeader() {
        const header = document.querySelector('.site-header');
        const categoryBar = document.querySelector('.category-bar');

        if (header && categoryBar) {
            let lastScroll = 0;

            window.addEventListener('scroll', () => {
                const currentScroll = window.pageYOffset;

                if (currentScroll > 100) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }

                lastScroll = currentScroll;
            });
        }
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new Menu());
} else {
    new Menu();
}
