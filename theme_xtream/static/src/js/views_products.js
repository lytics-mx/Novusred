document.addEventListener('DOMContentLoaded', function() {
    var wishlistBtn = document.getElementById('wishlist-btn');
    var wishlistIcon = document.getElementById('wishlist-icon');
    var productId = wishlistBtn ? wishlistBtn.getAttribute('data-product-product-id') : null;

    if (wishlistBtn && productId) {
        wishlistBtn.addEventListener('click', function() {
            var isActive = wishlistIcon.classList.contains('text-danger');
            var url = isActive
                ? '/wishlist/remove/' + productId
                : '/wishlist/add/' + productId;

            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            }).then(function() {
                wishlistIcon.classList.toggle('text-danger', !isActive);
                wishlistIcon.classList.toggle('text-secondary', isActive);
            });
        });
    }
});