document.addEventListener('DOMContentLoaded', function() {
    const searchInputDesktop = document.querySelector('#searchInput');
    const searchResultsDesktop = document.querySelector('#searchResults');

    if (searchInputDesktop && searchResultsDesktop) {
        let lastQueryDesktop = '';
        searchInputDesktop.addEventListener('input', function() {
            const query = searchInputDesktop.value.trim();
            if (query.length === 0) {
                searchResultsDesktop.style.display = 'none';
                searchResultsDesktop.innerHTML = '';
                return;
            }

            if (query === lastQueryDesktop) return;
            lastQueryDesktop = query;

            fetch(`/search_live?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsDesktop.innerHTML = '';
                    if (data.results && data.results.length) {
                        searchResultsDesktop.style.display = 'block';
                        data.results.slice(0, 7).forEach(result => {
                            const truncatedName = result.name.length > 80 ? result.name.substring(0, 80) + '...' : result.name;
                            const imgSrc = result.image || '/theme_xtream/static/src/img/placeholder.png'; // Placeholder si no hay imagen
                            const item = document.createElement('a');
                            item.className = 'dropdown-item d-flex align-items-center';
                            item.href = result.url || '#';
                            item.innerHTML = `
                                <img src="${imgSrc}" alt="${truncatedName}" style="width:40px;height:40px;object-fit:contain;margin-right:10px;"/>
                                <div style="overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">${truncatedName}</div>
                            `;
                            searchResultsDesktop.appendChild(item);
                        });
                        const allResultsLink = document.createElement('a');
                        allResultsLink.className = 'dropdown-item text-center';
                        allResultsLink.href = `/subcategory?search=${encodeURIComponent(query)}`;
                        allResultsLink.textContent = 'Ver todos los resultados';
                        searchResultsDesktop.appendChild(allResultsLink);
                    } else {
                        searchResultsDesktop.style.display = 'none';
                    }
                })
                .catch(() => {
                    searchResultsDesktop.style.display = 'none';
                });
        });
    }
});