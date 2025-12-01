document.addEventListener('DOMContentLoaded', function() {
    // Buscador de desktop
    const searchInputDesktop = document.querySelector('#searchInput');
    const searchResultsDesktop = document.querySelector('#searchResults');
    const searchTypeInputDesktop = document.querySelector('#searchType'); // opcional

    if (searchInputDesktop && searchResultsDesktop) {
        let lastQueryDesktop = '';
        searchInputDesktop.addEventListener('input', function() {
            const query = searchInputDesktop.value.trim();
            const searchType = searchTypeInputDesktop ? searchTypeInputDesktop.value : 'all';

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
                            const imgSrc = result.image || '/theme_xtream/static/src/img/placeholder.png';
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

        document.addEventListener('click', function(e) {
            if (!searchResultsDesktop.contains(e.target) && e.target !== searchInputDesktop) {
                setTimeout(() => { searchResultsDesktop.style.display = 'none'; }, 150);
            }
        });
    }

    // Buscador de móvil
    const searchInputMobile = document.querySelector('#mobileSearchInput');
    const searchResultsMobile = document.querySelector('#mobileSearchResults');

    if (searchInputMobile && searchResultsMobile) {
        let lastQueryMobile = '';
        searchInputMobile.addEventListener('input', function() {
            const query = searchInputMobile.value.trim();
            if (query.length === 0) {
                searchResultsMobile.style.display = 'none';
                searchResultsMobile.innerHTML = '';
                return;
            }

            if (query === lastQueryMobile) return;
            lastQueryMobile = query;

            fetch(`/search_live?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsMobile.innerHTML = '';
                    if (data.results && data.results.length) {
                        searchResultsMobile.style.display = 'block';
                        data.results.slice(0, 7).forEach(result => {
                            const truncatedName = result.name.length > 30 ? result.name.substring(0, 30) + '...' : result.name;
                            const imgSrc = result.image || '/theme_xtream/static/src/img/placeholder.png';
                            const item = document.createElement('a');
                            item.className = 'dropdown-item d-flex align-items-center';
                            item.href = result.url || '#';
                            item.innerHTML = `
                                <img src="${imgSrc}" alt="${truncatedName}" style="width:32px;height:32px;object-fit:contain;margin-right:10px;"/>
                                <div style="overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">${truncatedName}</div>
                            `;
                            searchResultsMobile.appendChild(item);
                        });
                        const allResultsLink = document.createElement('a');
                        allResultsLink.className = 'dropdown-item text-center';
                        allResultsLink.href = `/subcategory?search=${encodeURIComponent(query)}`;
                        allResultsLink.textContent = 'Ver todos los resultados';
                        searchResultsMobile.appendChild(allResultsLink);
                    } else {
                        searchResultsMobile.style.display = 'none';
                    }
                })
                .catch(() => {
                    searchResultsMobile.style.display = 'none';
                });
        });

        document.addEventListener('click', function(e) {
            if (!searchResultsMobile.contains(e.target) && e.target !== searchInputMobile) {
                setTimeout(() => { searchResultsMobile.style.display = 'none'; }, 150);
            }
        });
    }
});