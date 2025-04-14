/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component,useRef, useState } from "@odoo/owl";
import { BlockUI } from "@web/core/ui/block_ui";
import { download } from "@web/core/network/download";
const actionRegistry = registry.category("actions");

export class InventoryProductExpiry extends Component {
    static template = "addis_systems_stock_reports.inventory_product_expiry";

   async setup() {
    super.setup(...arguments);
    this.initial_render = true;
    this.orm = useService('orm');
    this.action = useService('action');
    this.tbody = useRef('tbody');
    this.end_date = useRef('date_to');
    this.start_date = useRef('date_from');
    this.state = useState({
        data:null,
        message:"here we go",
        date_from: null,
        date_to: null,
        included_products:[],
        selected_date:null
    
    })
    this.filter_data=useState({
        date_from:null,
        date_to:null,
        product_ids:[],
        search_text:null,
        date_range:null
    })
    this.excluded_product=useState([])
    this.wizard_id = await this.orm.call("inventory.expiry.product.wizard", "create", [{}]) | null;
    this.load_data(self.initial_render = true);

    }

    async load_data() {
        /**
         * Loads the data for the Inventory product report.
         */
            var self = this;
            var action_title = self.props.action.display_name;
            try {
                var self = this;
                let data = await self.orm.call("inventory.expiry.product.wizard", "get_products", []);
                self.state.data = data
                console.log(data)
                self.state.title = action_title
                self.state.filter_data = [""],
                self.included_products=[]
                self.filter_data.product_ids= await self.orm.call("inventory.expiry.product.wizard", "get_products_list", []);
            }
            catch (el) {
                window.location.href
            }
        }
    
    async get_data_with_filter(){
        this.state.data= await this.orm.call("inventory.expiry.product.wizard", "get_products_list_with_filter", [this.filter_data.date_range,this.filter_data.date_from,this.filter_data.date_to,this.state.included_products]);

    }



    async print_pdf(ev) {
        ev.preventDefault();
        return this.action.doAction({
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'addis_systems_stock_reports.invenotory_product_expiry',
            'report_file': 'addis_systems_stock_reports.invenotory_product_expiry',
            'data': {
                'data': this.state||{},
                'report_name': this.props.action.display_name,
                'filtered_dates':this.filter_data,
                'filters':this.filter_data
            },
            'display_name': this.props.action.display_name,
        });
    }
    async print_xlsx(ev) {
        var self = this;
        BlockUI;
        this.action.doAction({
            type: "ir.actions.report",
            report_type: "xlsx",
            report_name:"addis_systems_stock_reports.report_pro_excel",
            report_file: "addis_systems_stock_reports.report_pro_excel",
            context:{},
            data:{options:self.state.data,filters:this.filter_data} ||{},
            display_name: "here we go",
            attachment_use:false
        });
       
    }
    async apply_date(ev){
        /**
         * Applies the selected date filter and triggers data loading based on the selected filter value.
         * @param {Event} ev - The event object triggered by the date selection.
         * @returns {Promise<void>} - A promise that resolves when the data is loaded.
         */
            self = this
            if (ev.target.name === 'start_date') {
                this.filter_data.date_range=null
                this.filter_data = {
                        ...this.filter_data,
                        date_from: ev.target.value
                    };
            } else if (ev.target.name === 'end_date') {
                this.filter_data.date_range=null
                    this.filter_data = {
                        ...this.filter_data,
                        date_to: ev.target.value
                    };

            } else if (ev.target.attributes["data-value"].value == 'month') {
                    this.filter_data = {
                        ...this.filter_data,
                        date_range: ev.target.attributes["data-value"].value
                    };
            } else if (ev.target.attributes["data-value"].value == 'year') {
                this.filter_data = {
                    ...this.filter_data,
                    date_range: ev.target.attributes["data-value"].value
                };
            } else if (ev.target.attributes["data-value"].value == 'first-quarter') {
                this.filter_data = {
                    ...this.filter_data,
                    date_range: ev.target.attributes["data-value"].value
                };
            } else if (ev.target.attributes["data-value"].value == 'second-quarter') {
                this.filter_data = {
                    ...this.filter_data,
                    date_range: ev.target.attributes["data-value"].value
                };
            } else if (ev.target.attributes["data-value"].value == 'third-quarter') {
                this.filter_data = {
                    ...this.filter_data,
                    date_range: ev.target.attributes["data-value"].value
                };
            } else if (ev.target.attributes["data-value"].value == 'last-quarter') {
                this.filter_data = {
                    ...this.filter_data,
                    date_range: ev.target.attributes["data-value"].value
                };
            }
            self.get_data_with_filter()
        }
        async apply_product(ev) {
            if (ev) {
                const product_name = ev.target.attributes["product_name"].value;
                const product_id = ev.target.attributes["product_id"].value;
        
                // Use arrow function to maintain the correct 'this' context
                const exists = this.state.included_products.some(product => product.product_id === product_id);
        
                if (!exists) {
                    // Add the new product to the included_products array
                    this.state.included_products = [
                        ...this.state.included_products,
                        { product_id, product_name }
                    ];
        
                    // Filter product_ids in filter_data to exclude products already in included_products
                    this.filter_data.product_ids = this.filter_data.product_ids.filter(product => 
                        !this.state.included_products.some(excludeProduct => excludeProduct.product_id === product.product_id)
                    );
        
                    console.log(this.filter_data.product_ids, this.state.included_products);
                }
                this.get_data_with_filter()
            }

        }
        



        async deleteme(ev){
            self=this
            if(ev.target.attributes["product_id"].value){
                const product_name = ev.target.attributes["product_name"].value
                const product_id=ev.target.attributes["product_id"].value
                const exists = self.state.included_products.some(product => product.product_id === ev.target.attributes["product_id"].value);
                console.log(product_name,product_id,exists,self.state.included_products)
                if (exists) {
                    // Push the new product to the array if it does not exist
                    self.state.included_products = self.state.included_products.filter(product=>product.product_id!==product_id)
                    this.filter_data.product_ids = [
                        ...this.filter_data.product_ids,
                        { product_id, product_name }
                    ];
                    this.get_data_with_filter()

                }
                
            }
            

        }





    
}
actionRegistry.add("inventory_product_expiry", InventoryProductExpiry);