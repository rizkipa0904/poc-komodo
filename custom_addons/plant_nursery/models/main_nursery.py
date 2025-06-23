from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

class MainNursery(models.Model):
    _name = 'plant.main_nursery'
    _description = 'Main Nursery Batch'

    batch_id = fields.Many2one('plant.pre_nursery', string='Batch from Pre-Nursery', required=True)
    bed_number = fields.Char(string='Bed Number', related='batch_id.bed_number', store=True)
    plot_number = fields.Char(string='Plot Number', required=True)
    row_number = fields.Char(string='Row Number', required=True)
    tree_number = fields.Integer(string='Tree Number', required=True)
    planting_date = fields.Date(string='Planting Date', required=True)

    plant_code = fields.Char(string='Plant Code', compute="_compute_plant_code", store=True, readonly=True)
    plant_qr_code = fields.Binary(string='QR Code', compute="generate_qr_code", store=True, attachment=True)

    @api.depends('batch_id.batch_number', 'plot_number', 'row_number', 'tree_number')
    def _compute_plant_code(self):
        for record in self:
            if record.batch_id and record.batch_id.batch_number and record.bed_number and record.plot_number and record.row_number and record.tree_number:
                record.plant_code = f"{record.batch_id.batch_number}-{record.bed_number}-{record.plot_number}-{record.row_number}-{record.tree_number}"
            else:
                record.plant_code = ''
    
    @api.depends('plant_code')
    def generate_qr_code(self):
        for record in self:
            if record.plant_code and not record.plant_qr_code:
                qr = qrcode.make(record.plant_code)
                buffer = BytesIO()
                qr.save(buffer, format='PNG')
                qr_image = base64.b64encode(buffer.getvalue())
                record.plant_qr_code = qr_image
            else:
                record.plant_qr_code = False

class MainNurseryView(models.Model):
    _inherit = 'plant.main_nursery'

    list_view = [
        'plant_code', 'batch_id', 'bed_number', 'plot_number', 'row_number', 'tree_number', 'planting_date', 'plant_qr_code'
    ]
    form_view = [
        'plant_code', 'batch_id', 'bed_number', 'plot_number', 'row_number', 'tree_number', 'planting_date', 'plant_qr_code'
    ]