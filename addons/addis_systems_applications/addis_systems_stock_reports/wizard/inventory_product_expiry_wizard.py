
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from odoo.tools.misc import get_lang
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
class InventoryProductExpiryReportWizard(models.TransientModel):
    _name="inventory.expiry.product.wizard"
    _description="Addissystems Stock expiry report"
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)
    product_ids=fields.Many2many(comodel_name="product.template", string="Filter Products")
    def _build_contexts(self, data):
        result = {}
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['product_ids'] = data['form']['product_ids'] or  False
        return result
    def _print_report(self, data):
        raise NotImplementedError()
    
    @api.model
    def get_lines(self,product):
        domain=[('product_id','=',product[0].id)]
        x=self.env['stock.lot'].search(domain)
        return x
    @api.model
    def filter_js(self,filters):
        return []
    
    @api.model
    def get_line_js(self,product_id):
        domain=[('product_id','=',product_id)]
        lots=self.env['stock.lot'].search(domain)
        lots_dict=[{
            "lot_id":lot.id,
            "lot_name":lot.name,
            "expiration_date":lot.expiration_date
        }
        for lot in lots]
        return lots_dict
    
    def get_data(self,products):
        data=[


        ]
        for product in products:
            line = {
            "product_id": str(product[0].id),  # Store the product ID as a string here
            "product_name": product[0].name,  # Store the product name separately
            "lots": self.get_line_js(product[0].id),  # Store the lots using your function
            }
            data.append(line)
        return data



    @api.model
    def get_products(self):
        lines = self.env['stock.lot']._read_group([], ['product_id'])
        return self.get_data(lines)
    def generate_report_html(self):
        self.ensure_one()
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_html').report_action(self)
    
    @api.model
    def get_products_list(self):
        products = self.env['stock.lot']._read_group([], ['product_id'])
        return    [{
                "product_id": str(product[0].id),  # Store the product ID as a string here
                "product_name": product[0].name,
            } for product in products
        ]
    


    def fliter_product(self,products=[],date_from=None,date_to=None):
        data=[


        ]
        for product in products:
            line = {
            "product_id": str(product[0].id),  # Store the product ID as a string here
            "product_name": product[0].name,  # Store the product name separately
            "lots": self.get_line_js(product[0].id),  # Store the lots using your function
            }
            data.append(line)
        return []
    @api.model
    def get_products_rep(self,included_products):
        if included_products:
            ids=[product["product_id"] for product in included_products]
            products=self.env['product.product'].browse(ids)
            return products
        ids = [product[0].id for product in self.env['stock.lot']._read_group([], ['product_id'])]
        products=self.env['product.product'].browse(ids)
        return products
        
    def get_date_range(self,date_str):
        domain = []
    
        # Current date for reference
        today = date.today()
        
        if date_str == "month":
            # Current month range
            start_date = today.replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)

        elif date_str == "year":
            # Current year range
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)

        elif date_str == "first-quarter":
            # First quarter (January - March)
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=3, day=31)

        elif date_str == "second-quarter":
            # Second quarter (April - June)
            start_date = today.replace(month=4, day=1)
            end_date = today.replace(month=6, day=30)

        elif date_str == "third-quarter":
            # Third quarter (July - September)
            start_date = today.replace(month=7, day=1)
            end_date = today.replace(month=9, day=30)

        elif date_str == "last-quarter":
            # Last quarter (October - December)
            start_date = today.replace(month=10, day=1)
            end_date = today.replace(month=12, day=31)

        else:
            raise ValueError(f"Unknown date_str: {date_str}")

        # Add the calculated date range to the domain
        domain += [("expiration_date", ">=", start_date), ("expiration_date", "<=", end_date)]
        
        return domain
    
    def get_date_range_domain(self,date_from=None, date_to=None):
        # Initialize the domain list
        domain = []

        # Convert date strings to datetime objects if they are provided
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            domain += [("expiration_date", ">=", date_from)]
        
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
            domain += [("expiration_date", "<=", date_to)]

        return domain
    

    def get_formatted_data(self,domain):
        data=[]
        products= self.env['stock.lot']._read_group(domain, ['product_id'])
        for product in products:
            line = {
            "product_id": str(product[0].id),  # Store the product ID as a string here
            "product_name": product[0].name,  # Store the product name separately
            "lots": self.get_line_js(product[0].id),  # Store the lots using your function
            }
            data.append(line)
        return data



    @api.model
    def get_products_list_with_filter(self,date_range,date_from,date_to,included_products):
        domain=[]
        products=self.get_products_rep(included_products)
        if products:
            domain+=[("product_id","in",[int(i) for i in products.ids])]

        if date_range:
            domain+=self.get_date_range(date_range)
        else:
            domain+=self.get_date_range_domain(date_from,date_to)
        getformatted_data=self.get_formatted_data(domain)
        return getformatted_data
