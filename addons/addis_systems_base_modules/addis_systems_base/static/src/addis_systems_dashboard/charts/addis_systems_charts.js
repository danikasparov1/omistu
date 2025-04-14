/** @odoo-module */

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useRef, onMounted, useState } = owl

export class AddisSystemsAdministratorDashboardConnected extends Component {
  setup() {
    this.orm = useService("orm");
    this.chartRef = useRef("addis_systems_administrator_dashboard_connected_users")
    
    onWillStart(async () => {
      // const res = await this.orm.searchCount('hr.employee', [])
      // console.log(res)
      // console.log(moment().subtract(10, 'days').calendar())
      await loadJS("/addis_systems_theme/static/src/js/chart.umd.min.js")
    })

    onMounted(() => this.renderChart())
  }

  async renderChart() {
    const current_date = new Date().setHours(1, 0, 0, 0); // 8:00 AM
    const previous_date = new Date().setHours(1, 0, 0, 0); // 8:00 AM

    const getDailyConnectedUsers = async (current_date, previous_date) => {
      let startTime = new Date().setHours(1, 0, 0, 0); // 8:00 AM
      let endTime = new Date().setHours(23, 59, 59, 0); // 8:00 PM

      let date_range = []
      let today_data = []
      let yesterday = []

      console.log(startTime, endTime)

      for (let currentTime = startTime; currentTime <= endTime; currentTime += 3600000) {
        const timeString = new Date(currentTime).toLocaleTimeString();

        let today_orm = await this.orm.searchCount('hr.employee', [])
        let bb = await this.orm.searchCount('hr.department', [])
        
        date_range.push(timeString);
        today_data.push(Math.floor(Math.random() * 4000));
        yesterday.push(Math.floor(Math.random() * 4000));

        // const user = await fetchUserData(id);
      }

      return { times: date_range, today: today_data, yesterday:yesterday}; // Returns an object literal
    }
    

    const test = await getDailyConnectedUsers(current_date, previous_date)
    console.log(test)

    new Chart(this.chartRef.el,
      {
        type: this.props.type,
        data: {
          labels: test.times,
          datasets: [
            {
              label: 'Today',
              data: test.today,
              hoverOffset: 4
            }, {
              label: 'Yesterday',
              data: test.yesterday,
              hoverOffset: 4
            }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
            },
            title: {
              display: true,
              text: this.props.title,
              position: 'bottom',
            }
          }
        },
      }
    );
  }
}

export class AddisSystemsAdministratorDashboardOutgoingMail extends Component {
  setup() {
    this.chartRef = useRef("addis_systems_administrator_dashboard_outgoing_mail")
    
    onWillStart(async () => {
      await loadJS("/addis_systems_theme/static/src/js/chart.umd.min.js")
    })

    onMounted(() => this.renderChart())
  }

  renderChart() {
    new Chart(this.chartRef.el,
      {
        type: this.props.type,
        data: {
          labels: [
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '10'
          ],
          datasets: [
            {
              label: 'Last Month',
              data: [283, 112, 231, 211, 22, 10, 222, 111, 10, 123],
              hoverOffset: 4
            }, {
              label: 'This Month',
              data: [300, 50, 10, 300, 50, 10, 300, 50, 10, 300],
              hoverOffset: 4
            }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
            },
            title: {
              display: true,
              text: this.props.title,
              position: 'bottom',
            }
          }
        },
      }
    );
  }
}

export class AddisSystemsAdministratorDashboardOdooMessages extends Component {
  setup() {
    this.chartRef = useRef("addis_systems_administrator_dashboard_outgoing_mail")
    
    onWillStart(async () => {
      await loadJS("/addis_systems_theme/static/src/js/chart.umd.min.js")
    })

    onMounted(() => this.renderChart())
  }

  renderChart() {
    new Chart(this.chartRef.el,
      {
        type: this.props.type,
        data: {
          labels: [
            '1',
            '2',
            '3',
            '4',
            '4',
            '5'
          ],
          datasets: [
            {
              label: 'Last Month',
              data: [283, 112, 231, 211, 22, 10, 222, 111, 10, 123],
              hoverOffset: 4
            }, {
              label: 'This Month',
              data: [300, 50, 10, 300, 50, 10, 300, 50, 10, 300],
              hoverOffset: 4
            }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
            },
            title: {
              display: true,
              text: this.props.title,
              position: 'bottom',
            }
          }
        },
      }
    );
  }
}

AddisSystemsAdministratorDashboardConnected.template = "addis_systems_base.AddisSystemsAdministratorDashboardConnected"
AddisSystemsAdministratorDashboardOutgoingMail.template = "addis_systems_base.AddisSystemsAdministratorDashboardOutgoingMail"
AddisSystemsAdministratorDashboardOdooMessages.template = "addis_systems_base.AddisSystemsAdministratorDashboardOdooMessages"
