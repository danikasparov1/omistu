/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BaseDrilldownReport } from "@accounting_drill_down_report/js/base_report";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

export class AgedReceivableReport extends BaseDrilldownReport {
    async setup() {
        this.action = useService('action');
        await super.setup();
        this.toggle_lines = this.toggle_lines.bind(this);
        this.goto_journal_entry = this.goto_journal_entry.bind(this);
        this.set_account_type = this.set_account_type.bind(this);
        if (!this.state.partners) {
            this.state.partners = []; // Initialize if not already defined
        }
        if (!this.state.account_type) {
            this.state.account_type = { name: 'customer', label: 'Receivable Accounts' };
        }

        const partners = await this.orm.searchRead("res.partner", [], ["name"]);
        this.state.partners = partners.map((partner) => {
            return { ...partner, selected: false }; // Add `selected: false` to each journal
        });
    }

    async set_partners(partnerId) {
        const Partner = this.state.partners.find(ptnl => ptnl.id === partnerId);
        if (Partner) {
            // Toggle the selected state
            Partner.selected = !Partner.selected;
            // Force the state to update (OWL will automatically handle this)
            this.state.partners = [...this.state.partners];
        }
        await this.get_financial_data();
    }

    async set_account_type(accountType) {
        this.state.account_type = accountType;
        await this.get_financial_data();
    }

    async toggle_lines(line) {
        const currentSelected = this.state.lines[line].selected;
        this.state.lines[line].selected = !currentSelected;
    }

    async goto_journal_entry(id) {
        return await this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Journal Entries'),
            target: 'current',
            res_model: 'account.move',
            res_id: id,
            views: [[false, 'form']],
        });
    }

    async getxlsx(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': 'accounting_drill_down_report.report_aged_receivable_xlsx',
            'report_file': 'accounting_drill_down_report.report_aged_receivable_xlsx',
            'data': {
                'report_name': "Aged Receivable xlsx",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Aged Receivable",
            }
        });
    }

    async print_pdf(ev) {
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'accounting_drill_down_report.report_aged_receivable',
            'report_file': 'accounting_drill_down_report.report_aged_receivable',
            'data': {
                'report_name': "Aged Receivable",
                'data': {
                    ...this.state,
                    date_from: this.state.date_from ? this.state.date_from.toFormat('yyyy-MM-dd') : null,
                    date_to: this.state.date_to ? this.state.date_to.toFormat('yyyy-MM-dd') : null,
                },
                'display_name': "Aged Receivable",
            }
        });
    }

    async get_financial_data() {
        this.report_name = "Aged Receivable Report";
        this.state.lines = await this.orm.call("addissystems.report_agedreceivable", "get_lines", [this.state]);
    }
}

AgedReceivableReport.template = "accounting_drill_down_report.aged_receivable_report_owl";
actionRegistry.add("addisystems_aged_receivable", AgedReceivableReport);