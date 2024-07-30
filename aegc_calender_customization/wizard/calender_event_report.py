from odoo import fields, models, api
import json
from odoo.tools import date_utils, groupby as groupbyelem

import xlsxwriter
import base64

import io
import json
from datetime import datetime, date
from dateutil.rrule import rrule, DAILY

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from datetime import datetime, timedelta


class AppointmentSlot(models.Model):
    _inherit = "appointment.slot"

    def get_slots_duration_list(self):
        all_slots = {}
        dates = self.display_name.split(",")[1].split("-")
        start_time = datetime.strptime(dates[0].replace(' ', ''), "%H:%M")
        end_time = datetime.strptime(dates[1].replace(' ', ''), "%H:%M")
        time_interval = timedelta(hours=self.appointment_type_id.appointment_duration)


        current_time = start_time

        while current_time <= end_time:
            all_slots[current_time.strftime("%H:%M")] = {'duration': current_time.strftime("%H:%M"), "attendees": [],
                                                         'status': 'Available'}
            current_time += time_interval

        return all_slots


class CalenderEventReport(models.TransientModel):
    _name = 'calendar.event.report'

    date_of_entry = fields.Date(string='Date ', required=True)
    operation_type_id = fields.Many2many('appointment.type', string="Appointment Type", required=True)

    def action_download_report(self):
        return self.env.ref('aegc_calender_customization.action_calendar_event_report_xls').report_action(self, data={})
