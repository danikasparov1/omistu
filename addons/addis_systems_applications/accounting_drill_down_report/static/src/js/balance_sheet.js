/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import {BaseDrilldownReport} from "@accounting_drill_down_report/js/base_report";


const actionRegistry = registry.category("actions");

export class BalanceSheetReportOwl extends BaseDrilldownReport {
    async setup() {
        super.setup()
        this.toggle_lines =this.toggle_lines.bind(this)
        this.report_name = "Balance Sheet Report"
        this.action = useService('action');
        this.goto_general_ledgure = this.goto_general_ledgure.bind(this)


    }

        async print_pdf(ev) {
            return this.action.doAction({
                'type': 'ir.actions.report',
                'report_type': 'qweb-pdf',
                'report_name': 'accounting_drill_down_report.report_balancesheet',
                'report_file': 'accounting_drill_down_report.report_balancesheet',
                'data': {
                    'report_name': "Balance Sheet",
                    'data': {
                        ...this.state,
                        date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                        date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                    },
                    'display_name': "Balance Sheet",
                } // Missing closing brace for the 'data' object
            });
        }
        
        getxlsx(){
            return this.action.doAction({
                'type': 'ir.actions.report',
                'report_type': 'xlsx',
                'report_name': 'accounting_drill_down_report.report_balancesheet_xlsx',
                'report_file': 'accounting_drill_down_report.report_balancesheet_xlsx',
                'data': {
                    'report_name': "Balance Sheet Excel",
                    'data': {
                        ...this.state,
                        date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                        date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                    },
                    'display_name': "Balance Sheet Excel",
                } // Missing closing brace for the 'data' object
            });
        }

        async toggle_lines(line,line_2){
            const currentSelected = this.state.lines[line].datasets[line_2].selected;
            this.state.lines[line].datasets[line_2].selected = !currentSelected;
        }

        async get_financial_data(){
            this.state.lines = await this.orm.call("addissystems.report_balancesheet", "get_lines", [this.state]); 
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

}
BalanceSheetReportOwl.template = "accounting_drill_down_report.balance_sheet_report_owl";
actionRegistry.add("balance_sheet_report_owl", BalanceSheetReportOwl);