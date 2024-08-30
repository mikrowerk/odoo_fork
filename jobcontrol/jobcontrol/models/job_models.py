# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.purchase.models.purchase_order import PurchaseOrder

from .job_utils import shorten_text, MAX_NAME_LENGTH

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
JOB_CATEGORY = [
    ('STANDARD', 'Standard'),
    ('EVENT', 'Event'),
]


class Job(models.Model):
    """
    Job Model which is a container for job information and anchor for related records
    """
    _name = 'jobcontrol.job'
    _description = 'main model for jobs'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    number = fields.Char("Job_ID", required=True)
    display_name = fields.Char(compute="_display_name", string="Display")
    description = fields.Text("Description", required=False)
    category = fields.Selection(selection=JOB_CATEGORY, string="Category", default='STANDARD')
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
    job_cost_line = fields.One2many(
        comodel_name='jobcontrol.job_costs',
        inverse_name='job_id',
        string='Job Costs'
    )
    job_cost_line_to_invoice = fields.One2many(
        comodel_name='jobcontrol.job_costs',
        inverse_name='job_id',
        string='Job Costs to invoice',
        domain=[('invoiced', '=', False)]
    )
    job_event_line = fields.One2many(
        comodel_name='jobcontrol.eventmanagement.event',
        inverse_name='job_id',
        string='Events'
    )

    def _display_name(self):
        for record in self:
            record.display_name = shorten_text(f"{record.number} {record.name}", MAX_NAME_LENGTH)

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
    job_id = fields.Many2one(comodel_name='jobcontrol.job', string="Job")
    event_id = fields.Many2one(comodel_name="jobcontrol.eventmanagement.event", string="Event")

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Adding job ids to the generated invoices
        """
        print(f"Creating invoices for {self}")
        job_id = 0
        for order in self:
            print(f"Creating invoices for job={order.job_id.id} order={order.ids}")
            if order.job_id.id != 0:
                job_id = order.job_id.id
                break
        res = super(JobSales, self)._create_invoices(grouped, final, date)
        if job_id:
            for move in res:
                move.job_id = job_id
        return res


class JobPurchase(models.Model):
    """
    Extends the standard purchase model to have a relation to jobcontrol.job.
    """
    _inherit = 'purchase.order'
    subject = fields.Char(string="Subject")
    job_id = fields.Many2one(comodel_name='jobcontrol.job', string="Job")
    session_id = fields.Many2one(comodel_name='jobcontrol.eventmanagement.session', string="Event Session")
    event_id = fields.Many2one(comodel_name="jobcontrol.eventmanagement.event", string="Event")

    def _prepare_invoice(self):
        invoice_vals = super(JobPurchase, self)._prepare_invoice()
        if self.job_id:
            invoice_vals.update({
                'job_id': self.job_id.id
            })
        return invoice_vals

    @api.depends("event_id", "session_id")
    def _compute_tax_totals(self):
        for record in self:
            if record.session_id:
                record.event_id = record.session_id.event_id.id
                record.job_id = record.event_id.job_id.id
                print(f"Set EventID={record.event_id.id} JobID={record.job_id.id}")
        super(JobPurchase, self)._compute_tax_totals()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['session_id']:
                session_rec = self.env['jobcontrol.eventmanagement.session'].browse(vals['session_id'])
                if session_rec.event_id:
                    vals['event_id'] = session_rec.event_id.id
                    print(f"Set EventID={session_rec.event_id.id}")
                    event_rec = self.env['jobcontrol.eventmanagement.event'].browse(session_rec.event_id.id)
                    if event_rec.job_id:
                        vals['job_id'] = event_rec.job_id.id
                        print(f"Set JobID={event_rec.job_id.id}")

        super().create(vals_list)
