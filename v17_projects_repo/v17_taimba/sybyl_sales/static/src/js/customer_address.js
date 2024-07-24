odoo.define('sybyl_sales.customer_address', function(require){
    "use strict";

    var rpc = require('web.rpc');
    var ajax = require('web.ajax');

    $(document).ready(function() {
        $("select[name='route_id']").on('change',function(e){
          var routes = $("select[name='route_id']").val()
            ajax.jsonRpc('/partner/billingAddress', 'call', {
                route_id: routes,
            }).then(function(data) {
            });
        });
    });
});