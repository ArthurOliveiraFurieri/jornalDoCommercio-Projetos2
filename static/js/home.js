// Função para a barra de pesquisa
document.getElementById('search-form').addEventListener('submit', function(e) {
    e.preventDefault(); 
    const searchTerm = document.getElementById('search-input').value.trim();

    if (searchTerm) {
        alert(`Buscando por: "${searchTerm}"\n\nEsta funcionalidade pode ser integrada com seu backend Django.`);
    } else {
        alert('Por favor, digite um termo para buscar.');
    }
});