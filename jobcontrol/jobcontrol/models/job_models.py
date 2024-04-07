# -*- coding: utf-8 -*-

from odoo import models, fields, api

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

MAX_NAME_LENGTH = 28


def shorten_text(text: str, max_length: int) -> str:
    """
    Shortens a text to max_length
    """
    return f"{(text[:max_length] + '...') if len(text) > max_length else text}"


class JobCategory(models.Model):
    """
    Job Category allows assigning categories to jobs
    """
    _name = 'jobcontrol.job_category'
    _description = 'categories for jobs'

    name = fields.Char("Name", required=True)
    description = fields.Text("Description", required=False)
    display_name = fields.Char(compute="_display_name", string="Display")

    job_lines = fields.One2many(
        comodel_name='jobcontrol.job',
        inverse_name='job_category_id',
        string='Jobs'
    )

    def _display_name(self):
        for record in self:
            record.display_name = shorten_text(f"{record.name}", MAX_NAME_LENGTH)


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
    job_category_id = fields.Many2one('jobcontrol.job_category', string="Job Category")
    job_cost_line = fields.One2many(
        comodel_name='jobcontrol.job_costs',
        inverse_name='job_id',
        string='Job Costs'
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


class JobCosts(models.Model):
    """
    Costs, which are related to a job
    """
    _name = 'jobcontrol.job_costs'
    _description = 'Costs related to jobs'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    description = fields.Text("Description", required=False)
    display_name = fields.Char(compute="_display_name", string="Display")
    job_id = fields.Many2one('jobcontrol.job', string="Job")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    unit_price = fields.Float(string="Unit Price", required=True, digits=(12, 4))
    total_price = fields.Monetary(string="Total Price", compute='_compute_total_price', inverse="_compute_unit_price",
                                  store=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id', 'product_uom_qty', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.unit_price * line.product_uom_qty
            print(f"_compute_total_price: unit_price={line.unit_price} >> total_price={line.total_price}")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.unit_price = line.product_id.lst_price
            print(f"_onchange_product_id:{line.product_id.name} >> line.unit_price={line.unit_price}")

    @api.onchange('total_price')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.total_price / line.product_uom_qty
            print(f"_compute_unit_price: total_price={line.total_price} >> unit_price={line.unit_price}")

    def _display_name(self):
        for record in self:
            record.display_name = shorten_text(f"{record.name} {record.product_uom_qty} "
                                               f"{record.product_uom.name}", MAX_NAME_LENGTH)

