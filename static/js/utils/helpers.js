/**
 * ========================================
 * HELPER FUNCTIONS - Jornal do Commercio
 * ========================================
 */

/**
 * Formata uma data para o formato brasileiro
 * @param {Date|string} date - Data a ser formatada
 * @returns {string} Data formatada (dd/mm/yyyy)
 */
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

/**
 * Formata uma data e hora para o formato brasileiro
 * @param {Date|string} date - Data a ser formatada
 * @returns {string} Data e hora formatadas (dd/mm/yyyy HH:mm)
 */
function formatDateTime(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

/**
 * Obtém a hora atual formatada
 * @returns {string} Hora atual (HH:mm:ss)
 */
function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

/**
 * Trunca um texto para um número específico de palavras
 * @param {string} text - Texto a ser truncado
 * @param {number} maxWords - Número máximo de palavras
 * @returns {string} Texto truncado
 */
function truncateWords(text, maxWords) {
    const words = text.split(' ');
    if (words.length <= maxWords) return text;
    return words.slice(0, maxWords).join(' ') + '...';
}

/**
 * Debounce function - Limita a frequência de execução de uma função
 * @param {Function} func - Função a ser executada
 * @param {number} wait - Tempo de espera em milissegundos
 * @returns {Function} Função com debounce aplicado
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copia texto para a área de transferência
 * @param {string} text - Texto a ser copiado
 * @returns {Promise} Promise que resolve quando o texto é copiado
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Erro ao copiar texto:', err);
        return false;
    }
}

/**
 * Cria um elemento DOM a partir de HTML string
 * @param {string} html - String HTML
 * @returns {Element} Elemento DOM
 */
function createElementFromHTML(html) {
    const div = document.createElement('div');
    div.innerHTML = html.trim();
    return div.firstChild;
}

/**
 * Verifica se um elemento está visível na viewport
 * @param {Element} element - Elemento a ser verificado
 * @returns {boolean} True se o elemento está visível
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Scroll suave para um elemento
 * @param {string|Element} target - Seletor CSS ou elemento
 * @param {number} offset - Deslocamento em pixels (opcional)
 */
function smoothScrollTo(target, offset = 0) {
    const element = typeof target === 'string'
        ? document.querySelector(target)
        : target;

    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

/**
 * Mostra uma mensagem de alerta temporária
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo do alerta (success, error, warning, info)
 * @param {number} duration - Duração em milissegundos
 */
function showAlert(message, type = 'info', duration = 3000) {
    const alert = createElementFromHTML(`
        <div class="alert alert-${type}" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
        </div>
    `);

    document.body.appendChild(alert);

    setTimeout(() => {
        alert.style.transition = 'opacity 0.3s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, duration);
}

/**
 * Valida um email
 * @param {string} email - Email a ser validado
 * @returns {boolean} True se o email é válido
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Formata um número com separadores de milhares
 * @param {number} num - Número a ser formatado
 * @returns {string} Número formatado
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
