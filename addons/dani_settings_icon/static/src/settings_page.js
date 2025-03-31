/** @odoo-module **/
import { SettingsPage } from "@web/webclient/settings_form_view/settings/settings_page";
import { patch } from "@web/core/utils/patch";
import { ActionSwiper } from "@web/core/action_swiper/action_swiper";

import { Component, useState, useRef, useEffect } from "@odoo/owl";


patch(SettingsPage.prototype, {
    setup() {
      super.setup();
      if (this.props.modules) {
        this.state.selectedTab = this.props.initialTab || this.props.modules[0].key;
        this.props.modules.forEach(module => {
            module.newKey = '/dani_settings_icon/static/src/icon/icon.png';
        });
    }
    },
  });