                                        document.addEventListener('DOMContentLoaded', function() {
                                            var wishlistBtn = document.getElementById('wishlist-btn');
                                            var wishlistIcon = document.getElementById('wishlist-icon');
                                            var productId = wishlistBtn ? wishlistBtn.getAttribute('data-product-product-id') : null;

                                            if (wishlistBtn && wishlistIcon && productId) {
                                                wishlistBtn.addEventListener('click', function() {
                                                    var isActive = wishlistIcon.classList.contains('wishlist-active');
                                                    var url = isActive
                                                        ? '/wishlist/remove/' + productId
                                                        : '/wishlist/add/' + productId;

                                                    fetch(url, {
                                                        method: 'POST',
                                                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                                                    }).then(function() {
                                                        // Cambia el color: negro si activo, gris si no
                                                        if (isActive) {
                                                            wishlistIcon.classList.remove('wishlist-active');
                                                            wishlistIcon.style.color = '#888'; // gris
                                                        } else {
                                                            wishlistIcon.classList.add('wishlist-active');
                                                            wishlistIcon.style.color = '#222'; // negro
                                                        }
                                                    });
                                                });
                                            }
                                        });