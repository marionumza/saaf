from odoo import fields, models,api

class StockContainers(models.Model):
    _name = 'stock.containers'
    _rec_name = 'name'

    name = fields.Char(string="الإسم", required=True, )
    number = fields.Char(string="الرقم", required=True, )
    delivery_time = fields.Integer(string="مدة الايجار",required=True, )


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            recs = self.browse()
            if operator in positive_operators:
                recs = self.search(['|', ('number', operator, name), ('name', operator, name)] + args,limit=limit)
                if not recs:
                    recs = self.search([('number', '=', name)] + args, limit=limit)
        else:
            recs = self.search(args, limit=limit)

        return recs.name_get()

    def name_get(self):
        res = []
        for rec in self:
            if rec.number and  rec.name:
                name = '%s / %s' % (rec.number, rec.name)
            elif rec.number and not rec.name:
                name = '%s' % (rec.number)
            elif rec.name and not rec.number:
                name = '%s' % (rec.name)
            res.append((rec.id, name))
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="السيارة", required=False,copy=False)
    driver_id = fields.Many2one(related='vehicle_id.driver_id',comodel_name="res.partner", string="السواق",store=True, required=False,readonly=False,copy=False )
    container_id = fields.Many2one(comodel_name="stock.containers", string="رقم الحاوية", required=False,ondelete='restrict',copy=False )
    delivery_time = fields.Integer(related='container_id.delivery_time',string="مدة الايجار", required=False,readonly=False,store=True, )
    service_number = fields.Char(string="رقم الخدمة", required=False )



