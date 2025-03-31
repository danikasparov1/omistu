
from odoo import models, api

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # @api.model
    # def get_top_manufactured_products_chart(self):
    #     """Returns the top 10 manufactured products by quantity produced."""
    #     query = """
    #         SELECT product_id, SUM(product_qty) as total_produced
    #         FROM mrp_production
    #         WHERE state = 'done'  -- Only completed manufacturing orders
    #         GROUP BY product_id
    #         ORDER BY total_produced DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     products = self.env["product.product"].browse([rec[0] for rec in results])

    #     return {
    #         "labels": [product.name for product in products],
    #         "data": [rec[1] for rec in results],
    #     }

    @api.model
    def get_top_manufactured_products_chart(self):
        """Returns top 10 manufactured products by quantity produced."""
        query = """
            SELECT product_id, SUM(product_qty) as total_produced
            FROM mrp_production
            WHERE state = 'done'  -- Only completed manufacturing orders
            GROUP BY product_id
            ORDER BY total_produced DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch product names from product.product model
        products = self.env["product.product"].browse([rec[0] for rec in results])

        return [
            {
                "product": product.name,  # Product name
                "total_produced": rec[1],  # Total quantity produced
            }
            for rec, product in zip(results, products)
        ]



class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    # @api.model
    # def get_top_workcenters_chart(self):
    #     """Returns the top 10 work centers by total operation duration (hours)."""
    #     query = """
    #         SELECT workcenter_id, SUM(duration) / 60.0 as total_hours
    #         FROM mrp_workorder
    #         WHERE state = 'done'  -- Only completed work orders
    #         GROUP BY workcenter_id
    #         ORDER BY total_hours DESC
    #         LIMIT 10
    #     """
    #     self._cr.execute(query)
    #     results = self._cr.fetchall()

    #     workcenters = self.env["mrp.workcenter"].browse([rec[0] for rec in results])

    #     return {
    #         "labels": [workcenter.name for workcenter in workcenters],
    #         "data": [rec[1] for rec in results],  # Total hours
    #     }

    @api.model
    def get_top_workcenters_chart(self):
        """Returns top 10 work centers by total operation duration (hours)."""
        query = """
            SELECT workcenter_id, SUM(duration) / 60.0 as total_hours
            FROM mrp_workorder
            WHERE state = 'done'  -- Only completed work orders
            GROUP BY workcenter_id
            ORDER BY total_hours DESC
            LIMIT 10
        """
        self._cr.execute(query)
        results = self._cr.fetchall()

        # Fetch work center names
        workcenters = self.env["mrp.workcenter"].browse([rec[0] for rec in results])

        return [
            {
                "workcenter": workcenter.name,  # Work center name
                "total_hours": rec[1],  # Total hours
            }
            for rec, workcenter in zip(results, workcenters)
        ]

