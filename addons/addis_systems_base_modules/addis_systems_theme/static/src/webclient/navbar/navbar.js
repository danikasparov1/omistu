/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { useService } from '@web/core/utils/hooks';

import { NavBar } from '@web/webclient/navbar/navbar';
import { AppsBar } from '@addis_systems_theme/webclient/appsbar/appsbar';
import { AppsMenu } from "@addis_systems_theme/webclient/appsmenu/appsmenu";

patch(NavBar.prototype, {
	setup() {
        super.setup();
        this.appMenuService = useService('app_menu');
    },
	getAppsMenuItems() {
	    const currentApp = this.menuService.getCurrentApp();
		const menuItems = this.menuService.getApps().map((menu) => {
			const appsMenuItem = {
				id: menu.id,
				name: menu.name,
				xmlid: menu.xmlid,
				appID: menu.appID,
				actionID: menu.actionID,
				href: this.getMenuItemHref(menu),
				action: () => this.menuService.selectMenu(menu),
				active: currentApp && menu.id === currentApp.id,
			};
		    if (menu.webIconData) {
		        const prefix = (
		        	menu.webIconData.startsWith('P') ? 
	    			'data:image/svg+xml;base64,' : 
					'data:image/png;base64,'
	            );
		        appsMenuItem.webIconData = (
	    			menu.webIconData.startsWith('data:image') ? 
					menu.webIconData : 
					prefix + menu.webIconData.replace(/\s/g, '')
	            );
		    }
			return appsMenuItem;
		});
		return menuItems;
    },
});


patch(NavBar, {
    components: {
        ...NavBar.components,
        AppsBar,
		AppsMenu
    },
});
