# -*- coding: utf-8 -*-

from odoo import models, fields

JOB_STATE = [
    ('draft', "Draft"),
    ('quotation', "Quotation"),
    ('ordered', "Order Received"),
    ('progress', "In Progress"),
    ('invoiced', "Invoiced"),
    ('completed', "Completed"),
    ('archived', "Archived"),
    ('danger', "In Danger"),
]


class Job(models.Model):
    """
    Job Model which is a container for job information and anchor for related records
    """
    _name = 'jobcontrol.job'
    _description = 'jobcontrol.job'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    number = fields.Char("Job_ID", required=True)
    display_name = fields.Char(compute="_display_name", string="Display")
    description = fields.Text("Description", required=False)
    state = fields.Selection(
        selection=JOB_STATE,
        string="Status",
        copy=False, index=True,
        tracking=3,
        default='draft')
    date_started = fields.Date("Start Date", required=True)
    date_completed = fields.Date("Completion Date", required=True)
    partner_company_id = fields.Many2one('res.partner', string="Customer Company", required=True)
    partner_responsible_id = fields.Many2one('res.partner', string="Contact", required=True)
    user_id = fields.Many2one('res.users', string="Assigned to", required=True)
    sales_order_line = fields.One2many(
        comodel_name='sale.order',
        inverse_name='job_id',
        string='Sales Order'
    )
    purchase_order_line = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='job_id',
        string='Purchase Order'
    )
    sales_invoice_order_line = fields.One2many(
        comodel_name='account.move',
        inverse_name='job_id',
        string='Sales Invoice',
        domain=[('journal_id.type', '=', 'sale')]
    )
    purchase_invoice_order_line = fields.One2many(
        comodel_name='account.move',
        inverse_name='job_id',
        string='Purchase Invoice',
        domain=[('journal_id.type', '=', 'purchase')]
    )

    max_name_length = 20

    def _display_name(self):
        for record in self:
            record.display_name = (f"{record.number} "
                                   f"{(record.name[:self.max_name_length] + '...') if len(record.name) > self.max_name_length else record.name}")

    def name_get(self):
        result = []
        for record in self:
            name = record.number
            result.append((record.id, name))
        return result

    def create_sales_order(self):
        """
        Create sales order for job
        """
        self.ensure_one()
        job_id = self.id
        job_number = self.number
        user_id = self.user_id.id
        customer_id = self.partner_company_id.id
        responsible_id = self.partner_responsible_id.id
        currency_id = self.env.company.currency_id.id
        print(f"Create sale.order with Job id= {job_id}, job_number= {job_number}, user_id= {user_id}, ",
              f"currency_id={currency_id}, customer_id= {customer_id}, responsible_id={responsible_id}")
        order_ref = self.env['sale.order'].browse(self._context.get('id', []))
        order = order_ref.create({
            'partner_invoice_id': customer_id,
            'partner_id': responsible_id,
            'partner_shipping_id': responsible_id,
            'currency_id': currency_id,
            'job_id': job_id,
            'origin': job_number,
            'user_id': user_id
        })
        return {
            'name': 'Sales Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'current',
            'res_id': order.id,
            'res_model': 'sale.order',
            'context': {'create': False, 'delete': True, 'edit': True, }
        }


class JobSales(models.Model):
    """
    Extends the standard sales model to have a relation to jobcontrol.job.
    """
    _inherit = 'sale.order'
    job_id = fields.Many2one('jobcontrol.job', string="Job")


class JobPurchase(models.Model):
    """
    Extends the standard purchase model to have a relation to jobcontrol.job.
    """
    _inherit = 'purchase.order'
    job_id = fields.Many2one('jobcontrol.job', string="Job")


class JobInvoice(models.Model):
    """
    Extends the standard purchase model to have a relation to jobcontrol.job.
    """
    _inherit = 'account.move'
    job_id = fields.Many2one('jobcontrol.job', string="Job")
    job_number: fields.Char(related="job_id.number", string="Job Number")
