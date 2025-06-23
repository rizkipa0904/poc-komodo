import logging
from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO

_logger = logging.getLogger(__name__)

class PlantBatch(models.Model):
    _name = 'plant.batch'
    _description = 'Plant Batch'

    plant_code = fields.Char(string="Plant Code", required=True)
    batch_number = fields.Char(string="Batch Number", required=True)
    bed_number = fields.Char(string="Bed Number", required=True)
    image = fields.Image(string="Plant Image", max_width=1920, max_height=1920) 
    number_of_seeds = fields.Integer(string="Number of Seeds", required=True)
    type_of_seeds = fields.Char(string="Type of Seeds", required=True)
    origin_of_seeds = fields.Char(string="Origin of Seeds", required=True)
    planting_date = fields.Datetime(string="Planting Date", required=True)
    transplanting_date = fields.Datetime(string="Transplanting Date")

    qr_code = fields.Binary("QR Code", compute="_generate_qr_code", store=True)
    qr_code_str = fields.Char("QR Code String", compute="_generate_qr_code", store=True)

    @api.depends("batch_number")
    def _generate_qr_code(self):
        """ Generate QR Code based on batch_number """
        for record in self:
            if record.batch_number:
                qr_data = f"{record.batch_number}"  # Ganti dengan batch_number saja
                record.qr_code_str = qr_data

                qr_img = qrcode.make(qr_data)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                record.qr_code = qr_code_base64
            else:
                record.qr_code = False
                record.qr_code_str = ""

    @api.model
    def get_batch_by_qr(self, barcode):
        """Return the batch that matches the given QR code."""
        batch = self.search([('batch_number', '=', barcode)], limit=1)
        if not batch:
            _logger.info("No batch found with this QR code.")
            return {'error': 'batch_not_found'}
        else:
            # Menggunakan .read() untuk melihat semua field dalam batch
            batch_data = batch.read()  # Mengambil semua field dari record
            _logger.info(f"Batch data: {batch_data}")  # Menampilkan data batch ke log
            return batch_data  # Mengembalikan data batch
        
