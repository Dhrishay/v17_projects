odoo.define('sybyl_sales.update_price', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
publicWidget.registry.WebsiteSale.include({
    /**
     * Overright Cart Quantity _onChangeCartQuantity method
     for Quantity with Floating Number
     * @override
     */
    _onChangeCartQuantity: function (ev) {
        var $input = $(ev.currentTarget);
        if ($input.data('update_change')) {
            return;
        }
        var value = parseFloat($input.val() || 0.00, 10.00);
        if (isNaN(value)) {
            value = 1;
        }
        var $dom = $input.closest('tr');
        var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
        var line_id = parseInt($input.data('line-id'), 10);
        var productIDs = [parseInt($input.data('product-id'), 10)];
        this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
    }
});
});
