from odoo import _, fields, models, api
from odoo.exceptions import UserError

class PlantActivity(models.Model):
    _name = 'plant.activity'
    _description = 'Plant Activity'

    batch_id = fields.Many2one('plant.batch', string='Batch Number', required=True)
    activity_date = fields.Date('Activity Date', required=True, default=fields.Date.today)
    watering = fields.Boolean('Watering')
    fertilization = fields.Boolean('Fertilization')
    pesticide_treatment = fields.Boolean('Pesticide Treatment')
    weeding = fields.Boolean('Weeding')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Canceled')
    ], default='draft', string="Status")
    confirmation_date = fields.Datetime('Confirmation Date')

    @api.model
    def get_activity_by_batch(self, batch_id):
        activity = self.search([('batch_id', '=', batch_id)], limit=1)
        return activity if activity else []

    @api.model
    def register_plant_activity(self, batch_id):
        activity = self.search([('batch_id', '=', batch_id)], limit=1)

        if activity:
            status = 'already_registered' if activity.state == 'done' else 'pending'
        else:
            activity = self.create({
                'batch_id': batch_id,
                'activity_date': fields.Date.today(),
                'state': 'draft',
            })
            status = 'new_activity_created'

        return {
            'message': status,
            'activity': activity if activity else []
        }

    def action_confirm(self):
        self.ensure_one()

        if not (self.watering or self.fertilization or self.pesticide_treatment or self.weeding):
            raise UserError(_("At least one activity must be selected before confirming."))

        existing_activity = self.search([('batch_id', '=', self.batch_id.id)], limit=1)

        if existing_activity:
            existing_activity.write({
                'activity_date': self.activity_date,
                'watering': self.watering,
                'fertilization': self.fertilization,
                'pesticide_treatment': self.pesticide_treatment,
                'weeding': self.weeding,
                'state': 'done',
                'confirmation_date': fields.Datetime.now()
            })
        else:
            self.create({
                'batch_id': self.batch_id.id,
                'activity_date': self.activity_date,
                'watering': self.watering,
                'fertilization': self.fertilization,
                'pesticide_treatment': self.pesticide_treatment,
                'weeding': self.weeding,
                'state': 'done',
                'confirmation_date': fields.Datetime.now()
            })

        if self.batch_id:
            self.batch_id.write({'last_activity_date': self.activity_date})

        return True

    def action_save(self):
        self.write({
            'watering': self.watering,
            'fertilization': self.fertilization,
            'pesticide_treatment': self.pesticide_treatment,
            'weeding': self.weeding,
            'state': 'draft'
        })
