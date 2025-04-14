/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import {BaseDrilldownReport} from "@accounting_drill_down_report/js/base_report";


const actionRegistry = registry.category("actions");

export class ProfitAndLossReport extends BaseDrilldownReport {
    async setup() {
        super.setup()
        this.toggle_lines =this.toggle_lines.bind(this)


    }

    async toggle_lines(line,line_2){
        const currentSelected = this.state.lines[line].datasets[line_2].selected;
        this.state.lines[line].datasets[line_2].selected = !currentSelected;
    }

    async get_financial_data(){
        this.report_name = "Profit and Loss Report"
        this.state.lines = await this.orm.call("addissystems.report_profitandloss", "get_lines", [this.state]); 
        

    }


    async print_pdf(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'accounting_drill_down_report.report_profit_loss',
            'report_file': 'accounting_drill_down_report.report_profit_loss',
            'data': {
                'report_name': "Profit and Loss",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Profit and Loss",
            } // Missing closing brace for the 'data' object
        });
    }
    
    getxlsx(){
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': 'accounting_drill_down_report.report_profit_loss_xlsx',
            'report_file': 'accounting_drill_down_report.report_profit_loss_xlsx',
            'data': {
                'report_name': "Profit and Loss Excel",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Profit and Loss Excel",
            } // Missing closing brace for the 'data' object
        });
    }

    
}

ProfitAndLossReport.template = "accounting_drill_down_report.profit_and_loss_report_owl";
actionRegistry.add("addisystems_proft_and_loss", ProfitAndLossReport);