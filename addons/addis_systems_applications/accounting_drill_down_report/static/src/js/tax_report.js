/** @odoo-module **/

import { registry } from "@web/core/registry";
import {BaseDrilldownReport} from "@accounting_drill_down_report/js/base_report";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

const { DateTime } = luxon;
export class TaxReportOwl extends BaseDrilldownReport {
    static template = "accounting_drill_down_report.tax_report_owl";

    async setup() {
    super.setup()
    this.goto_general_ledgure = this.goto_general_ledgure.bind(this)

   }


    async set_target_move(target_move) {
        if (target_move=='all' && target_move==this.state.target_move){
            this.state.target_move='posted'
        }
        else{
            this.state.target_move=target_move
        }
        this.state.lines = await this.orm.call("addissystems.report_tax", "get_lines", [this.state]);

        
    }

    async goto_general_ledgure(tax_id) {
        // Import `DateTime` from Luxon if necessary
        const { DateTime } = luxon;
        const id = await this.orm.searchRead(
            "account.tax.repartition.line",
            [['tax_id', '=', tax_id], ['account_id', '!=', false]],
            ["account_id"]
        );
        
        const filteredAccounts = id.filter(item => item.account_id && item.account_id.length > 0);
        
        const accountIds = filteredAccounts.map(item => item.account_id[0]);        
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
        domain.push(['account_id','in',accountIds])
    
        // Return the action
        return await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Tax Audit'),
            target: 'new',
            domain: domain,
            context: {
                ...this.env.context, // Include existing context
                search_default_account_id: accountIds, // Add any default filters
            },
            res_model: 'account.move.line',
            views: [[false, 'tree']],
        });
    }
    
    async print_pdf(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'accounting_drill_down_report.report_tax',
            'report_file': 'accounting_drill_down_report.report_tax',
            'data': {
                'lines': this.state.lines || {},
                'report_name': 'Tax Report',
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': 'Tax Report',
            } // Missing closing brace for the 'data' object
        });
    }
    
    getxlsx(){
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': 'accounting_drill_down_report.report_tax_xlsx',
            'report_file': 'accounting_drill_down_report.report_tax_xlsx',
            'data': {
                'lines': this.state.lines || {},
                'report_name': 'Tax Report',
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': 'Tax Report',
            } // Missing closing brace for the 'data' object
        });
    }
    async get_financial_data(){
        this.report_name="Tax Report"
        this.state.lines = await this.orm.call("addissystems.report_tax", "get_lines", [this.state]);

    }

}
actionRegistry.add("tax_report_owl", TaxReportOwl);