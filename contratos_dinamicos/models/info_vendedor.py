from odoo import models,fields


class InfoVendedor(models.Model):
    _name = 'info.vendedor'
    _description = "Información del Vendedor"

    name = fields.Char(string="Nombre", required=True)
    email = fields.Char(string="Correo Electrónico")
    numero_de_identificacion = fields.Char(string="Número de Identificación CI/RUC")
    phone = fields.Char(string="Numero de Télefono")
    nacionalidad_id = fields.Many2one("res.country", string="Nacionalidad")
    image_1920 = fields.Image(string="Imagen", max_width=1920, max_height=1920)
