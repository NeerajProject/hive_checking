odoo.define('techfuge_event_qrcode_scanner.exhibitor_dashboard_qrcode', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;


    publicWidget.registry.DashboardQRScan = publicWidget.Widget.extend({
        selector: '.badge-scan-container',

        start: function () {

            const qrcode = window.qrcode;

            const video = document.createElement("video");
            const canvasElement = document.getElementById("qr-canvas");
            const canvas = canvasElement.getContext("2d");

            const btnScanQR = document.getElementById("btn-scan-qr");
            const scanQRMsg = document.getElementById("scan-qr-msg");
            const invalidQRMsg = document.getElementById("invalid-qr-msg");
            const badgeQRInfo = document.getElementById("badge-qr-info");

            let scanning = false;

            qrcode.callback = data => {
                if (data) {
                    this._rpc({
                        model: 'event.registration',
                        method: 'get_badge_details',
                        kwargs: {
                            qr_code_data: data,
                        }
                    }).then(function(result) {
                        if (result.error) {
                            invalidQRMsg.hidden = false;
                            badgeQRInfo.innerText = result.error;
                        } else {
                            window.location.replace(result.redirect_url);
                        }
                    });

                    scanning = false;

                    video.srcObject.getTracks().forEach(track => {
                        track.stop();
                    });

                    canvasElement.hidden = true;
                    btnScanQR.hidden = false;
                    scanQRMsg.hidden = false;
                }
            };

            btnScanQR.onclick = () => {
                navigator.mediaDevices
                .getUserMedia({ video: { facingMode: "environment" } })
                .then(function(stream) {
                    scanning = true;
                    btnScanQR.hidden = true;
                    scanQRMsg.hidden = true;
                    invalidQRMsg.hidden = true;
                    canvasElement.hidden = false;
                    video.setAttribute("playsinline", true);
                    video.srcObject = stream;
                    video.play();
                    tick();
                    scan();
                });
            };

            function tick() {
                canvasElement.height = video.videoHeight;
                canvasElement.width = video.videoWidth;
                canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

                scanning && requestAnimationFrame(tick);
            }

            function scan() {
                try {
                    qrcode.decode();
                } catch (e) {
                    setTimeout(scan, 300);
                }
            }

            return this._super.apply(this, arguments);
        },

    });

});