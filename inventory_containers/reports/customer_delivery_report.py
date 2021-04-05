# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import xlsxwriter
import base64
import tempfile
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError,Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import io


class CustomerDeliveryReport(models.TransientModel):
    _name = "customer.delivery.report"
    _description = "Sales By Customer Report"

    name = fields.Char(string="Report Name", required=True, default="كروت الخدمة")
    date_from = fields.Date(string='من', default=lambda *a: fields.Date.today() + relativedelta(day=1), required=False)
    date_to = fields.Date(string='إلى', default=lambda *a: fields.Date.today(), required=False)
    company_id = fields.Many2one('res.company', 'شركة', required=True, default=lambda self: self.env.company)
    so_ids = fields.Many2many('sale.order', string='أمر البيع',relation="so_ids_rel", column1="so_ids_col1",column2="so_ids_col2")
    customer_ids = fields.Many2many('res.partner', string='عميل',relation="customer_ids_rel", column1="customer_ids_col1",column2="customer_ids_col2")
    vehicle_id = fields.Many2many(comodel_name="fleet.vehicle", string="السيارة",relation="vehicle_id_rel", column1="vehicle_id_col1",column2="vehicle_id_col2")
    driver_id = fields.Many2many(comodel_name="res.partner", string="السواق",relation="driver_id_rel", column1="driver_id_col1",column2="driver_id_col2")
    container_id = fields.Many2many(comodel_name="stock.containers", string="رقم الحاوية",relation="container_id_rel", column1="container_id_col1",column2="container_id_col2")
    service_number = fields.Char(string="رقم الخدمة", required=False )
    filename = fields.Char(string='File Name', size=64)
    excel_file = fields.Binary(string='Report File')

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        if self.date_from > self.date_to:
            raise Warning(_('Date From Cannot Be Greater Than Date TO!'))
        if self.date_to > date.today():
            raise Warning(_('Date To Cannot Exceed Today!'))

    def print_delivery_customer_excel_report(self):
        self.ensure_one()
        temp_location = tempfile.mkstemp()[1]
        workbook = xlsxwriter.Workbook(temp_location + '.xlsx')
        sub_heading_format = workbook.add_format({
                                'align': 'center', 'border': 1,
                                'bold': True, 'size': 18, 'bg_color': '#D3D3D3'})
        sub_heading_format.set_align('vcenter')
        cell_heading_format = workbook.add_format({'align': 'center',
                                'bold': True, 'border': 1,
                                'size': 12, 'bg_color': '#D3D3D3'})
        cell_main_format = workbook.add_format({'align': 'center',
                                'bold': True, 'border': 1,
                                'size': 12, 'bg_color': '#90EE90'})
        cell_data_format = workbook.add_format({
                            'align': 'center', 'border': 1, 'size': 10})
        heading_amount_format = workbook.add_format(
            {'align': 'right', 'bold': True, 'border': 1,
                                'size': 12, 'bg_color': '#D3D3D3'})

        cell_amount_format = workbook.add_format({
            'align': 'center', 'border': 1, 'size': 10})
        heading_data_format = workbook.add_format({'align':'center', 'border': 1, 'size': 12, 'num_format': '#,##0.00'})
        so_domain = [('state', 'in', ('sale', 'done')),('company_id','=',self.company_id.id),]
        if self.customer_ids:
            so_domain.append(('partner_id', 'in', self.customer_ids.ids),)
        if self.so_ids:
            so_domain.append(('id', 'in', self.so_ids.ids),)

        so_records = self.env['sale.order'].sudo().search(so_domain)

        # try:
        worksheet = workbook.add_worksheet('كروت الخدمة')
        row, column = 1, 0
        if self.env.user.company_id.logo:
            buf_image = io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            worksheet.set_row(0, 85)
            worksheet.insert_image('A1', "any_name.png", {'image_data': buf_image, 'x_scale': 0.5, 'y_scale': 0.5})
            row += 3

        worksheet.merge_range('C%s:F%s' % (row, row+2), self.name, sub_heading_format)
        row += 3
        worksheet.set_column('A:Z', 20)

        # Report Details
        worksheet.write(row, column, 'من', cell_heading_format)
        worksheet.write(row, column+4, 'إلى', cell_heading_format)
        worksheet.write(row+1, column, 'شركة', cell_heading_format)
        worksheet.write(row+1, column+4, 'امر بيع', cell_heading_format)
        worksheet.write(row+2, column, 'عميل', cell_heading_format)
        worksheet.write(row+2, column+4, 'سيارة', cell_heading_format)
        worksheet.write(row+3, column, 'سواق', cell_heading_format)
        worksheet.write(row+3, column+4, 'رقم حاوية', cell_heading_format)

        worksheet.merge_range('B%s:C%s' % (row+1, row+1), self.date_from.strftime(DF) if self.date_from else '-', heading_data_format)
        worksheet.merge_range('F%s:G%s' % (row+1, row+1), self.date_to.strftime(DF) if self.date_to else '-', heading_data_format)
        worksheet.merge_range('B%s:C%s' % (row+2, row+2), self.company_id.name, heading_data_format)
        if self.so_ids:
            worksheet.merge_range('F%s:G%s' % (row+2, row+2), ', '.join(self.so_ids.mapped('name')), heading_data_format)
        else:
            worksheet.merge_range('F%s:G%s' % (row+2, row+2), 'الكل', heading_data_format)
        if self.customer_ids:
            worksheet.merge_range('B%s:C%s' % (row+3, row+3), ', '.join(self.customer_ids.mapped('name')), heading_data_format)
        else:
            worksheet.merge_range('B%s:C%s' % (row+3, row+3), 'الكل', heading_data_format)
        if self.vehicle_id:
            worksheet.merge_range('F%s:G%s' % (row+3, row+3), ', '.join(self.vehicle_id.mapped('name')), heading_data_format)
        else:
            worksheet.merge_range('F%s:G%s' % (row+3, row+3), 'الكل', heading_data_format)
        if self.driver_id:
            worksheet.merge_range('B%s:C%s' % (row + 4, row + 4), ', '.join(self.driver_id.mapped('name')),heading_data_format)
        else:
            worksheet.merge_range('B%s:C%s' % (row + 4, row + 4), 'الكل', heading_data_format)
        if self.container_id:
            worksheet.merge_range('F%s:G%s' % (row + 4, row + 4), ', '.join(self.container_id.mapped('name')),heading_data_format)
        else:
            worksheet.merge_range('F%s:G%s' % (row + 4, row + 4), 'الكل', heading_data_format)

        total_reserved, total_done = 0.0, 0.0
        row += 8
        worksheet.write(row-1, column, 'عميل', cell_heading_format)
        worksheet.write(row-1, column+1, 'امر بيع', cell_heading_format)
        worksheet.write(row-1, column+2, 'مرجع', cell_heading_format)
        worksheet.write(row-1, column+3, 'عنوان التوصيل', cell_heading_format)
        worksheet.write(row-1, column+4, 'سيارة', cell_heading_format)
        worksheet.write(row-1, column+5, 'سواق', cell_heading_format)
        worksheet.write(row-1, column+6, 'حاوية رقم', cell_heading_format)
        worksheet.write(row-1, column+7, 'مدة الإيجار', cell_heading_format)
        worksheet.write(row-1, column+8, 'رقم الخدمة', cell_heading_format)
        worksheet.write(row-1, column+9, 'تاريخ التوصيل', cell_heading_format)
        worksheet.write(row-1, column+10, 'رقم الفاتورة', cell_heading_format)
        worksheet.write(row-1, column+11, 'تاريخ الفاتورة', cell_heading_format)
        worksheet.write(row-1, column+12, 'المنتج', cell_heading_format)
        worksheet.write(row-1, column+13, 'محجوز', cell_heading_format)
        worksheet.write(row-1, column+14, 'تم', cell_heading_format)
        for so in so_records:
            invoice_ids = self.env['account.move'].sudo().search([('id','in',so.invoice_ids.ids)],limit=1)
            picking_domain= [('id','in',so.picking_ids.ids),]
            if self.vehicle_id:
                # picking_domain.append('|',)
                picking_domain.append(('vehicle_id', 'in', self.vehicle_id.ids), )
                # picking_domain.append(('vehicle_id', '=',False), )
            if self.driver_id:
                # picking_domain.append('|', )
                picking_domain.append(('driver_id', 'in', self.driver_id.ids), )
                # picking_domain.append(('driver_id', '=', False), )
            if self.container_id:
                # picking_domain.append('|', )
                picking_domain.append(('container_id', 'in', self.container_id.ids), )
                # picking_domain.append(('container_id', '=', False), )
            if self.service_number:
                # picking_domain.append('|', )
                picking_domain.append(('service_number', '=', self.service_number), )
                # picking_domain.append(('container_id', '=', False), )

            picking_ids = self.env['stock.picking'].sudo().search(picking_domain)
            for picking in picking_ids:
                if picking.move_line_ids_without_package:
                    for line in picking.move_line_ids_without_package:
                        worksheet.write(row, column, so.partner_id.display_name, cell_data_format)
                        worksheet.write(row, column + 1, so.name, cell_data_format)
                        worksheet.write(row, column+2, picking.name, cell_data_format)
                        worksheet.write(row, column+3, picking.partner_id.display_name, cell_data_format)
                        worksheet.write(row, column+4, ', '.join(picking.vehicle_id.mapped('name')), cell_data_format)
                        worksheet.write(row, column+5, ', '.join(picking.driver_id.mapped('name')), cell_data_format)
                        worksheet.write(row, column+6, ', '.join(picking.container_id.mapped('name')), cell_data_format)
                        worksheet.write(row, column+7, picking.delivery_time, cell_data_format)
                        worksheet.write(row, column+8, picking.service_number, cell_data_format)
                        worksheet.write(row, column+9, picking.date_done.strftime(DF) if picking.date_done else '-', cell_data_format)
                        worksheet.write(row, column+10, invoice_ids.name if invoice_ids else '-', cell_data_format)
                        worksheet.write(row, column+11,invoice_ids.invoice_date.strftime(DF) if invoice_ids else '-', cell_data_format)
                        worksheet.write(row, column+12, line.product_id.display_name, cell_data_format)
                        worksheet.write(row, column+13, line.product_uom_qty, cell_data_format)
                        worksheet.write(row, column+14, line.qty_done, cell_data_format)
                        total_reserved += line.product_uom_qty
                        total_done += line.qty_done
                        row += 1
                else:
                    worksheet.write(row, column, so.partner_id.display_name, cell_data_format)
                    worksheet.write(row, column + 1, so.name, cell_data_format)
                    worksheet.write(row, column + 2, picking.name, cell_data_format)
                    worksheet.write(row, column + 3, picking.partner_id.display_name, cell_data_format)
                    worksheet.write(row, column + 4, ', '.join(picking.vehicle_id.mapped('name')), cell_data_format)
                    worksheet.write(row, column + 5, ', '.join(picking.driver_id.mapped('name')), cell_data_format)
                    worksheet.write(row, column + 6, ', '.join(picking.container_id.mapped('name')), cell_data_format)
                    worksheet.write(row, column + 7, picking.delivery_time, cell_data_format)
                    worksheet.write(row, column + 8, picking.service_number, cell_data_format)
                    worksheet.write(row, column + 9, picking.date_done.strftime(DF) if picking.date_done else '-', cell_data_format)
                    worksheet.write(row, column + 10, invoice_ids.name if invoice_ids else '-', cell_data_format)
                    worksheet.write(row, column + 11, invoice_ids.invoice_date.strftime(DF) if invoice_ids else '-', cell_data_format)
                    worksheet.write(row, column + 12, '', cell_data_format)
                    worksheet.write(row, column + 13, '', cell_data_format)
                    worksheet.write(row, column + 14, '', cell_data_format)
                    row += 1

        worksheet.merge_range('A%s:M%s' % (row+1, row+1), 'المجموع',cell_heading_format)
        worksheet.write(row, column+13, total_reserved, cell_amount_format)
        worksheet.write(row, column+14, total_done, cell_amount_format)
        worksheet.right_to_left()
        # except Exception as e:
        #     raise ValidationError(_('You are not able to print this report please contact your'
        #                         'administrator : %s ' % str(e)))
        workbook.close()
        fp = base64.encodestring(open(temp_location + '.xlsx','rb').read())
        if self.date_from and self.date_to:
            file_name = '%s from %s to %s.xlsx' % (self.name ,self.date_from, self.date_to)
        elif self.date_from and not self.date_to:
            file_name = '%s from %s.xlsx' % (self.name ,self.date_from)
        elif self.date_to and not self.date_from:
            file_name = '%s to %s.xlsx' % (self.name ,self.date_to)
        else:
            file_name = '%s.xlsx' % (self.name)

        self.write({'filename': file_name, 'excel_file': fp})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=customer.delivery.report&field=excel_file&download=true&id=%s&filename=%s'%(self.id, file_name),
            'target': 'new',
        }