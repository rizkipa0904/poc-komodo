from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

class PreNursery(models.Model):
    _name = 'plant.pre_nursery'
    _description = 'Pre-Nursery Batch'

    batch_number = fields.Char(string='Batch Number', required=True)
    bed_number = fields.Char(string='Bed Number', required=True)
    seed_id = fields.Many2one('plant.seed', string='Seed Type', required=True)
    number_of_seeds = fields.Integer(string='Number of Seeds', required=True)
    planting_date = fields.Date(string='Planting Date', required=True)
    transplanting_date = fields.Date(string='Transplanting Date')

    plant_code = fields.Char(string='Plant Code', compute="_compute_plant_code", store=True, readonly=True)
    plant_qr_code = fields.Binary(string='QR Code', compute="generate_qr_code", store=True, attachment=True)

    @api.depends('batch_number', 'bed_number')
    def _compute_plant_code(self):
        for record in self:
            record.plant_code = f"{record.batch_number}-{record.bed_number}" if record.batch_number and record.bed_number else ''

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

class PreNurseryView(models.Model):
    _inherit = 'plant.pre_nursery'

    list_view = [
        'plant_code', 'batch_number', 'bed_number', 'seed_id', 'number_of_seeds', 'planting_date', 'transplanting_date', 'plant_qr_code'
    ]
    form_view = [
        'plant_code', 'batch_number', 'bed_number', 'seed_id', 'number_of_seeds', 'planting_date', 'transplanting_date', 'plant_qr_code'
    ]