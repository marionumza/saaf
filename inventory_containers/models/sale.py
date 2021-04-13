from odoo import api, fields, models


class SaleAdvancePaymentInv(models.Model):
    _inherit= 'sale.order'
    service_number = fields.Char(string="رقم الخدمة", required=False )


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        for so in sale_orders:
            picking_ids = self.env['stock.picking'].sudo().search([('id', 'in', so.picking_ids.ids)])
            for pick in picking_ids:
                so.service_number = pick.service_number
                for inv in so.invoice_ids:
                    inv.ref = pick.service_number
        return res
