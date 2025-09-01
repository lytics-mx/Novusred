document.addEventListener('DOMContentLoaded', function() {
    // Código para menús de categorías
    const parentCategories = document.querySelectorAll('.parent-category');
    const childCategories = document.querySelectorAll('.child-category');

    parentCategories.forEach(parent => {
        parent.addEventListener('mouseenter', function() {
            const subMenu = parent.querySelector('.subcategory-menu');
            if (subMenu && subMenu.children.length > 0) {
                subMenu.style.display = 'block';
            }
        });

        parent.addEventListener('mouseleave', function() {
            const subMenu = parent.querySelector('.subcategory-menu');
            if (subMenu) {
                subMenu.style.display = 'none';
            }
        });
    });

    childCategories.forEach(child => {
        child.addEventListener('mouseenter', function() {
            const subMenu = child.querySelector('.subcategory-menu');
            if (subMenu && subMenu.children.length > 0) {
                subMenu.style.display = 'block';
            }
        });

        child.addEventListener('mouseleave', function() {
            const subMenu = child.querySelector('.subcategory-menu');
            if (subMenu) {
                subMenu.style.display = 'none';
            }
        });
    });

    // Código para notificaciones
    const notificationCounter = document.getElementById('notificationCounter');
    const notificationMessage = document.getElementById('notificationMessage');
    const noNotificationsMessage = document.getElementById('noNotificationsMessage');

    // Simulación de lógica para mostrar notificaciones
    const hasNotifications = false; // Cambiar a true si hay notificaciones

    if (hasNotifications) {
        if (notificationCounter) notificationCounter.style.display = 'block';
        if (notificationMessage) notificationMessage.style.display = 'block';
        if (noNotificationsMessage) noNotificationsMessage.style.display = 'none';
    } else {
        if (notificationCounter) notificationCounter.style.display = 'none';
        if (notificationMessage) notificationMessage.style.display = 'none';
        if (noNotificationsMessage) noNotificationsMessage.style.display = 'block';
    }

    // Código para búsqueda en vivo
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const searchTypeInput = document.querySelector('input[name="search_type"]');

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function() {
            const query = searchInput.value.trim();
            const searchType = searchTypeInput ? searchTypeInput.value : 'all';
            
            // Solo mostrar productos si el filtro es "all"
            if (query.length > 0 && searchType === 'all') {
                fetch(`/search_live?query=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        searchResults.innerHTML = '';
                        if (data.results.length > 0) {
                            searchResults.style.display = 'block';
                            data.results.slice(0, 5).forEach(result => {
                                const truncatedName = result.name.length > 160 ? result.name.substring(0, 160) + '...' : result.name;
                                const item = document.createElement('a');
                                item.className = 'dropdown-item';
                                item.href = `/shop/product/${result.id}`;
                                item.innerHTML = `
                                    <img src="/web/image/product.template/${result.id}/image_1024" alt="${truncatedName}" style="width: 40px; height: 40px; object-fit: contain; margin-right: 10px;" />
                                    <span style="display: inline-block; vertical-align: middle; max-width: 1000px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${truncatedName}</span>
                                `;
                                searchResults.appendChild(item);
                            });
                            const allResultsLink = document.createElement('a');
                            allResultsLink.className = 'dropdown-item text-center';
                            allResultsLink.href = `/subcategory?category_id=${encodeURIComponent(query)}`;
                            allResultsLink.innerHTML = 'Ver todos los resultados';
                            searchResults.appendChild(allResultsLink);
                        } else {
                            searchResults.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching search results:', error);
                        searchResults.style.display = 'none';
                    });
            } else {
                searchResults.style.display = 'none';
            }
        });

        document.addEventListener('click', function(event) {
            if (!searchResults.contains(event.target) && event.target !== searchInput) {
                searchResults.style.display = 'none';
            }
        });

        // Manejo de los filtros para cambiar el placeholder y el tipo de búsqueda
        const dropdownItems = document.querySelectorAll('.dropdown-menu .dropdown-item');
        dropdownItems.forEach(function(item) {
            item.addEventListener('click', function() {
                let value = '';
                let placeholder = '';
                if (this.textContent.includes('Todo')) {
                    value = 'all';
                    placeholder = 'Buscar productos, marcas o categorías...';
                } else if (this.textContent.includes('Marca')) {
                    value = 'brand';
                    placeholder = 'Buscar marca...';
                } else if (this.textContent.includes('Categoría')) {
                    value = 'category';
                    placeholder = 'Buscar categoría...';
                }
                if (searchTypeInput) searchTypeInput.value = value;
                if (searchInput) searchInput.placeholder = placeholder;
                // Oculta los resultados si no es "all"
                if (value !== 'all') {
                    searchResults.style.display = 'none';
                }
            });
        });
    }

    // Función para mostrar notificación del carrito
    function showCartNotification(productHtml) {
        var popup = document.getElementById('notificationPopup');
        var content = document.getElementById('notificationPopupContent');
        if (popup && content) {
            content.innerHTML = productHtml;
            popup.style.display = 'block';
            setTimeout(function() {
                popup.style.display = 'none';
            }, 4000); // Oculta después de 4 segundos
        }
    }


        // Actualiza el badge del carrito
    function updateCartBadge(qty) {
        var badge = document.getElementById('notificationCounter');
        if (badge) {
            badge.textContent = qty;
            badge.style.display = qty > 0 ? 'inline-block' : 'none';
        }
    }
    
    // Muestra el popup de notificación
    function showCartNotification(productName, qty) {
        var popup = document.getElementById('notificationPopup');
        var content = document.getElementById('notificationPopupContent');
        if (popup && content) {
            content.innerHTML = `<div>${qty} x ${productName} agregado(s) al carrito.</div>`;
            popup.style.display = 'block';
            setTimeout(function() { popup.style.display = 'none'; }, 3500); // Se oculta después de 3.5s
        }
    }
    

});                 