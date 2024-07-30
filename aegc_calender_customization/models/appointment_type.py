from odoo import fields, models,api
from datetime import date, datetime, time
from odoo.tools import plaintext2html, DEFAULT_SERVER_DATETIME_FORMAT as dtf
from datetime import timedelta




def check_events_golf_list(non_blocked, slots):

    for rec in non_blocked:
           is_end = False
           is_start =True
           index_need =[]
           index=-1
           for slot in slots:
               index = index + 1
               if is_end:
                   break
               else:
                   if is_start:

                       if slot['start'] >= rec.start+timedelta(hours=4)+ timedelta(seconds=1):
                           if rec.is_blocked:
                               index_need.append({'index':index,'is_event':True,'is_blocked':True,'name':rec.name,'color':rec.color_event})

                           else:
                               index_need.append({'index': index,'is_event':True,'is_blocked':False,'name':rec.name,'color':rec.color_event })
                           is_start = True
                   if not (slot['end'] <= rec.end + timedelta(hours=4)):
                       if rec.is_blocked:
                           index_need.append({'index': index, 'is_event': True, 'is_blocked': True,'name':rec.name,'color':rec.color_event})
                           is_end=True

                       else:
                           index_need.append({'index': index, 'is_event': True, 'is_blocked': False,'name':rec.name,'color':rec.color_event})
                           is_end=True

           for rec in  slots[index_need[0]['index']-1:index_need[-1]['index']+1]:
               rec['is_event'] = index_need[0]['is_event']
               rec['is_blocked'] = index_need[0]['is_blocked']
               rec['name'] = index_need[0]['name']
               rec['color'] = index_need[0]['color']


    print(slots)
    return  slots


class AppintmentTypeTimestamp(models.Model):
    _name='appointment.type.timestamp'
    name = fields.Char(required=True)
    last_selected_date = fields.Date(string="Last Selected Date")
    search_appointment_type_ids = fields.Many2many('appointment.type')
    def get_domain_of_filter(self):
        return  []
class AppointmentType(models.Model):
    _inherit = 'appointment.type'
    appointment_save_details = fields.Many2one('appointment.type.timestamp',string="Default View of Appointment")

    is_eighteen_points = fields.Boolean(string="Is Related 10 Tee")
    eighteen_point_appointment_type = fields.Many2one('appointment.type', string="Related 10 Tee ")
    span_of_eighteen_points = fields.Float(string="Corresponding Tee Booking time")
    span_of_eighteen_points_screeen = fields.Float(string="Screen Time Interval")
    is_visible_in_screen = fields.Boolean()
    event_appointment_type_id = fields.One2many('golf.event.create','appointment_type_id',string="Events ID")
    gap_between_slots = fields.Integer()










    # @api.onchange('span_of_eighteen_points')
    # def set_span_of_eighteen_points_screeen(self):
    #     self.span_of_eighteen_points_screeen = self.span_of_eighteen_points


    def get_form_view_action(self, appointment_type_id, start_date, duration):
        appointment_type = self.env['appointment.type'].search([('id', '=', int(appointment_type_id))])
        start_date_new = datetime.strptime(start_date, dtf)
        start_date_on_db = start_date_new
        start_date_new = start_date_new - timedelta(hours=4)
        end_date = start_date_new + timedelta(hours=float(duration))
        action = {
            'name': ' Appointment ',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'tree,form,calendar',
            'views': [[False, 'form']],
            'target': 'current',
            'context': {
                'default_name': appointment_type.name + '| Appointment | ' + str(start_date),
                'default_appointment_type_id': int(appointment_type_id),
                'default_start': start_date_new,
                'default_stop': end_date,
                'default_duration': float(duration),
                'default_real_start_date_in_db': start_date_on_db,
                'default_partner_ids': False,
                'default_start_date_real_date': start_date_on_db

            }}
        return action



    def float_to_datetime(self,input_date,last_selected_date):
        time_str = str(input_date)
        time_format = "%H:%M"

        # Assuming today's date for the example, but you can adjust as needed
        today_date_str = last_selected_date.strftime("%Y-%m-%d")
        # Combine date and time to create a datetime object
        datetime_str = f"{today_date_str} {time_str}"
        return  datetime.strptime(datetime_str, f"%Y-%m-%d {time_format}")


    def generate_time_slots(self,last_selected_date,appointment_all):
        weeks_selection = {'monday':'1','tuesday':'2','wednesday':'3','thursday':'4' ,'friday':'5' ,'saturday':'6','sunday':'7'}
        week_number = last_selected_date.strftime("%A").lower()
        slot_id =  self.slot_ids.filtered(lambda pm: pm.weekday == weeks_selection[week_number])



        if self.is_eighteen_points:
            current_time =  self.float_to_datetime(str(slot_id.start_hour).replace('.',":"),last_selected_date)+timedelta(minutes=float(self.span_of_eighteen_points_screeen))
        else:
            current_time = self.float_to_datetime(str(slot_id.start_hour).replace('.', ":"),last_selected_date)
        end_time  =   self.float_to_datetime(str(slot_id.end_hour).replace('.',":"),last_selected_date)
        print(current_time)
        print(end_time)
        print(appointment_all)

        padding_minutes= self.appointment_duration*60
        time_slots = []
        non_blocked = self.event_appointment_type_id.filtered(
            lambda o: o.date_of_event == last_selected_date)


        while current_time <= end_time:


                slot = {'time_in_text': current_time.strftime("%I:%M %p")}
                slot['id'] = False
                slot['start'] = current_time
                slot['name'] = ''
                slot['end'] = current_time+timedelta(minutes=padding_minutes)
                slot['is_already_created'] = False
                slot['attendee_type_id'] = self.id
                slot['slot_duration'] = self.appointment_duration
                slot['partner_ids'] = []
                slot['is_blocked'] = False
                slot['is_event'] = False
                time_slots.append(slot)
                current_time += timedelta(minutes=padding_minutes)

        time_slots = check_events_golf_list(non_blocked,time_slots)

        for rec  in appointment_all.filtered(lambda x: x.appointment_type_id.id == self.id ):



            for record in time_slots:
                if record['start']  == rec.start + timedelta(hours=4):

                    print('start >>>>>>>>>>>>>>>>>>>> if else', rec.start)
                    print('start view >>>>>>>> if', record['start'])
                    record['id'] = rec.id
                    record['is_already_created'] = True
                    record['start'] = rec.start+ timedelta(hours=4)
                    record['end'] = rec.stop
                    record['attendee_type_id'] = self.id
                    record['partner_ids'] = rec.partner_ids.mapped('name')
                    record['payment_status'] = rec.payment_status
        remove_duplicate =[]
        result = []
        for rec in  time_slots:
            if rec in remove_duplicate:
                pass
            else:
                remove_duplicate.append(rec)
                result.append(rec)
        return result


    def get_time_slots_of_date(self):
        record = self.env['appointment.type.timestamp'].search([],limit=1)

        last_selected_date = record.last_selected_date
        slots_list =[]
        search_appointment_type_ids= record.search_appointment_type_ids
        appointment_all = self.env['calendar.event'].search([('start_date_real_date','=',last_selected_date),('appointment_type_id','in',search_appointment_type_ids.ids)])
        for rec in search_appointment_type_ids:
            slots=rec.generate_time_slots(last_selected_date, appointment_all)
            for slot in range(rec.gap_between_slots):
                slots.insert(0,
                    {'time_in_text': '', 'id': False, 'start': '', 'name': '', 'end': '', 'is_already_created': False,
                     'attendee_type_id': 8, 'slot_duration': 0, 'partner_ids': [], 'is_blocked': True,
                     'is_event': False}
                )



            slots_list.append({'name' : rec.name ,'available_appointment':search_appointment_type_ids.ids,'appointment_type_id':rec.id,'slots':slots })
        return {'slots_list':slots_list,'date_of_search':last_selected_date.strftime("%A, %B %d, %Y")}


    def get_screen_data_for_golf(self):

        return self.get_time_slots_of_date()
    def set_appointment_type_in_search(self,added_appointment_id):
        appointment_default_search=self.env['appointment.type.timestamp'].search([],limit=1)
        appointment_type_list=appointment_default_search.search_appointment_type_ids.mapped('id')
        appointment_type_list.append(added_appointment_id)
        appointment_default_search.search_appointment_type_ids = appointment_type_list
    def unlink_appointment_type_in_search(self,added_appointment_id):
        appointment_default_search=self.env['appointment.type.timestamp'].search([],limit=1)
        appointment_type_list=appointment_default_search.search_appointment_type_ids.mapped('id')
        appointment_type_list.remove(added_appointment_id)
        appointment_default_search.search_appointment_type_ids = appointment_type_list

    def update_default_search_date(self,  date_of_search):
        appointment_default_search=self.env['appointment.type.timestamp'].search([],limit=1)
        appointment_default_search.last_selected_date = date_of_search

    def get_all_appointment_type(self):
        appointment_default_search=self.env['appointment.type.timestamp'].search([],limit=1)
        appointment_type_list= appointment_default_search.search_appointment_type_ids.mapped('id')
        appointment_type_ids = self.env['appointment.type'].search([('is_visible_in_screen','=',True)])
        appointment_type_ids_screen = []
        for rec in appointment_type_ids:
            value = {}
            value['id'] = rec.id
            value['name'] = rec.name
            if rec.id in appointment_type_list:
                value['checked'] = 1
            else:
                value['checked'] = 0
            appointment_type_ids_screen.append(value)
        print(appointment_type_ids_screen)
        return  {'appointment_type_ids_screen':appointment_type_ids_screen,'date_of_search':appointment_default_search.last_selected_date}