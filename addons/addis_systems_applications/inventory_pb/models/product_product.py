from odoo import  fields,models, api
import operator as py_operator
from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_is_zero, check_barcode_encoding
from odoo.tools.float_utils import float_round
from odoo.tools.mail import html2plaintext, is_html_empty

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    # qty_available = fields.Float(
    #     'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
    #     digits='Product Unit of Measure', compute_sudo=False,
    #     help="Current quantity of products.\n"
    #          "In a context with a single Stock Location, this includes "
    #          "goods stored at this Location, or any of its children.\n"
    #          "In a context with a single Warehouse, this includes "
    #          "goods stored in the Stock Location of this Warehouse, or any "
    #          "of its children.\n"
    #          "stored in the Stock Location of the Warehouse of this Shop, "
    #          "or any of its children.\n"
    #          "Otherwise, this includes goods stored in any Stock Location "
    #          "with 'internal' type.")
    # virtual_available = fields.Float(
    #     'Forecasted Quantity', compute='_compute_quantities', search='_search_virtual_available',
    #     digits='Product Unit of Measure', compute_sudo=False,
    #     help="Forecast quantity (computed as Quantity On Hand "
    #          "- Outgoing + Incoming)\n"
    #          "In a context with a single Stock Location, this includes "
    #          "goods stored in this location, or any of its children.\n"
    #          "In a context with a single Warehouse, this includes "
    #          "goods stored in the Stock Location of this Warehouse, or any "
    #          "of its children.\n"
    #          "Otherwise, this includes goods stored in any Stock Location "
    #          "with 'internal' type.")
    # free_qty = fields.Float(
    #     'Free To Use Quantity ', compute='_compute_quantities', search='_search_free_qty',
    #     digits='Product Unit of Measure', compute_sudo=False,
    #     help="Forecast quantity (computed as Quantity On Hand "
    #          "- reserved quantity)\n"
    #          "In a context with a single Stock Location, this includes "
    #          "goods stored in this location, or any of its children.\n"
    #          "In a context with a single Warehouse, this includes "
    #          "goods stored in the Stock Location of this Warehouse, or any "
    #          "of its children.\n"
    #          "Otherwise, this includes goods stored in any Stock Location "
    #          "with 'internal' type.")
    # incoming_qty = fields.Float(
    #     'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
    #     digits='Product Unit of Measure', compute_sudo=False,
    #     help="Quantity of planned incoming products.\n"
    #          "In a context with a single Stock Location, this includes "
    #          "goods arriving to this Location, or any of its children.\n"
    #          "In a context with a single Warehouse, this includes "
    #          "goods arriving to the Stock Location of this Warehouse, or "
    #          "any of its children.\n"
    #          "Otherwise, this includes goods arriving to any Stock "
    #          "Location with 'internal' type.")
    # outgoing_qty = fields.Float(
    #     'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
    #     digits='Product Unit of Measure', compute_sudo=False,
    #     help="Quantity of planned outgoing products.\n"
    #          "In a context with a single Stock Location, this includes "
    #          "goods leaving this Location, or any of its children.\n"
    #          "In a context with a single Warehouse, this includes "
    #          "goods leaving the Stock Location of this Warehouse, or "
    #          "any of its children.\n"
    #          "Otherwise, this includes goods leaving any Stock "
    #          "Location with 'internal' type.")
    # @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    # @api.depends_context(
    #     'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
    #     'location', 'warehouse',
    # )
    
    # def _filter_warehouse_context(self):
    #     filtered_warehouse_ids = [warehouse.id for warehouse in self.env['stock.warehouse'] if warehouse.id in allowed_warehouses]
    #     self._context.update({'warehouse': filtered_warehouse_ids})

    def _filter_warehouse_ids(self):
        filtered_warehouse_ids = self.env.user.allowed_warehouses_ids.ids
        return filtered_warehouse_ids
    
    # def _compute_quantities(self):
    #     # self._filter_warehouse_context()
    #     # warehouse_ids = self._filter_warehouse_ids()
    
        
    #     products = self.filtered(lambda p: p.type != 'service')
    #     res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
    #     for product in products:
    #         product.update(res[product.id])
    #     # Services need to be set with 0.0 for all quantities
    #     services = self - products
    #     services.qty_available = 0.0
    #     services.incoming_qty = 0.0
    #     services.outgoing_qty = 0.0
    #     services.virtual_available = 0.0
    #     services.free_qty = 0.0

    # def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        
    #     domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
    #     domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
    #     dates_in_the_past = False
    #     # only to_date as to_date will correspond to qty_available
    #     to_date = fields.Datetime.to_datetime(to_date)
    #     if to_date and to_date < fields.Datetime.now():
    #         dates_in_the_past = True

    #     domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
    #     domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
    #     if lot_id is not None:
    #         domain_quant += [('lot_id', '=', lot_id)]
    #     if owner_id is not None:
    #         domain_quant += [('owner_id', '=', owner_id)]
    #         domain_move_in += [('restrict_partner_id', '=', owner_id)]
    #         domain_move_out += [('restrict_partner_id', '=', owner_id)]
    #     if package_id is not None:
    #         domain_quant += [('package_id', '=', package_id)]
    #     if dates_in_the_past:
    #         domain_move_in_done = list(domain_move_in)
    #         domain_move_out_done = list(domain_move_out)
    #     if from_date:
    #         date_date_expected_domain_from = [('date', '>=', from_date)]
    #         domain_move_in += date_date_expected_domain_from
    #         domain_move_out += date_date_expected_domain_from
    #     if to_date:
    #         date_date_expected_domain_to = [('date', '<=', to_date)]
    #         domain_move_in += date_date_expected_domain_to
    #         domain_move_out += date_date_expected_domain_to

    #     Move = self.env['stock.move'].with_context(active_test=False)
    #     Quant = self.env['stock.quant'].with_context(active_test=False)
    #     domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
    #     domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
    #     moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #     moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #     quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'])) for item in Quant._read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity'], ['product_id'], orderby='id'))
    #     if dates_in_the_past:
    #         # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
    #         domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
    #         domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
    #         moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
    #         moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move._read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

    #     res = dict()
    #     for product in self.with_context(prefetch_fields=False):
    #         origin_product_id = product._origin.id
    #         product_id = product.id
    #         if not origin_product_id:
    #             res[product_id] = dict.fromkeys(
    #                 ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
    #                 0.0,
    #             )
    #             continue
    #         rounding = product.uom_id.rounding
    #         res[product_id] = {}
    #         if dates_in_the_past:
    #             qty_available = quants_res.get(origin_product_id, [0.0])[0] - moves_in_res_past.get(origin_product_id, 0.0) + moves_out_res_past.get(origin_product_id, 0.0)
    #         else:
    #             qty_available = quants_res.get(origin_product_id, [0.0])[0]
                
    #         reserved_quantity = quants_res.get(origin_product_id, [False, 0.0])[1]
    #         res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
    #         res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity, precision_rounding=rounding)
    #         res[product_id]['incoming_qty'] = float_round(moves_in_res.get(origin_product_id, 0.0), precision_rounding=rounding)
    #         res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(origin_product_id, 0.0), precision_rounding=rounding)
    #         res[product_id]['virtual_available'] = float_round(
    #             qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
    #             precision_rounding=rounding)

    #     return res
        
    # def _get_domain_locations(self):
    #     '''
    #     Parses the context and returns a list of location_ids based on it.
    #     It will return all stock locations when no parameters are given
    #     Possible parameters are shop, warehouse, location, compute_child
    #     '''
    #     warehouse_ids = self._filter_warehouse_ids()
        
    #     Warehouse = self.env['stock.warehouse']

    #     def _search_ids(model, values):
    #         ids = set()
    #         domain = []
    #         for item in values:
    #             if isinstance(item, int):
    #                 ids.add(item)
    #             else:
    #                 domain = expression.OR([[(self.env[model]._rec_name, 'ilike', item)], domain])
    #         if domain:
    #             ids |= set(self.env[model].search(domain).ids)
    #         return ids

    #     # We may receive a location or warehouse from the context, either by explicit
    #     # python code or by the use of dummy fields in the search view.
    #     # Normalize them into a list.
    
    #     location = self.env.context.get('location')
    #     if location and not isinstance(location, list):
    #         location = [location]
    #     warehouse = self.env.context.get('warehouse')
        
    #     if warehouse and not isinstance(warehouse, list):
    #         warehouse = [warehouse]
    
    #     # filter by location and/or warehouse
    #     if warehouse:
    #         w_ids = set(Warehouse.browse(_search_ids('stock.warehouse', warehouse)).mapped('view_location_id').ids)
    #         if location:
    #             l_ids = _search_ids('stock.location', location)
    #             location_ids = w_ids & l_ids
    #         else:
    #             location_ids = w_ids
    #     else:
    #         if location:
    #             location_ids = _search_ids('stock.location', location)
    #         else:
    #             location_ids = set(Warehouse.search([]).mapped('view_location_id').ids)

    #     return self._get_domain_locations_new(location_ids)
    
    
    # updated _get_domain_locations
    
    def _get_domain_locations(self):
        '''
        Parses the context and returns a list of location_ids based on it.
        It will return all stock locations when no parameters are given
        Possible parameters are shop, warehouse, location, compute_child
        '''

        warehouse_ids = self._filter_warehouse_ids()
        
        Warehouse = self.env['stock.warehouse']
        
        
        def _search_ids(model, values):
            ids = set()
            domain = []
            for item in values:
                if isinstance(item, int):
                    ids.add(item)
                else:
                    domain = expression.OR([[(self.env[model]._rec_name, 'ilike', item)], domain])
            if domain:
                ids |= set(self.env[model].search(domain).ids)
            return ids

        # We may receive a location from the context, either by explicit
        # python code or by the use of dummy fields in the search view.
        # Normalize them into a list.
        location = self.env.context.get('location')
        if location and not isinstance(location, list):
            location = [location]

        # filter by location
        if location:
            l_ids = _search_ids('stock.location', location)
            location_ids = l_ids
        else:
            # Ensure only locations from allowed warehouses are considered
            location_ids = set(Warehouse.search([('id', 'in', warehouse_ids)]).mapped('view_location_id').ids)

        return self._get_domain_locations_new(location_ids)

        
        


    def _search_qty_available(self, operator, value):
        # In the very specific case we want to retrieve products with stock available, we only need
        # to use the quants, not the stock moves. Therefore, we bypass the usual
        # '_search_product_quantity' method and call '_search_qty_available_new' instead. This
        # allows better performances.
        if not ({'from_date', 'to_date'} & set(self.env.context.keys())):
            product_ids = self._search_qty_available_new(
                operator, value, self.env.context.get('lot_id'), self.env.context.get('owner_id'),
                self.env.context.get('package_id')
            )
            return [('id', 'in', product_ids)]
        return self._search_product_quantity(operator, value, 'qty_available')
    
    
    def _search_qty_available_new(self, operator, value, lot_id=False, owner_id=False, package_id=False):
        ''' Optimized method which doesn't search on stock.moves, only on stock.quants. '''
        product_ids = set()
        domain_quant = self._get_domain_locations()[0]
        
        # Fetch allowed warehouses for the current user
        allowed_warehouses_ids = self.env.user.allowed_warehouses_ids
        
        # Add warehouse filter to domain_quant
        if allowed_warehouses_ids:
            domain_quant.append(('warehouse_id','in', allowed_warehouses_ids))
        
        if lot_id:
            domain_quant.append(('lot_id', '=', lot_id))
        if owner_id:
            domain_quant.append(('owner_id', '=', owner_id))
        if package_id:
            domain_quant.append(('package_id', '=', package_id))
        
        quants_groupby = self.env['stock.quant']._read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id')

        # check if we need include zero values in result
        include_zero = (
            value < 0.0 and operator in ('>', '>=') or
            value > 0.0 and operator in ('<', '<=') or
            value == 0.0 and operator in ('>=', '<=', '=')
        )

        processed_product_ids = set()
        for quant in quants_groupby:
            product_id = quant['product_id'][0]
            if include_zero:
                processed_product_ids.add(product_id)
            if OPERATORS[operator](quant['quantity'], value):
                product_ids.add(product_id)

        if include_zero:
            products_without_quants_in_domain = self.env['product.product'].search([
                ('type', '=', 'product'),
                ('id', 'not in', list(processed_product_ids))],
                order='id'
            )
            product_ids |= set(products_without_quants_in_domain.ids)
        return list(product_ids)



    # def _get_domain_locations_new(self, location_ids):
    #     locations = self.env['stock.location'].browse(location_ids)
    #     # TDE FIXME: should move the support of child_of + auto_join directly in expression
    #     loc_domain, dest_loc_domain = [], []
    #     # this optimizes [('location_id', 'child_of', locations.ids)]
    #     # by avoiding the ORM to search for children locations and injecting a
    #     # lot of location ids into the main query
    #     for location in locations:
    #         loc_domain = loc_domain and ['|'] + loc_domain or loc_domain
    #         loc_domain.append(('location_id.parent_path', '=like', location.parent_path + '%'))
    #         dest_loc_domain = dest_loc_domain and ['|'] + dest_loc_domain or dest_loc_domain
    #         dest_loc_domain.append(('location_dest_id.parent_path', '=like', location.parent_path + '%'))

    #     return (
    #         loc_domain,
    #         dest_loc_domain + ['!'] + loc_domain if loc_domain else dest_loc_domain,
    #         loc_domain + ['!'] + dest_loc_domain if dest_loc_domain else loc_domain
    #     )
