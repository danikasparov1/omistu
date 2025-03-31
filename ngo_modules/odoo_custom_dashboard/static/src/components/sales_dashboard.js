/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl

export class OwlSalesDashboard extends Component {
    setup(){
      this.state = useState({
                quotations: {
                    value:10,
                    percentage:6,
                },
                period:90,
            })
            this.orm = useService("orm")
//            this.actionService = useService("action")

            onWillStart(async ()=>{
                this.getDates()
                await this.getQuotations()
//                await this.getOrders()
            })
    }
    async onChangePeriod(){
        this.getDates()
        await this.getQuotations()
//        await this.getOrders()
    }

    getDates(){
    console.log(this.state.period)
//       this.state.current_date = fields.datetime.now() + datetime.timedelta(-1).strftime('%Y-%m-%d')
//       this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('L')
    }

    async getQuotations(){
//        let domain = [['state', 'in', ['registered']]]
//        if (this.state.period > 0){
////            domain.push(['create_date','>', this.state.current_date])
//        }
        const data = await this.orm.searchCount("g2b.beneficiary.info", [])
        this.state.quotations.value =  data
//        // previous period
        let prev_domain = [['state', 'in', ['confirmed']]]
        let vouch_domain = [['state', 'in', ['confirmed','redeemed']]]
        let prev_domain1 = [['status', 'in', ['confirmed']]]
//        if (this.state.period > 0){
////            prev_domain.push(['date_order','>', this.state.previous_date], ['date_order','<=', this.state.current_date])
//        }
        const prev_data = await this.orm.searchCount("g2b.beneficiary.info", prev_domain)
        const benefit = await this.orm.searchCount("g2b.benefit.info", [])
        const benefit_conf = await this.orm.searchCount("g2b.benefit.info", prev_domain1)
        const voucher = await this.orm.searchCount("g2b.voucher.info", [])
        const voucher_conf = await this.orm.searchCount("g2b.voucher.info", vouch_domain)
        const provider = await this.orm.searchCount("g2b.provider.info", [])
        const provider_conf = await this.orm.searchCount("g2b.provider.info", prev_domain)
        const percentage = (prev_data/data) * 100
        const benefit_per=(benefit_conf/benefit)*100
        const voucher_per=(voucher_conf/voucher)*100
        const provider_per=(provider_conf/provider)*100
        this.state.quotations.percentage = percentage.toFixed(2)
        this.state.quotations.benefit = benefit
        this.state.quotations.benefit_per = benefit_per.toFixed(2)
        this.state.quotations.voucher = voucher
        this.state.quotations.voucher_per = voucher_per.toFixed(2)
        this.state.quotations.provider = provider
        this.state.quotations.provider_per = provider_per.toFixed(2)
    }


}

OwlSalesDashboard.template = "owl.OwlSalesDashboard"
OwlSalesDashboard.components = { KpiCard, ChartRenderer }

registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard)