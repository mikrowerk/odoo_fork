from odoo import models, fields


class JobInvoice(models.Model):
    """
    Extends the standard account move model to have a relation to jobcontrol.job.
    """
    _inherit = 'account.move'
    job_id = fields.Many2one('jobcontrol.job', string="Job")


class JobCostsInvoiceLine(models.Model):
    """
    Extends the standard account move_line model to have a relation to jobcontrol.job_cost
    """
    _inherit = 'account.move.line'
    job_cost_ids = fields.One2many(comodel_name="jobcontrol.job_costs", string="Job Cost Lines", inverse_name="invoice_line")
