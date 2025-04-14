/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useSetupAction } from "@web/webclient/actions/action_hook";
import { useEnrichWithActionLinks } from "@web/webclient/actions/reports/report_hook";
import { Component, useRef, useSubEnv } from "@odoo/owl";
import { ReportAction } from "@web/webclient/actions/reports/report_action";
import {patch} from "@web/core/utils/patch";
patch(ReportAction.prototype,{
    print_excel_inventory() {
        console.log("here we go" ,this.props)
        this.action.doAction({
            type: "ir.actions.report",
            report_type: "xlsx",
            report_name:this.props.report_name+'_excel',
            report_file: this.props.report_file,
            data: this.props.data || {},
            context: this.props.context || {},
            display_name: this.title,
            attachment_use:false
        });
}

});