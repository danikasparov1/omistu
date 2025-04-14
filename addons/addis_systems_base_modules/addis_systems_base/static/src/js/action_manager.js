/** @odoo-module */
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import { BlockUI } from "@web/core/ui/block_ui";
import { session } from "@web/session";

registry.category("ir.actions.report handlers").add("xlsx", async (action, options, env) => {
    if (action.report_type === 'excel') {
        const actionContext = action.context || {};
        console.log(env)
        BlockUI
        var def = $.Deferred();
        await download({
            url: '/report/excel/',
            data: action.data,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: () => unblockUI,
        });
    }
});