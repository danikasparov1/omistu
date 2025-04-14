/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component,useRef, useState } from "@odoo/owl";
import { BlockUI } from "@web/core/ui/block_ui";
import { download } from "@web/core/network/download";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { DateTimePickerPopover } from "@web/core/datetime/datetime_picker_popover";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { session } from "@web/session";
import { getCurrency } from "@web/core/currency";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";


const actionRegistry = registry.category("actions");

export class BaseDrilldownReport extends Component {
    async setup() {
        this.orm = useService('orm');
        this.goto_general_ledgure = this.goto_general_ledgure.bind(this);
        this.set_filter_by = this.set_filter_by.bind(this);
        this.set_period_start = this.set_period_start.bind(this);
        this.set_period_end = this.set_period_end.bind(this);

        this.action = useService('action');
        this.company_name = "My Company (San Francisco)";
        this.currencySymbol = null;
        this.report_name = "Custom Report"
        this.state = useState({
            date_from:null,
            date_to:null,
            target_move:'posted',
            lines: {
            },
            period_start:null,
            period_end:null,
            journals:[],
            filter_by:"Date",
        });

        this.loadCurrencySymbol();
        const journals = await this.orm.searchRead("account.journal", [], ["name", "code", "type"]);
        this.state.journals = journals.map((journal) => {
            return { ...journal, selected: false }; // Add `selected: false` to each journal
        });
        this.period_selection = await this.orm.searchRead("account.fiscal.year", [], ["name", "date_from", "date_to"]);
        this.name="Custom Report"
        await this.get_default_values()
        await this.get_financial_data()
    }

    async goto_general_ledgure(id) {
        // Import `DateTime` from Luxon if necessary
        const { DateTime } = luxon;
    
        // Ensure domain is initialized
        let domain = [
            ['display_type', 'not in', ['line_section', 'line_note']],
            ['parent_state', '!=', 'cancel']
        ];
    
        // Convert Luxon DateTime to string in YYYY-MM-DD format
        if (this.state.target_move == "posted") {
            domain.push(['parent_state','=','posted'])
        }
        if (this.state.date_from) {
            const dateFrom = DateTime.fromMillis(this.state.date_from.ts).toISODate(); // Convert to 'YYYY-MM-DD'
            domain.push(['date', '>=', dateFrom]);
        }
        if (this.state.date_to) {
            const dateTo = DateTime.fromMillis(this.state.date_to.ts).toISODate(); // Convert to 'YYYY-MM-DD'
            domain.push(['date', '<=', dateTo]);
        }
        const jrnls=this.state.journals.filter((journal) => journal.selected).map((journal) => journal.id); 
        if(jrnls.length){
            domain.push(["journal_id", "in", jrnls])
        }
        // Return the action
        return await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('General Ledger'),
            target: 'new',
            domain: domain,
            context: {
                ...this.env.context, // Include existing context
                search_default_account_id: id, // Add any default filters
            },
            res_model: 'account.move.line',
            views: [[false, 'tree']],
        });
    }
    
    async get_default_values(){
    
    }

    async loadCurrencySymbol() {
        const result = await jsonrpc('/get_currency_symbol',{});
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
    
    async set_filter_by(fil) {
        this.state.filter_by=fil,
        this.state.date_from = null,
        this.state.date_to = null,
        this.state.period_from = null,
        this.state.period_end = null
        await this.get_financial_data()    }
    async set_date_from(date) {
        this.state.date_from=date
        await this.get_financial_data()
    }
    async set_date_to(date) {
            this.state.date_to=date
            await this.get_financial_data()
    
        }
        async set_target_move(target_move) {
            if (target_move=='all' && target_move==this.state.target_move){
                this.state.target_move='posted'
            }
            else{
                this.state.target_move=target_move
            }
            await this.get_financial_data()
    
            
        }


        async set_journals(journal_id) {
            // Find the journal with the matching id
            const journal = this.state.journals.find(jrnl => jrnl.id === journal_id);
            if (journal) {
                // Toggle the selected state
                journal.selected = !journal.selected;
                // Force the state to update (OWL will automatically handle this)
                this.state.journals = [...this.state.journals];
            }
            
            await this.get_financial_data()

        }

        async set_period_start(period_id){
            const period_start_selected = this.period_selection.find(per => per.id === period_id);
            this.state.period_start = period_start_selected
            const { DateTime } = luxon;
            this.state.date_from =  DateTime.fromISO(this.state.period_start.date_from);
            await this.get_financial_data()
        }

        async set_period_end(period_id){
            const period_end_selected = this.period_selection.find(per => per.id === period_id);
            this.state.period_end = period_end_selected
            const { DateTime } = luxon;
            this.state.date_to = DateTime.fromISO(this.state.period_end.date_from);
            await this.get_financial_data()
        }


        async print_pdf(ev) {
           alert("please override the method")
        }

        getxlsx(){
            alert("Over Ride THis Method")
        }

        async get_financial_data(){
            alert("please Override The Method")
        }

}
BaseDrilldownReport.components = { Dropdown, DropdownItem,DateTimePicker ,DateTimePickerPopover,DateTimeInput};
BaseDrilldownReport.template = "accounting_drill_down_report.base_template";