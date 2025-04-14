/** @odoo-module */

const { Component } = owl

export class AddisSystemsPendingInvitationsKpiCard extends Component {}
export class AddisSystemsActiveUsersKpiCard extends Component {}
export class AddisSystemsBlacklistedEmailKpiCard extends Component {}
export class AddisSystemsBanksKpiCard extends Component {}
export class AddisSystemsContactsKpiCard extends Component {}

AddisSystemsPendingInvitationsKpiCard.template = "addis_systems_base.AddisSystemsPendingInvitationsKpiCard"
AddisSystemsActiveUsersKpiCard.template = "addis_systems_base.AddisSystemsActiveUsersKpiCard"
AddisSystemsBlacklistedEmailKpiCard.template = "addis_systems_base.AddisSystemsBlacklistedEmailKpiCard"
AddisSystemsBanksKpiCard.template = "addis_systems_base.AddisSystemsBanksKpiCard"
AddisSystemsContactsKpiCard.template = "addis_systems_base.AddisSystemsContactsKpiCard"