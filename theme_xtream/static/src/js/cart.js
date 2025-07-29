odoo.define('theme_xtream.cart', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.CartUpdateCounter = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            // Inicializar eventos manualmente si es necesario
            this.$el.on('change', '.cart-quantity-input input[name="set_qty"]', function() {
                self._updateCartBadge();
            });
            return this._super.apply(this, arguments);
        },

        _updateCartBadge: function () {
            let totalItems = 0;
            document.querySelectorAll('.cart-quantity-input input[name="set_qty"]').forEach(function(input) {
                totalItems += parseInt(input.value) || 0;
            });
            
            ajax.jsonRpc('/tienda/cart/update_badge', 'call', {
                'total_items': totalItems
            });
        }
    });

    return publicWidget.registry.CartUpdateCounter;
});