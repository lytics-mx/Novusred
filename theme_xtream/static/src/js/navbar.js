document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('#searchInput') || document.querySelector('input[name="search"]');
    const searchResults = document.querySelector('#searchResults') || document.querySelector('.search-results-dropdown');
    const searchTypeInput = document.querySelector('#searchType'); // opcional

    if (searchInput && searchResults) {
        let lastQuery = '';
        searchInput.addEventListener('input', function() {
            const query = searchInput.value.trim();
            const searchType = searchTypeInput ? searchTypeInput.value : 'all';

            if (query.length === 0) {
                searchResults.style.display = 'none';
                searchResults.innerHTML = '';
                return;
            }

            if (query === lastQuery) return;
            lastQuery = query;

            if (searchType === 'all') {
                fetch(`/search_live?query=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    })
                    .then(data => {
                        searchResults.innerHTML = '';
                        if (data.results && data.results.length) {
                            searchResults.style.display = 'block';
                            data.results.slice(0, 7).forEach(result => {
                                const truncatedName = result.name.length > 80 ? result.name.substring(0, 80) + '...' : result.name;
                                const imgSrc = result.image || '/theme_xtream/static/src/img/placeholder.png'; // Usar placeholder si no hay imagen
                                const item = document.createElement('a');
                                item.className = 'dropdown-item d-flex align-items-center';
                                item.href = result.url || '#';
                                item.innerHTML = `
                                    <img src="${imgSrc}" alt="${truncatedName}" style="width:40px;height:40px;object-fit:contain;margin-right:10px;"/>
                                    <div style="overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">${truncatedName}</div>
                                `;
                                searchResults.appendChild(item);
                            });
                            const allResultsLink = document.createElement('a');
                            allResultsLink.className = 'dropdown-item text-center';
                            allResultsLink.href = `/subcategory?search=${encodeURIComponent(query)}`;
                            allResultsLink.textContent = 'Ver todos los resultados';
                            searchResults.appendChild(allResultsLink);
                        } else {
                            searchResults.style.display = 'none';
                        }
                    })
                    .catch(err => {
                        console.error('Error fetching search_live:', err);
                        searchResults.style.display = 'none';
                    });
            } else {
                searchResults.style.display = 'none';
            }
        });

        document.addEventListener('click', function(e) {
            if (!searchResults.contains(e.target) && e.target !== searchInput) {
                setTimeout(() => { searchResults.style.display = 'none'; }, 150);
            }
        });
    }
});        