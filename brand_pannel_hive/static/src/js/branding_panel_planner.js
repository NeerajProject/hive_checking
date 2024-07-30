odoo.define('brand_pannel_hive.brand_pannel_hive_upload', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;




    publicWidget.registry.PlannerDashboard = publicWidget.Widget.extend({
        selector: '#brand_pannel_hive_upload',
        events: {
            'change #field_change': '_onClickShowFileName',
        },

        start: function () {

            return this._super.apply(this, arguments);
        },

          _onClickShowFileName: function (ev) {
                 var filename = $('.upload_name').val().split('\\').pop();
                 $('#field_filename').val(filename)
               },



    });

});