/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { useService } from "@web/core/utils/hooks";
import core from 'web.core';

var _t = core._t;

export class QRScanningFormController extends FormController {
    /**
     * @override
     **/
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notificationService = useService("notification");
        this.actionService = useService("action");
        this.resId = this.props.resId;
    }

    async onClickConfirmAttendeeRegistration() {
        const menu_id = await this.orm.call(
            "attendee.registration.confirm",
            "confirm_attendee_registration",
            [this.resId],
        );
        if (menu_id) {
            this.notificationService.add(this.env._t("Attendee Registration Confirmed!"), {
                type: "success",
            });
            var url = "/web#menu_id=" + menu_id;
            window.location.href = url;
        }
    }

    async onClickPrintBadge() {
        const badge_attachment_id = await this.orm.call(
            "attendee.registration.confirm",
            "print_attendee_badge",
            [this.resId],
        );
        if (badge_attachment_id) {
            var url = "/web/content/" + badge_attachment_id + "?download=true";
            window.location.href = url;
        }
    }

}

export const QRScanningFormView = {
    ...formView,
    Controller: QRScanningFormController,
};

registry.category("views").add("qr_scanning_form", QRScanningFormView);
