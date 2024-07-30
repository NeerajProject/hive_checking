odoo.define('techfuge_customisation.event_registration_details', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.EventRegistrationDetails = publicWidget.Widget.extend({
        selector: '.event_reg_details_section',
        events: {
            'click #btn_submit_event_reg_details': '_onClickSubmitEventRegistrationDetails',
        },

        start: function () {

            var attendee_id = $("#attendee_id").val();
            var attendee_activity_location = $("#attendee_activity_location").val();
            var exhibitor_name = $("#exhibitor_name").val();
            var stand_number = $("#stand_number").val();

            $.ajax({
                url: '/submit/event_registration_details',
                type: 'POST',
                data: {
                    attendee_id: attendee_id,
                    attendee_activity_location: attendee_activity_location,
                    exhibitor_name: exhibitor_name,
                    stand_number: stand_number
                },
            });

            setTimeout(function() {
                window.location.href = '/exhibitor_dashboard/scan_badge';
            }, 2000);

            return this._super.apply(this, arguments);
        },

        _onClickSubmitEventRegistrationDetails: function (ev) {
            var activity_location = $("#attendee_activity_location").val();
            var exhibitor_name = $("#exhibitor_name").val();
            if (!activity_location && !exhibitor_name) {
                alert("Please select either location or exhibitor");
                return false;
            }
        },

    });

});
