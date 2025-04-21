odoo.define('theme_xtream.category_toggle', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.CategoryToggle = publicWidget.Widget.extend({
        selector: '.category-toggle',
        events: {
            'click': '_onCategoryClick',
        },

        /**
         * Maneja el clic en una categoría para desplegar/ocultar subcategorías.
         */
        _onCategoryClick: function (ev) {
            ev.preventDefault();
            const categoryId = ev.currentTarget.dataset.categoryId;
            const subcategoryList = document.querySelector(`#subcategory-${categoryId}`);
            if (subcategoryList) {
                const isVisible = subcategoryList.style.display === 'block';
                subcategoryList.style.display = isVisible ? 'none' : 'block';
            }
        },
    });
});