/** @odoo-module **/

import { registry } from "@web/core/registry";
import {BaseDrilldownReport} from "@accounting_drill_down_report/js/base_report";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

export class BankBookReport extends BaseDrilldownReport {
    async setup() {
        super.setup()
        this.toggle_lines = this.toggle_lines.bind(this)
        this.goto_journal_entry = this.goto_journal_entry.bind(this)

        if (!this.state.accounts) {
            this.state.accounts = []; // Initialize if not already defined
        }
        const accounts = await this.orm.call("addissystems.report_bankbook", "get_default_account_ids", []); 
        this.state.accounts = accounts.map((account) => {
            return { ...account, selected: false }; // Add `selected: false` to each journal
        });

    }


    async set_accounts(accountId) {
        const account = this.state.accounts.find(acct => acct.id === accountId);
        if (account) {
            // Toggle the selected state
            account.selected = !account.selected;
            // Force the state to update (OWL will automatically handle this)
            this.state.accounts = [...this.state.accounts];
        }
        await this.get_financial_data()
    }

    async toggle_lines(line){
        const currentSelected = this.state.lines[line].selected;
        this.state.lines[line].selected = !currentSelected;
    }

    async goto_journal_entry(id) {
        return await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Journal Entries'),
            target: 'current',
            res_model: 'account.move',
            res_id:id,
            views: [[false, 'form']],
        });
    }

    async getxlsx(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': 'accounting_drill_down_report.report_bankbook_xlsx',
            'report_file': 'accounting_drill_down_report.report_bankbook_xlsx',
            'data': {
                'report_name': "Bank Book xlsx",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Bank Book",
            } // Missing closing brace for the 'data' object
        });
    }

    async print_pdf(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'accounting_drill_down_report.report_bankbook',
            'report_file': 'accounting_drill_down_report.report_bankbook',
            'data': {
                'report_name': "Bank Book",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Bank Book",
            } // Missing closing brace for the 'data' object
        });
    }


    async get_financial_data(){
        this.report_name = "Bank Book Report"
        this.state.lines = await this.orm.call("addissystems.report_bankbook", "get_lines", [this.state]); 
        

    }

    

}

BankBookReport.template = "accounting_drill_down_report.bank_book_report_owl";
actionRegistry.add("addisystems_bank_book", BankBookReport);