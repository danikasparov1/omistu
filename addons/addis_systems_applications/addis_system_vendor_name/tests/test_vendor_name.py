from odoo.tests.common import TransactionCase

class TestPurchaseOrderVendor(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderVendor, self).setUp()
        self.vendor = self.env['res.partner'].create({'name': 'Test Vendor'})
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
        })

    def test_vendor_name_in_purchase_order(self):
        self.assertEqual(self.purchase_order.partner_id.name, 'Test Vendor', "Vendor name should match the created partner")
