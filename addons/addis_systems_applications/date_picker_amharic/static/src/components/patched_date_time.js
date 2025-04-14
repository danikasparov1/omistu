/** @odoo-module **/

import { patch } from "@web/core/utils/patch"
import { DateTimeField } from "@web/views/fields/datetime/datetime_field"
import { Component, onWillStart, onMounted,useState } from "@odoo/owl";

patch(DateTimeField.prototype, {
    setup(){
        super.setup()
    }
    

})