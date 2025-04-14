/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useInputField } from "@web/views/fields/input_field_hook";
import { Component } from "@odoo/owl";
export class Tinnumber extends Component {
    static template = "addis_systems_sales.tinNumber";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        useInputField({ getValue: () => this.props.record.data[this.props.name] || "" });
    }
    get isinvalidTinnumber(){
        console.log("ABD",this.props.record.data)
        let re = /^\d{10}$|^\d{11}$|^\d{12}$|^\d{10}-\d{1,2}$/;

        if (re.test(this.props.record.data[this.props.name])){
            return false
        }
        return true
    }
    get phoneHref() {
        return "tel:" + this.props.record.data[this.props.name].replace(/\s+/g, "");
    }
}

export const tinnumber = {
    component: Tinnumber,
    displayName: _t("tinnumber"),
    supportedTypes: ["number"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("tinnumber", tinnumber);
