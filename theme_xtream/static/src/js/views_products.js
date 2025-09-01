document.addEventListener('DOMContentLoaded', function() {
    var bundleForm = document.getElementById('bundle-form');
    var totalPriceElement = document.getElementById('bundle-total'); // Elemento para mostrar el precio total
    var buyNowButton = document.getElementById('bundle-buy-now'); // Botón "Comprar"

    // Función para obtener el precio de un producto
    function getPriceFromText(text) {
        return parseFloat((text || '').replace(/[^0-9.]/g, '')) || 0;
    }

    // Función para obtener el precio raíz (descuento si existe, si no, list_price)
    function getRootPrice() {
        var discounted = document.querySelector('.col-12.col-md-4 .new-main-price');
        if (discounted) {
            return getPriceFromText(discounted.textContent);
        }
        var list = document.querySelector('.col-12.col-md-4 .fw-bold.d-block.new-main-price');
        if (list) {
            return getPriceFromText(list.textContent);
        }
        return 0;
    }

    // Función para actualizar el precio total
    function updateTotal() {
        var total = getRootPrice();
        // Sumar los accesorios seleccionados
        document.querySelectorAll('input[name="bundle_product_ids[]"]:checked').forEach(function(cb) {
            var priceDiv = cb.closest('.accessory-card')?.querySelector('.accessory-main-price') || null;
            if (priceDiv) {
                total += getPriceFromText(priceDiv.textContent);
            }
        });
        if (totalPriceElement) {
            totalPriceElement.textContent = `$${total.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
        }
    }

    // Escuchar cambios en los checkboxes
    document.querySelectorAll('input[name="bundle_product_ids[]"]').forEach(function(cb) {
        cb.addEventListener('change', updateTotal);
    });

    // Actualizar el precio total al cargar la página
    updateTotal();

    // Manejo del envío del formulario para "Agregar al carrito"
    if (bundleForm) {
        bundleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var data = new FormData(bundleForm);

            // Agregar el producto raíz al carrito
            var productRoot = document.querySelector('input[name="product_id"]').value;
            data.append('product_id', productRoot);

            // Agregar todos los productos seleccionados al carrito
            var selectedProducts = document.querySelectorAll('input[name="bundle_product_ids[]"]:checked');
            if (selectedProducts.length === 0) {
                alert('Por favor selecciona al menos un producto para agregar al carrito.');
                return;
            }
            selectedProducts.forEach(function(cb) {
                data.append('bundle_product_ids[]', cb.value);
            });

            fetch(bundleForm.action, {
                method: 'POST',
                body: data,
                credentials: 'same-origin'
            }).then(function(response) {
                if (response.ok) {
                    window.location.href = '/shop/cart';
                } else {
                    alert('Hubo un error al agregar los productos al carrito. Por favor intenta nuevamente.');
                }
            }).catch(function(error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar tu solicitud.');
            });
        });
    }

    // Manejo del botón "Comprar"
    if (buyNowButton) {
        buyNowButton.addEventListener('click', function() {
            var data = new FormData(bundleForm);

            // Agregar el producto raíz al carrito
            var productRoot = document.querySelector('input[name="product_id"]').value;
            data.append('product_id', productRoot);

            // Agregar todos los productos seleccionados al carrito
            var selectedProducts = document.querySelectorAll('input[name="bundle_product_ids[]"]:checked');
            if (selectedProducts.length === 0) {
                alert('Por favor selecciona al menos un producto para comprar.');
                return;
            }
            selectedProducts.forEach(function(cb) {
                data.append('bundle_product_ids[]', cb.value);
            });

            fetch(bundleForm.action, {
                method: 'POST',
                body: data,
                credentials: 'same-origin'
            }).then(function(response) {
                if (response.ok) {
                    window.location.href = '/shop/checkout?try_skip_step=true';
                } else {
                    alert('Hubo un error al procesar tu compra. Por favor intenta nuevamente.');
                }
            }).catch(function(error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar tu solicitud.');
            });
        });
    }

    // Galería de imágenes
    var mainImg = document.getElementById('main-product-img');
    var thumbs = document.querySelectorAll('#product-thumbs .product-thumb');
    // Cambiar imagen principal al hacer click en miniatura
    thumbs.forEach(function(thumb) {
        thumb.addEventListener('click', function() {
            mainImg.src = thumb.getAttribute('data-img');
            thumbs.forEach(function(t) { t.classList.remove('active'); });
            thumb.classList.add('active');
        });
    });
    // Al hacer click en la imagen principal, vuelve a la primera miniatura
    if (mainImg) {
        mainImg.addEventListener('click', function() {
            var firstThumb = document.querySelector('#product-thumbs .product-thumb');
            if (firstThumb) {
                mainImg.src = firstThumb.getAttribute('data-img');
                thumbs.forEach(function(t) { t.classList.remove('active'); });
                firstThumb.classList.add('active');
            }
        });
    }

    // Manejo de cantidad y popup de carrito
    var qtyInput = document.getElementById('qty-input');
    var cartQty = document.getElementById('cart-qty');
    var cartForm = document.getElementById('add-to-cart-form');
    var popup = document.getElementById('cart-popup');
    var closePopup = document.getElementById('close-popup');

    if (cartForm && cartQty && qtyInput && popup && closePopup) {
        cartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            cartQty.value = qtyInput.value;
            var data = new FormData(cartForm);
            fetch(cartForm.action, {
                method: 'POST',
                body: data,
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.ok) {
                    popup.style.display = 'block';
                }
            });
        });

        closePopup.addEventListener('click', function() {
            popup.style.display = 'none';
        });
    }
});