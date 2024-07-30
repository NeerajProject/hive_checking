# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def get_badge_details(self, qr_code_data):
        user = self.env.user
        badge_data = {}
        redirect_url = False
        attendee_id = False
        attendee_activity_obj = self.env['event.attendee.activities'].sudo()
        attendee_activity_exists = False

        if qr_code_data:
            attendee_id = qr_code_data.split('=')[1]
            redirect_url = qr_code_data

        if attendee_id:
            attendee = self.sudo().browse(int(attendee_id))
            if not attendee:
                badge_data.update({'error': 'Invalid QR Code'})
            else:
                activity_location = self.env['event.activity.location'].sudo().search(
                    [('id', 'in', user.hall_ids.ids)])
                attendee_activity = False
                if activity_location:
                    attendee_activity = attendee_activity_obj.search([
                        ('name', '=', activity_location.name),
                        ('stand_number', '=', user.stand_ids.stand_number),
                        ('attendee_id', '=', attendee.id)
                    ])

                if user.hall_ids.activity_location_type_id.is_cafe:
                    exhibitor_contract = attendee.exhibitor_contract_id
                    cafe_activities = False
                    if exhibitor_contract and exhibitor_contract.eligible_for_food_coupon:
                        if attendee_activity:
                            cafe_activities = attendee_activity.filtered(
                                lambda activity: activity.attendee_activity_datetime.date() == fields.Date.today())
                        if exhibitor_contract.space_type_id.type == 'package':
                            if cafe_activities and len(cafe_activities) == 2:
                                attendee_activity_exists = True
                                badge_data.update({'error': 'Already consumed the food coupons for today'})
                        else:
                            if not exhibitor_contract.no_of_food_coupons:
                                badge_data.update({'error': 'No food coupons available'})
                                attendee_activity_exists = True
                            elif not exhibitor_contract.remaining_food_coupons:
                                attendee_activity_exists = True
                                badge_data.update({'error': 'All the food coupons are consumed'})
                            else:
                                if cafe_activities and len(cafe_activities) == 2:
                                    attendee_activity_exists = True
                                    badge_data.update({'error': 'Already consumed the food coupons for today'})
                    else:
                        badge_data.update({'error': 'No food coupons available'})

                if not attendee_activity_exists:
                    badge_data.update({
                        'attendee_id': attendee.id,
                        'redirect_url': redirect_url
                    })

        return badge_data
