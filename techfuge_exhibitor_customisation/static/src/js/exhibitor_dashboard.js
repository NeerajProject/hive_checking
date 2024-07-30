odoo.define('techfuge_exhibitor_customisation.exhibitor_dashboard', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;


    publicWidget.registry.PlannerDashboard = publicWidget.Widget.extend({
        selector: '.dashboard',
        jsLibs: [
            '/web/static/lib/Chart/Chart.js',
        ],
        events: {
            'click #btn_clear_all': '_onClickClearAllData',
            'click #btn_clear_shipment_form': '_onClickClearAllShipmentData',
            'change #exh_letter_from_date': '_getNumberOfLetterRequestDays',
            'change #exh_letter_till_date': '_getNumberOfLetterRequestDays',
            'change #exh_hotel_checkin_date': '_getNumberOfNights',
            'change #exh_hotel_checkout_date': '_getNumberOfNights',
            'change #exh_shipment_volume': '_onChangeShipmentVolume',
            'click #btn_generate_badge': '_onClickGenerateBadge',
            'click #btn_book_hotel': '_onClickBookHotel',
            'change #exh_document_type': '_onChangeDocumentType',
            'change #exh_shipment_document_type': '_onChangeDocumentType',
            'change #ehx_contractor_document_type': '_onChangeDocumentType',
            'click a.other_request_change_qty': '_onClickChangeQuantity',
            'change .other_request_quantity': '_onChangeOtherRequestQuantity',
            'click .confirm_other_request': '_onCClickOtherRequestButton',
            'submit #attendee_badge_request_form': '_onSubmitBadgeRequestForm',
        },

        start: function () {

            this._getNumberOfLetterRequestDays();
            $("#exh_hotel_checkin_date").val('2023-06-12');
            $("#exh_hotel_checkout_date").val('2023-06-16');
            this._getNumberOfNights();

            setTimeout(function() {
                $('#submission_success_msg').fadeOut('medium');
            }, 10000);

            document.querySelectorAll('nav.dashboard-nav-list > a').forEach((nav) => {
                var navPathname = nav.pathname;
                var windowLocationPathname = window.location.pathname;
                if ((navPathname === windowLocationPathname) || (navPathname === '/exhibitor_dashboard/company_details'
                && windowLocationPathname.includes('/exhibitor_dashboard/company_details/')) || (navPathname === '/exhibitor_dashboard/other_requests'
                && windowLocationPathname.includes('/exhibitor_dashboard/other_requests/'))) {
                    nav.classList.add('active')
                } else {
                    nav.classList.remove('active')
                }
            });

            this._rpc({
                model: 'exhibitor.contract',
                method: 'get_badge_information',
                args: [session.user_id],
            }).then(function (result) {
                if (result && window.location.pathname === '/exhibitor_dashboard') {
                    if (result.remaining_badges) {
                        var xValues = ["Used", "Remaining"];
                        var yValues = [result.used_badges, result.remaining_badges];
                        var barColors = [
                            "#12adbc",
                            "#f07216"
                        ];
                    } else {
                        var xValues = ["Generated Badges"];
                        var yValues = [result.used_badges];
                        var barColors = [
                            "#12adbc",
                        ];
                    }

                    new Chart("badge-info-chart", {
                        type: "doughnut",
                        data: {
                            labels: xValues,
                            datasets: [{
                                backgroundColor: barColors,
                                data: yValues
                            }]
                        },
                        options: {
                            title: {
                                display: true,
                                text: "Badge Usage"
                            }
                        }
                    });
                }
            });

            return this._super.apply(this, arguments);
        },

        _onClickGenerateBadge : function (ev) {
            var space_type = $('#space_type').val();
            var no_of_badges = $('#no_of_badges').val();
            var remaining_badges = $('#remaining_badges').val();
            var selected_attendee = $('#selected_attendee').val();
            if (space_type === 'non-package' || space_type === '') {
                if (!no_of_badges) {
                    new Dialog(this, {
                        title: _t("HFS 2023"),
                        $content: $('<div>', {
                            text: _t("Badges are chargeable. Go to 'Place Orders' Section and  Please send request for an Invoice !")
                        }),
                    }).open();
                    return false;
                } else if (!remaining_badges && !selected_attendee) {
                    new Dialog(this, {
                        title: _t("HFS 2023"),
                        $content: $('<div>', {
                            text: _t("To request for more Badges, Please send mail to exhibit@iiffglobal.com")
                        }),
                    }).open();
                    return false;
                }
            }
        },

        _onSubmitBadgeRequestForm: function (ev) {
            $('#btn_generate_badge').attr('disabled','disabled')
        },

        _onClickClearAllData: function (ev) {
            if (ev.currentTarget.form) {
                ev.currentTarget.form.reset()
            }
        },

        _onClickClearAllShipmentData: function (ev) {
            document.getElementById("shipment_details_submission_form").reset()
            document.getElementById("shipment_upload_document_form").reset()
        },

        _getNumberOfLetterRequestDays: function (ev) {
            const from_date = new Date($("#exh_letter_from_date").val());
            const till_date = new Date($("#exh_letter_till_date").val());
            const letter_request_diff_time = Math.abs(till_date - from_date);
            const letter_request_diff_days = Math.ceil(letter_request_diff_time / (1000 * 60 * 60 * 24));
            if (letter_request_diff_days) {
                $("#exh_letter_no_of_days").val(letter_request_diff_days);
            }
        },

        _getNumberOfNights: function (ev) {
            var checkin_date = new Date($("#exh_hotel_checkin_date").val());
            var checkout_date = new Date($("#exh_hotel_checkout_date").val());
            var diffTime = Math.abs(checkout_date - checkin_date);
            var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            var allowed_nights = $("#exh_hotel_allowed_nights").val();
            var rate_per_night = $("#rate_per_additional_night").val();
            if (diffDays) {
                $("#exh_hotel_nights").val(diffDays);
                if (diffDays > allowed_nights) {
                    var additional_nights = diffDays - allowed_nights;
                    if (additional_nights) {
                        $(".additional_hotel_info").removeClass('d-none');
                        var additional_payment = additional_nights * rate_per_night;
                        $("#exh_hotel_additional_nights").val(additional_nights);
                        $("#exh_hotel_additional_payment").val(additional_payment);
                        $('#exh_hotel_additional_payment_ack').attr('required', 'required');
                    }
                }
            }
            return diffDays;
        },

        _onClickBookHotel: function (ev) {
            var diffDays = this._getNumberOfNights();
            var event_year = $('#event_year').val();
            var warning_title = "HFS " + event_year;
            var remaining_rooms = $('#remaining_hotel_rooms').val();
            if (!remaining_rooms) {
                new Dialog(this, {
                    title: _t(warning_title),
                    $content: $('<div>', {
                        text: _t("Do you need more Hotel Rooms than assigned? Please contact Hive team !")
                    }),
                }).open();
                return false;
            }
        },

        _onChangeDocumentType: function (ev) {
            let type_id = false;
            const document_type_id = $("#exh_document_type").val();
            const shipment_document_type_id = $("#exh_shipment_document_type").val();
            const contractor_document_type_id = $("#ehx_contractor_document_type").val();

            if (document_type_id) {
                type_id = document_type_id;
            } else if (shipment_document_type_id) {
                type_id = shipment_document_type_id;
            } else if (contractor_document_type_id) {
                type_id = contractor_document_type_id;
            }

            this._rpc({
                model: 'exhibitor.document.type',
                method: 'get_document_information',
                args: [type_id],
            }).then(function (document_data) {
                if (document_data) {
                    if (document_data.document_size && document_data.document_format) {
                        var document_format_msg = "Please upload file less than " + document_data.document_size +
                        " MB and file format should be " + document_data.document_format
                        document.getElementById("document_format_msg").innerText = document_format_msg;
                    } else {
                        document.getElementById("document_format_msg").innerText = '';
                    }

                    if (document_data.document_note) {
                        document.getElementById("document_additional_msg").innerText = document_data.document_note;
                    } else {
                        document.getElementById("document_additional_msg").innerText = '';
                    }
                }
            });
        },

        _onChangeShipmentVolume: function (ev) {
            const total_area = $("#exh_total_area").val();
            const allowed_cbm = total_area / 10;
            const total_volume = $("#exh_shipment_volume").val();
            const extra_cbm = total_volume - allowed_cbm;
            const exceeding_charge = $("#exh_shipment_exc_charge").val();
            const additional_charges = extra_cbm * exceeding_charge;
//            const additional_charges = $("#exh_shipment_add_charge").val()
            $("#exh_shipment_allowed_cbm").val(allowed_cbm);
            if (extra_cbm > 0) {
                $("#exh_shipment_extra_cbm").val(extra_cbm.toFixed(2));
                $("#exh_shipment_add_charge").val(Math.round(additional_charges));
                $("#exh_shipment_final_charge").val(Math.round(additional_charges));
            }else{
            $("#exh_shipment_extra_cbm").val(0);
                $("#exh_shipment_add_charge").val(0);
                $("#exh_shipment_final_charge").val(0);
            }
        },

        _onClickChangeQuantity: function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.input-group').find("input");
            var min = parseFloat($input.data("min") || 0);
            var max = parseFloat($input.data("max") || Infinity);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            }
            return false;
        },

        async _onChangeOtherRequestQuantity(ev) {
            ev.preventDefault();
            let self = this,
            $target = $(ev.currentTarget),
            quantity = parseInt($target.val()),
            other_request_id = parseInt($target.data('other-req-id'));

            await this._rpc({
                route: "/update/other_requests",
                params: {
                    'other_request_id': other_request_id,
                    'input_quantity': quantity >= 0 ? quantity : false,
                },
            });

            window.location.reload();
        },

        _onCClickOtherRequestButton: function(ev) {
            var $target = ev.currentTarget
            var comment = $("#exh_other_request_comment").val();
            $target.href = '/submit/other_requests?exhibitor_comment=' + comment;
        },

    });

});


const mobileScreen = window.matchMedia("(max-width: 990px )");
$(document).ready(function () {

    if (window.location.pathname === '/exhibitor_dashboard') {
        $('.dashboard-toolbar').css('left', '0px');
    }

    $(".dashboard-nav-dropdown-toggle").click(function () {
        $(this).closest(".dashboard-nav-dropdown")
            .toggleClass("show")
            .find(".dashboard-nav-dropdown")
            .removeClass("show");
        $(this).parent()
            .siblings()
            .removeClass("show");
    });
    $(".menu-toggle").click(function () {
        if (mobileScreen.matches) {
            $(".dashboard-nav").toggleClass("mobile-show");
        } else {
            $(".dashboard").toggleClass("dashboard-compact");
        }
    });
});