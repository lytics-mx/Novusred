                                    // Actualiza el placeholder según el tipo de búsqueda seleccionado
                                    const searchType = document.getElementById('searchType');
                                    const searchInput = document.getElementById('searchInputDesktop');
                                    if (searchType && searchInput) {
                                        function updatePlaceholder() {
                                            if (searchInput.value.trim().length > 0) return; // No cambiar si hay texto
                                            if (searchType.value === 'all') {
                                                searchInput.placeholder = 'Buscar productos, marcas o categorías...';
                                            } else if (searchType.value === 'brand') {
                                                searchInput.placeholder = 'Buscar marca...';
                                            } else if (searchType.value === 'category') {
                                                searchInput.placeholder = 'Buscar categoría...';
                                            } else if (searchType.value === 'model') {
                                                searchInput.placeholder = 'Buscar modelo...';
                                            }
                                        }
                                        searchType.addEventListener('change', updatePlaceholder);
                                        searchInput.addEventListener('input', updatePlaceholder);
                                        updatePlaceholder();
                                    }
                                    // ...existing code...
                                    (function(){
                                        function initDesktopSearch() {
                                            var desktopNav = document.querySelector('.custom-navbar nav.navbar.d-lg-block');
                                            if (!desktopNav) return;

                                            var searchInput = desktopNav.querySelector('#searchInputDesktop');
                                            var searchResults = desktopNav.querySelector('#searchResultsDesktop');
                                            var searchType = desktopNav.querySelector('#searchType')
                                            if (!searchInput || !searchResults || !searchType) return;

                                            var lastDesktopQuery = '';
                                            var lastDesktopType = searchType.value;

                                            searchType.addEventListener('change', function() {
                                                searchResults.style.display = 'none';
                                                searchResults.innerHTML = '';
                                                lastDesktopType = searchType.value;
                                            });

                                            searchInput.addEventListener('input', function() {
                                                var query = searchInput.value.trim();
                                                var type = searchType.value;
                                                if (query.length === 0) {
                                                    searchResults.style.display = 'none';
                                                    searchResults.innerHTML = '';
                                                    lastDesktopQuery = '';
                                                    return;
                                                }
                                                if (query === lastDesktopQuery && type === lastDesktopType) return;
                                                lastDesktopQuery = query;
                                                lastDesktopType = type;

                                                // Enviar el tipo de búsqueda al backend
                                                fetch('/search_live?query=' + encodeURIComponent(query) + '&type=' + encodeURIComponent(type))
                                                    .then(function(response){ return response.json(); })
                                                    .then(function(data){
                                                        searchResults.innerHTML = '';
                                                        if ((type === 'category' || type === 'brand') && data.results && data.results.length) {
                                                            searchResults.style.display = 'block';
                                                            data.results.slice(0, 7).forEach(function(result){
                                                                var name = result.name || '';
                                                                var item = document.createElement('a');
                                                                item.className = 'dropdown-item';
                                                                item.href = result.url;
                                                                item.title = name || '';
                                                                item.textContent = name;
                                                                searchResults.appendChild(item);
                                                            });
                                                            var allResultsLink = document.createElement('a');
                                                            allResultsLink.className = 'dropdown-item text-center';
                                                            if (type === 'category') {
                                                                allResultsLink.href = '/category_search?search=' + encodeURIComponent(query);
                                                            } else if (type === 'brand') {
                                                                allResultsLink.href = '/brand_search_redirect?search=' + encodeURIComponent(query);
                                                            }
                                                            allResultsLink.textContent = 'Ver todos los resultados';
                                                            allResultsLink.style.fontSize = '15px';
                                                            allResultsLink.style.padding = '8px 0';
                                                            searchResults.appendChild(allResultsLink);
                                                        } else if (data.results && data.results.length && (type === 'all' || type === 'model')) {
                                                            // Mostrar productos con imagen
                                                            searchResults.style.display = 'block';
                                                            var seenIds = new Set();
                                                            data.results.slice(0, 7).forEach(function(result){
                                                                if (result.id && seenIds.has(result.id)) return;
                                                                if (result.id) seenIds.add(result.id);
                                                                var name = result.name || '';
                                                                var item = document.createElement('a');
                                                                item.className = 'dropdown-item d-flex align-items-center';
                                                                var url = result.website_url ? result.website_url : ('/shop/' + name + '?product=product.template(' + result.id + ',)');
                                                                item.href = url;
                                                                item.title = name || 'Producto';
                                                                var imgSrc = '/theme_xtream/static/src/img/placeholder.png';
                                                                if (result.image) {
                                                                    imgSrc = result.image;
                                                                } else if (result.id) {
                                                                    imgSrc = '/web/image/product.template/' + result.id + '/image_1920';
                                                                }
                                                                var imgAlt = name || 'Producto';
                                                                item.innerHTML = '<img src="' + imgSrc + '" alt="' + imgAlt + '" style="width:32px;height:32px;object-fit:contain;margin-right:10px;"/>' +
                                                                                 '<div style="overflow:auto;white-space:normal;text-overflow:unset;max-width:none;font-size:15px;">' + name + '</div>';
                                                                searchResults.appendChild(item);
                                                            });

                                                            var allResultsLink = document.createElement('a');
                                                            allResultsLink.className = 'dropdown-item text-center';
                                                            allResultsLink.href = '/subcategory?search=' + encodeURIComponent(query);
                                                            allResultsLink.textContent = 'Ver todos los resultados';
                                                            allResultsLink.style.fontSize = '15px';
                                                            allResultsLink.style.padding = '8px 0';
                                                            searchResults.appendChild(allResultsLink);
                                                        } else {
                                                            searchResults.style.display = 'none';
                                                        }
                                                    })
                                                    .catch(function(){
                                                        searchResults.style.display = 'none';
                                                    });
                                            });

                                            function onDocClickDesktop(e) {
                                                if (!desktopNav.contains(e.target)) {
                                                    if (searchResults && searchResults.style.display !== 'none') {
                                                        setTimeout(function(){ searchResults.style.display = 'none'; }, 150);
                                                    }
                                                }
                                            }
                                            document.addEventListener('click', onDocClickDesktop);
                                        }

                                        if (document.readyState === 'loading') {
                                            document.addEventListener('DOMContentLoaded', initDesktopSearch);
                                        } else {
                                            initDesktopSearch();
                                        }
                                    })();
