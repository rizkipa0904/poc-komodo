from odoo import models, fields

class PlantSeed(models.Model):
    _name = 'plant.seed'
    _description = 'Seed Information'

    name = fields.Char(string='Seed Type', required=True)
    origin = fields.Char(string='Seed Origin', required=True)