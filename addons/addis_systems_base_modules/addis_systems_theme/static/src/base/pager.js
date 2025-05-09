/** @odoo-module */
import { useState, onWillUnmount } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { patch } from '@web/core/utils/patch';
import { session } from "@web/session";

import { Pager } from '@web/core/pager/pager';

patch(Pager.prototype, {
	setup() {
        super.setup();
        const autoLoad = browser.localStorage.getItem(
        	this.getAutoLoadStorageKey()
        )
        this.autoLoadInterval = false;
        this.autoLoadState = useState({
        	active: autoLoad,
        });
        if (autoLoad) {
        	this.setAutoLoad();
        }
        onWillUnmount(() => {
            this.clearAutoLoad();
        });
    },
    checkAutoLoadAvailability() {
    	return ['kanban', 'list'].includes(
    		this.env.config.viewType
    	);
    },
    getAutoLoadStorageKey() {
    	return (
    		'pager_autoload:' +
    		this.env.config.actionId +
    		',' +
    		this.env.config.viewId
    	);
    },
    getAutoLoadIntervalTimeout() {return session.pager_autoload_interval || 30000;},
    getAutoloadTooltip() {
    	return JSON.stringify({
    		active: this.autoLoadState.active,
    		interval: this.getAutoLoadIntervalTimeout() / 1000,
    		autoload: this.checkAutoLoadAvailability(),
    	});
    },
    setAutoLoad() {
    	this.autoLoadInterval = browser.setInterval(
	    	() => { this.navigate(0); },
	    	this.getAutoLoadIntervalTimeout()
    	);
    	if (this.env.config.actionId) {
    		browser.localStorage.setItem(
	            this.getAutoLoadStorageKey(), true
	        );
    	}
    },
    clearAutoLoad() {
    	if (this.autoLoadInterval) {
    		browser.clearInterval(this.autoLoadInterval);
    	}
    },
    toggleAutoLoad() {
    	this.clearAutoLoad();
    	browser.localStorage.removeItem(
            this.getAutoLoadStorageKey()
        );
    	if (this.checkAutoLoadAvailability()) {
        	this.autoLoadState.active = !this.autoLoadState.active;
        	if (this.autoLoadState.active) {
        		this.setAutoLoad();
        	}
    	}
    },
});
