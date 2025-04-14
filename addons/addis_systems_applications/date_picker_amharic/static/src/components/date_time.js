
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onWillStart, onMounted,useState } from "@odoo/owl";
import { useInputField } from "@web/views/fields/input_field_hook";
import { jsonrpc } from "@web/core/network/rpc_service";

import { loadJS } from "@web/core/assets";
const { DateTime } = luxon

let ethiopianDatePickerId = 0;

export class DateEthiopiaField extends Component {
    static template = "date_picker_amharic.DateEthiopiaField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.datePickerId = `ethiopian_datepicker_${ethiopianDatePickerId++}`;
        onWillStart(async () => {
            await loadJS("date_picker_amharic/static/src/js/jquery.plugin.js");
            await loadJS("date_picker_amharic/static/src/js/jquery.calendars.js");
            await loadJS("date_picker_amharic/static/src/js/jquery.calendars.plus.js");
            await loadJS("date_picker_amharic/static/src/js/jquery.calendars.picker.js");
            await loadJS("date_picker_amharic/static/src/js/jquery.calendars.ethiopian.js");
            await loadJS("date_picker_amharic/static/src/js/jquery.calendars.ethiopian-am.js");
        });

        onMounted(() => {
            const calendar = $.calendars.instance("ethiopian", "am");
            $(`#${this.datePickerId}`).calendarsPicker({
                calendar: calendar,
                onSelect: this.onDateSelect.bind(this)

            });
        });
    }

    async onDateSelect(date) {
        // Handle date based on structure
        let formattedDate;
        if (Array.isArray(date)) {
            // If date is an array, extract and format
            const { _day, _month, _year } = date[0];
            formattedDate = `${_month}/${_day}/${_year}`;
        } else if (typeof date === "object" && date._day && date._month && date._year) {
            // If date is an object, format directly
            const { _day, _month, _year } = date;
            formattedDate = `${_month}/${_day}/${_year}`;
        } else if (typeof date === "string") {
            // If date is a string, assume it's already formatted
            formattedDate = date;
        } else {
            console.error("Unexpected date format or structure:", date);
            return;
        }
    
        const json_date = await jsonrpc('/get_date_gregorian',{'date':formattedDate});
        formattedDate = json_date.date
        const luxonDate = DateTime.fromFormat(formattedDate, "M/d/yyyy"); // Allow single/double digits
    
        if (luxonDate.isValid) {
            console.log("Valid Luxon date:", luxonDate.toISO());
    
            // Save the Luxon ISO format date
            var toUpdate={
                [this.props.name]:luxonDate
            }
            //this.props.record.data[this.props.name] = luxonDate.toISO();
            this.props.record.update(toUpdate);
            // this.state.date = luxonDate

        } else {
            console.error("Invalid date format. Luxon could not parse:", formattedDate);
        }
    }
    

    get formattedValue(){
        var dtHebrew = this.props.record.data[this.props.name] ? this.props.record.data[this.props.name].reconfigure({ outputCalendar: "ethiopic" }):"";
        const formattedDate = dtHebrew.toLocaleString().split(' ')[0]; // "4/8/2017"
        const [month, day, year] = formattedDate.split('/'); // Split into components
        const newFormat = `${day}/${month}/${year}`;
        return newFormat
        return this.props.record.data[this.props.name] 
        ? DateTime.fromISO(this.props.record.data[this.props.name]).toFormat("MM/dd/yyyy") 
        : "";
        }

   
}

export const dateEthiopia = {
    component: DateEthiopiaField,
    displayName: "Ethiopian Date",
    supportedTypes: ["date"],
    extractProps: ({ attrs }) => ({
    })
};

registry.category("fields").add("date_ethiopia", dateEthiopia);
