import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from datetime import datetime, date

# Create the root element
def wrte_xml_file(self):
    voucher_xml = ET.Element("VoucherXml")

    # Create the Voucher element
    voucher = ET.SubElement(voucher_xml, "Voucher")
    ET.SubElement(voucher, "code").text = self.name
    inv_code=str(404)
    if self.move_type=="out_invoice":
        inv_code=str(108)
    elif self.move_type=="out_receipt":
        inv_code=str(106)
    ET.SubElement(voucher, "voucherDefnition").text = inv_code
    ET.SubElement(voucher, "date").text = self.invoice_date.strftime('%Y-%m-%d')
    ET.SubElement(voucher, "grandTotal").text = str(self.amount_total_signed)

    # Create the customer element within Voucher
    customer = ET.SubElement(voucher, "customer")
    ET.SubElement(customer, "code").text = self.partner_id.partner_code
    ET.SubElement(customer, "name").text = self.partner_id.name
    ET.SubElement(customer, "TIN").text = self.partner_id.vat or ""

    # Create the LineItem element
    line_ids=self.line_ids.ids
    items_datas=self.env['account.move.line'].search([('id','in',line_ids),('display_type','=','product')])
    grand_discount=0
    for item_data in items_datas:
        grand_discount+=item_data.discount*item_data.price_unit*item_data.quantity*0.01
        line_item = ET.SubElement(voucher_xml, "LineItem")
        ET.SubElement(line_item, "unitAmount").text = f"{item_data.price_unit:.2f}"
        ET.SubElement(line_item, "quantity").text = str(item_data.quantity)
        ET.SubElement(line_item, "totalAmount").text = f"{item_data.price_total}"
        ET.SubElement(line_item, "taxType").text = "VAT"
        ET.SubElement(line_item, "Itm_Qty").text = str(item_data.quantity)

        # Create the item element within LineItem
        item = ET.SubElement(line_item, "item")
        ET.SubElement(item, "code").text = item_data.product_id.default_code
        ET.SubElement(item, "name").text = item_data.product_id.name
        ET.SubElement(item, "category").text = item_data.product_id.categ_id.name

        # Create the LineItemValues element within LineItem
        line_item_values = ET.SubElement(line_item, "LineItemValues")
        ET.SubElement(line_item_values, "discount").text = str(item_data.discount) + " %"
        ET.SubElement(line_item_values, "additionalCharge").text = "0"
    # Create the voucherValues element
    voucher_values = ET.SubElement(voucher_xml, "voucherValues")
    ET.SubElement(voucher_values, "discount").text = f"{grand_discount}"
    ET.SubElement(voucher_values, "additionalCharge").text = "0.00"
    ET.SubElement(voucher_values, "subTotal").text = f"{self.amount_untaxed_signed}"

    # Create the Activity element
    activity = ET.SubElement(voucher_xml, "Activity")
    ET.SubElement(activity, "deviceName").text = ""
    user = ET.SubElement(activity, "user")
    ET.SubElement(user, "employeeCode").text = self.user_id.login
    ET.SubElement(user, "fullName").text = self.user_id.partner_id.name
    ET.SubElement(user, "userName").text = self.user_id.login

    # Create the Doctor element
    doctor = ET.SubElement(voucher_xml, "Doctor")
    ET.SubElement(doctor, "code").text = ""
    ET.SubElement(doctor, "name").text = ""

    # Create the BusinessSource element
    business_source = ET.SubElement(voucher_xml, "BusinessSource")
    ET.SubElement(business_source, "code").text = ""
    ET.SubElement(business_source, "name").text = ""

    # Convert to a string and pretty print
    xml_str = ET.tostring(voucher_xml, encoding='utf-8', method='xml')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

    # Ensure the XML declaration includes the encoding
    pretty_xml_str_with_decl = '<?xml version="1.0" encoding="UTF-8"?>\n' + '\n'.join(pretty_xml_str.split('\n')[1:])
    return pretty_xml_str_with_decl
   

