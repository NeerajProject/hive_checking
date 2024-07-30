/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useInputField } from "@web/views/fields/input_field_hook";
import time from 'web.time';
import { whenReady, mount } from "@odoo/owl";
const { DateTime } = luxon;
var translation = require('web.translation');
import { useService } from "@web/core/utils/hooks";
const { Component, EventBus, onWillStart, useSubEnv, useState,useRef,onWillUpdateProps ,onWillUnmount, onMounted} = owl;
import { standardFieldProps } from "@web/views/fields/standard_field_props";
var _t = translation._t;

//const { Component,useRef} = owl;

var rpc = require('web.rpc');

export class AvailableSlotsWizardUpdate extends Component {
   static template = 'AvailableSlotsWizard'
   async setup(){




        this.action = useService("action");
        this.appointment_id = this.env.model.root.data.id
        this.props.available_slots=[]


    this.state = useState({
            available_slots: false,
            selected_slots : false
        });
 onWillStart(async () => {
            await this.getFreeSlotsInofEighteenHoles();

        });




        super.setup();




        }


        _selectAvailableSlotsWizard(duration,slot_duration,hours){
    var self =this

       this.state.selected_slots = hours
       const slot_duration_value =DateTime.fromSQL(slot_duration, { zone: "utc", numberingSystem: "latn" }).setZone("default");

        return this.props.record.update({ next_available_slot: slot_duration_value })

        }

async getFreeSlotsInofEighteenHoles(){
    var self = this
        this.props.available_slots=[{"appointment_type":"","appointment_type_id":"","slots":[]}]

 await   rpc.query({
                model: 'calendar.event',
                method: 'get_free_slots_in_of_available',
                args: [[],self.appointment_id],
            })
            .then(function (res) {
            self.state.available_slots = res
            })
}















}
AvailableSlotsWizardUpdate.props = {
    ...standardFieldProps,
};
registry.category("fields").add("AvailableSlotsWizardUpdate", AvailableSlotsWizardUpdate);
