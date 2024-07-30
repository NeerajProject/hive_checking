odoo.define('techfuge_event_qrcode_scanner.EventQRCodeScanView', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t;
    var QWeb = core.qweb;


    // load widget with main qrcode scanning View
    var EventQRCodeScanView = AbstractAction.extend({
        contentTemplate: 'event_qrcode_template',
        events: {
            'click .o_event_previous_menu': '_onClickBackToEvents',
        },

        /**
         * @override
         */
        willStart: function() {
            var self = this;
            return this._super().then(async function() {
                self.data = await self._rpc({
                    route: '/event/init_qrcode_interface',
                });
            });

        },

        /**
         * @override
         */
        start: function() {
            core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        },

        /**
         * @override
         */
        destroy: function () {
            core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
            this._super();
        },

        /**
         * @private
         *
         * When scanning a qrcode, call Registration.get_badge_details() to get
         * formatted badge information.
         */
        _onBarcodeScanned: function(barcode) {
            var self = this;
            this._rpc({
                model: 'event.registration',
                method: 'get_badge_details',
                kwargs: {
                    qr_code_data: barcode,
                }
            }).then(function(result) {
                if (result.error) {
                    self.displayNotification({ title: _t("Warning"), message: result.error, type: 'danger' });
                } else {
                    self._rpc({
                        model: 'attendee.registration.confirm',
                        method: 'create_attendee_registration_data',
                        kwargs: {
                            attendee_id: result.attendee_id,
                        }
                    }).then(function(attendee_registration_id) {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: 'attendee.registration.confirm',
                            res_id: attendee_registration_id,
                            views: [[false, 'form']],
                            target: 'current',
                        });
                    });
                }
            });
        },

    });

    core.action_registry.add('techfuge_event_qrcode_scanner.event_qrcode_scan_view', EventQRCodeScanView);

    return EventQRCodeScanView;

});
