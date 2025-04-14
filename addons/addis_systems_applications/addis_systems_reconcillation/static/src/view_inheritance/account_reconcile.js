/** @odoo-module */

import { registry } from "@web/core/registry"
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { jsonrpc } from "@web/core/network/rpc_service";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useState } from "@odoo/owl";

class AccountMoveLineReconcileController extends ListController {
    async setup() {
        super.setup()
        
        this.action = useService("action")
        this.orm = useService('orm');
        this.loadCurrencySymbol();
        this.state = useState({
           bank_info:null
        });
        this.state.bank_info=await this.orm.call(
            'addisystems.reconcillation.wizard',
            'get_bank_statement_info',
            [this.props.context.active_id]
    
        )
       
       
    }

 
    get Totalclickedamount() {
        this.total = 0
        for (const key in this.model.root.selection) {
            this.total += this.model.root.selection[key].data.debit - this.model.root.selection[key].data.credit
        }
        return this.total
    }


    async loadCurrencySymbol() {
        const result = await jsonrpc('/get_currency_symbol', {});
        this.currencySymbol = result.symbol;
        this.position = result.position; // optional
    }

 
    formatCurrency(value) {
        if (!this.currencySymbol) {
            // Fallback: format the number with two decimal places
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }).format(value);
        }
    
        const formattedValue = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value);
    
        return this.position === 'before'
            ? `${this.currencySymbol} ${formattedValue}`
            : `${formattedValue} ${this.currencySymbol}`;
    }

  async reconcile_items(){
    let resIds = await this.model.root.getResIds(true);
     await this.orm.call(
        'account.move.line',
        'addisystems_reconcile',
        [this.state.bank_info.statement_id,resIds]

    )
    this.state.bank_info.reconciled_amount +=  this.Totalclickedamount
    this.state.bank_info.un_reconciled_amount -=  this.Totalclickedamount
    this.env.searchModel.trigger('update');
  }

 

}
AccountMoveLineReconcileController.template = "addis_systems_reconcillation.AccountMoveLineReconcileView"
AccountMoveLineReconcileController.components = Object.assign({}, ListController.components, {
    Dropdown, DropdownItem
});

export const AccountMoveLineReconcileView = {
    ...listView,
    Controller: AccountMoveLineReconcileController,
    buttonTemplate: "addis_systems_reconcillation.AccountMoveLineReconcileView.Buttons",
}

registry.category("views").add("addisystems_account_reconcile_view", AccountMoveLineReconcileView)