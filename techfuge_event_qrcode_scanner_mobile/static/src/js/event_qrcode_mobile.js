odoo.define('web.event.qrcode_mobile', function (require) {
"use strict";

    const EventQRCodeScanView = require('techfuge_event_qrcode_scanner.EventQRCodeScanView');
    const barcodeMobileMixin = require('web_mobile.barcode_mobile_mixin');

    EventQRCodeScanView.include(Object.assign({}, barcodeMobileMixin, {
        events: Object.assign({}, barcodeMobileMixin.events, EventQRCodeScanView.prototype.events)
    }));

});
