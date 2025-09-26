from odoo import models,fields


class ResUsersInherit(models.Model):
    _inherit = "res.users"

    numero_de_identificacion = fields.Char(string="Numero de Identificacion CI/RUC")

    nacionalidad_related = fields.Many2one(comodel_name="res.country",related='partner_id.country_id')