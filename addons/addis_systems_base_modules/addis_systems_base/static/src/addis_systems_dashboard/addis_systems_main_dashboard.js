/** @odoo-module */

import { registry } from "@web/core/registry"
import { AddisSystemsPendingInvitationsKpiCard, AddisSystemsActiveUsersKpiCard, AddisSystemsBlacklistedEmailKpiCard, AddisSystemsBanksKpiCard, AddisSystemsContactsKpiCard } from "./kpi_card/addis_systems_kpi_card"
import { AddisSystemsAdministratorDashboardConnected, AddisSystemsAdministratorDashboardOutgoingMail, AddisSystemsAdministratorDashboardOdooMessages } from "./charts/addis_systems_charts"
import { loadJS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted, useState } = owl

export class AddisSystemsAdministratorDashboard extends Component {
    setup(){
        this.state = useState({
            aa: {
                value : 100,
                percent: -90,
            },
            bb: {
                value : 200,
                percent: 80,
            },
            cc: {
                value : 300,
                percent: 70,
            },
            dd: {
                value : 400,
                percent: 60,
            }
        })
    }
}

AddisSystemsAdministratorDashboard.template = "addis_systems_base.AddisSystemsAdministratorDashboardTemplate"
AddisSystemsAdministratorDashboard.components = {
    AddisSystemsPendingInvitationsKpiCard, AddisSystemsActiveUsersKpiCard, AddisSystemsBlacklistedEmailKpiCard, AddisSystemsBanksKpiCard, AddisSystemsContactsKpiCard,
    AddisSystemsAdministratorDashboardConnected, AddisSystemsAdministratorDashboardOutgoingMail, AddisSystemsAdministratorDashboardOdooMessages 
}

registry.category("actions").add("addis_systems_base.addis_systems_administrator_dashboard", AddisSystemsAdministratorDashboard)