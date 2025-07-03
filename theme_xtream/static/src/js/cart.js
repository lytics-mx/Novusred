odoo.define('theme_xtream.cart', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.CartUpdateCounter = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'change .cart-quantity-input input[name="set_qty"]': '_onChangeQuantity',
            'click .js_add_cart_json': '_onClickAddToCart',
        },

        _onChangeQuantity: function (ev) {
            var self = this;
            this._updateCartBadge();
        },

        _onClickAddToCart: function (ev) {
            var self = this;
            setTimeout(function() {
                self._updateCartBadge();
            }, 500);
        },

        _updateCartBadge: function () {
            let totalItems = 0;
            document.querySelectorAll('.cart-quantity-input input[name="set_qty"]').forEach(function(input) {
                totalItems += parseInt(input.value) || 0;
            });
            
            ajax.jsonRpc('/shop/cart/update_badge', 'call', {
                'total_items': totalItems
            }).then(function (data) {
                // Actualizar todos los indicadores del carrito en la página
                document.querySelectorAll('.my_cart_quantity').forEach(function(badge) {
                    badge.textContent = totalItems;
                });
            });
        }
    });
});