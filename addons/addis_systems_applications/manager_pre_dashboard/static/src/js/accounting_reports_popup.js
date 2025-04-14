// // /** @odoo-module **/

// // import { useState } from "@odoo/owl";
// // // import { Dialog } from "@web/core/dialog/dialog";
// // import { Component, mount } from "@odoo/owl";
// // import { registry } from "@web/core/registry";
// // import { Dialog } from "@web/core/dialog/dialog";

// // class AccountingReportsPopup extends Component {
// //     setup() {
// //         this.state = useState({
// //             open: true, // Initial state of the modal
// //         });
// //     }

// //     // Close modal handler
// //     closeModal() {
// //         this.state.open = false;
// //     }
// // }

// // AccountingReportsPopup.template = "DynamicAccountingReportsTemplate";

// // // Register the action
// // odoo.define("manager_pre_dashboard.accounting_reports_popup_action", function (require) {
// //     const { registry } = require("@web/core/registry");
// //     const { AccountingReportsPopup } = require("manager_pre_dashboard.accounting_reports_popup");
// //     console.log("AccountingReportsPopup", AccountingReportsPopup);
// //     const actionRegistry = registry.category("actions");
// //     actionRegistry.add("accounting_reports_popup", AccountingReportsPopup);
// // });



// /** @odoo-module **/

// import { registry } from "@web/core/registry";
// import { Dialog } from "@web/core/dialog/dialog";

// const actionRegistry = registry.category("actions");

// export class AccountingReportsPopup extends Dialog {
//     setup() {
//         super.setup();
//     }

//     async onActionClick(event) {
//         const action = event.currentTarget.dataset.action;
//         console.log("Action", action);
//         if (action) {
//             await this.action.doAction(action);
//         }
//     }
// }

// AccountingReportsPopup.template = "manager_pre_dashboard.AccountingReportsPopup";
// actionRegistry.add("manager_pre_dashboard.accounting_reports_popup", AccountingReportsPopup);


/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Dialog } from "@web/core/dialog/dialog";

const actionRegistry = registry.category("actions");

export class AccountingReportsPopup extends Dialog {
    setup() {
        super.setup();
    }

    async onActionClick(event) {
        const action = event.currentTarget.dataset.action;
        console.log("Action", action);
        if (action) {
            await this.action.doAction(action);
        }
    }
}

AccountingReportsPopup.template = "manager_pre_dashboard.AccountingReportsPopup";
actionRegistry.add("manager_pre_dashboard.accounting_reports_popup", AccountingReportsPopup);