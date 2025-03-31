/** @odoo-module **/

import { NavBar } from '@web/webclient/navbar/navbar';
import { useService } from '@web/core/utils/hooks';
import { patch } from "@web/core/utils/patch";
import { useEnvDebugContext } from "@web/core/debug/debug_context";

patch(NavBar.prototype, {
    setup() {
        super.setup();

        this.debugContext = useEnvDebugContext();
        this.rpc = useService('rpc');
        this.companyService = useService("company");
        this.currentCompany = this.companyService.currentCompany;
        this.menuService = useService("menu");

        // Bind the event handler
        this.onMenuClick = this.onMenuClick.bind(this);
    },

    toggleSidebar(ev) {
        $(ev.currentTarget).toggleClass('visible');
        $('.nav-wrapper-bits').toggleClass('toggle-show');
    },

    onMenuClick(ev) {
        const menuItem = ev.target.closest('.custom-menu-item');
        if (menuItem) {
            ev.preventDefault();
            ev.stopPropagation();

            // Toggle the collapse state
            const target = menuItem.getAttribute('data-bs-target');
            const collapseElement = document.querySelector(target);
            if (collapseElement) {
                const collapse = new bootstrap.Collapse(collapseElement, { toggle: true });
            }

            // Trigger the action
            const actionId = menuItem.getAttribute('data-action-id');
            if (actionId) {
                this.menuService.selectMenu(actionId);
            }
        }
    },

    mounted() {
        // Add the event listener after the component is mounted
        this.el.addEventListener('click', this.onMenuClick);
    },

    willUnmount() {
        // Clean up the event listener when the component is destroyed
        this.el.removeEventListener('click', this.onMenuClick);
    }
});