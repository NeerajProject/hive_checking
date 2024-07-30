odoo.define('aegc_calender_customization.aegc_booking_backend', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var time = require('web.time');
var field_utils = require('web.field_utils');
var QWeb = core.qweb;

var _t = core._t;


var AegcBookingBackend = AbstractAction.extend({
    contentTemplate: 'AegcBookingBackend',
    events: {
    'click #create_appointment':'_createAppointment',
    'click #open_already_booked_button': '_openAppointment',
    'mousemove #reload_page_of_booking_screen': '_reloadPage',
    'change #appointment_type_remove': '_captureAppointmentTypeRemove',
    'change #appointment_type_add': '_captureAppointmentTypeAdd',
     'change #update_search_date_of_screen': '_captureDateUpdate',
      'click #close_reload_page':'_reloadPageSearch',
      'click #aegc_create_event':'_createEvent'
    },


_createEvent: async function(ev){
                    this.is_update = true


 var action= {'name': ' Create Event ',
                'type': 'ir.actions.act_window',
                'res_model': 'golf.event.create',
                'view_mode': 'tree,form,calendar',
                'views': [[false, 'form']],
                'target': 'new'}
            return this.do_action(action)

},

_captureAppointmentTypeRemove: async function(ev){
var self= this
var added_appointment_type = parseInt(ev.target.value)
await this._rpc({
                model: 'appointment.type',
                method: 'unlink_appointment_type_in_search',
                args: [[],added_appointment_type],
            })
            .then(function (res) {
            })




},


_captureAppointmentTypeAdd:async function(ev){
var self= this
var added_appointment_type = parseInt(ev.target.value)
await this._rpc({
                model: 'appointment.type',
                method: 'set_appointment_type_in_search',
                args: [[],added_appointment_type],
            })
            .then(function (res) {
            })




},


_captureDateUpdate : async function(ev){
var self= this
var date_of_search = ev.target.value
await this._rpc({
                model: 'appointment.type',
                method: 'update_default_search_date',
                args: [[],date_of_search],
            })
            .then(function (res) {
            })


},

_reloadPageSearch: async function(env){
location.reload();

},

_reloadPage: async function(env){

var self = this

if (self.is_update){
  var def1 =  await this._rpc({
                model: 'appointment.type',
                method: 'get_screen_data_for_golf',
                args: [[]],
            })
            .then(function (res) {

            self.all_slots_available = res
            })


                this.$el.html(QWeb.render("AegcBookingBackend", {widget: this}))

}

self.is_update = false

},


_openAppointment: function(env){
if (env.target.attributes.value){

var id = env.target.attributes.value.nodeValue
                    this.is_update = true

 var action= {'name': ' Appointment ',
                'type': 'ir.actions.act_window',
                'res_model': 'calendar.event',
                'view_mode': 'tree,form,calendar',
                'views': [[false, 'form']],
                'target': 'current',
                 'res_id': parseInt(id)}
            return this.do_action(action)

}
else{
}



},
_createAppointment: async  function(env){
    var self = this
    var starting_time =env.target.attributes.value.nodeValue
    var duration = env.target.attributes.title.nodeValue
    var appointment_type_id = env.target.attributes.href.value
    console.log(env.target.attributes)

 await  this._rpc({
                model: 'appointment.type',
                method: 'get_form_view_action',
                args: [[],appointment_type_id,starting_time,duration],
            })
            .then(function (res) {
    return self.do_action(res)
            })

                    this.is_update = true


            },




 willStart:   function () {
        var self = this;
        self.is_update = false
     var def1 =  this._rpc({
                model: 'appointment.type',
                method: 'get_screen_data_for_golf',
                args: [[]],
            })
            .then(function (res) {
            console.log('all_slots_available',res)
            self.all_slots_available = res
            })


             var def2 = this._rpc({
                model: 'appointment.type',
                method: 'get_all_appointment_type',
                args: [[]],
            })
            .then(function (res) {

            self.all_appointment_type_except_selected = res
            console.log('res',res)
            })

        return Promise.all([def1,def2, this._super.apply(this, arguments)]);
    },

});

core.action_registry.add('AegcBookingBackend', AegcBookingBackend);

return AegcBookingBackend;

});
