/** @odoo-module **/

import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { STATIC_ACTIONS_GROUP_NUMBER } from "@web/search/action_menus/action_menus";
import { archParseBoolean } from "@web/views/utils";

const cogMenuRegistry = registry.category("cogMenu");

export class ExportPeachTree extends Component {
    static template = "addis_systems_peachtree_integration.ExportAll";
    static components = { DropdownItem };
    async onDirectExportData() {
        this.env.searchModel.trigger('direct-export-pdf-data');
    }
}

export const exportPeachtreeItem = {
    Component: ExportPeachTree,
    groupNumber: STATIC_ACTIONS_GROUP_NUMBER,
    isDisplayed: async (env) =>
        env.config.viewType === "listk" &&
        !env.model.root.selection.length &&
        await env.model.user.hasGroup("base.group_allow_export") &&
        archParseBoolean(env.config.viewArch.getAttribute("export_xlsx"), true),
}
cogMenuRegistry.add("export-all-peachtree-menu", exportPeachtreeItem, { sequence: 11 });