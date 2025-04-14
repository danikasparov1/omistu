/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import { TaxTotalsComponent } from "@account/components/tax_totals/tax_totals";
import {
    Component,
    onPatched,
    onWillUpdateProps,
    onWillRender,
    toRaw,
    useRef,
    useState,
} from "@odoo/owl";

import { formatMonetary } from "@web/views/fields/formatters";
import { formatFloat } from "@web/core/utils/numbers";
import { parseFloat } from "@web/views/fields/parsers";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { registry } from "@web/core/registry";
import { getCurrency } from "@web/core/currency";

patch(TaxTotalsComponent.prototype,{
    setup(){
        super.setup();
        this.check="check ok you know";
    },

    formatData(props) {
        let totals = JSON.parse(JSON.stringify(toRaw(props.record.data[this.props.name])));
        console.log("original subtotals",totals.subtotals)
        if (!totals) {
            return;
        }
        const currencyFmtOpts = { currencyId: props.record.data.currency_id && props.record.data.currency_id[0] };

        let amount_untaxed = totals.amount_untaxed;
        let amount_tax = 0;
        let subtotals = [];
        for (let subtotal_title of totals.subtotals_order) {
            let amount_total = amount_untaxed + amount_tax;
            console.log(subtotal_title,amount_total)
            subtotals.push({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': formatMonetary(amount_total, currencyFmtOpts),
            });
            let group = totals.groups_by_subtotal[subtotal_title];
            for (let i in group) {
                if(group[i].tax_group_amount > 0){
                    if (group[i].group_key !=-1){
                        console.log(group[i])
                        amount_tax = amount_tax + group[i].tax_group_amount;
                    }
                }
            }
        }
        totals.subtotals = subtotals;
        let rounding_amount = totals.display_rounding && totals.rounding_amount || 0;
        let amount_total = amount_untaxed + amount_tax + rounding_amount;
        totals.amount_total = amount_total;
        totals.formatted_amount_total = formatMonetary(amount_total, currencyFmtOpts);
        for (let group_name of Object.keys(totals.groups_by_subtotal)) {
            let group = totals.groups_by_subtotal[group_name];
            for (let key in group) {
                group[key].formatted_tax_group_amount = formatMonetary(group[key].tax_group_amount, currencyFmtOpts);
                group[key].formatted_tax_group_base_amount = formatMonetary(group[key].tax_group_base_amount, currencyFmtOpts);
            }
        }
        this.totals = totals;

    }

})