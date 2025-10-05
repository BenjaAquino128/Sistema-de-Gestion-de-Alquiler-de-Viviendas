from odoo import models,fields,api
import logging

_logger = logging.getLogger(__name__)


class InfoVendedor(models.Model):
    _name = 'info.vendedor'
    _description = "Información del Vendedor"

    name = fields.Char(string="Nombre", required=True)
    email = fields.Char(string="Correo Electrónico")
    numero_de_identificacion = fields.Char(string="Número de Identificación CI/RUC")
    phone = fields.Char(string="Numero de Télefono")
    nacionalidad_id = fields.Many2one("res.country", string="Nacionalidad")
    image_1920 = fields.Image(string="Imagen", max_width=1920, max_height=1920)

    propietario_vivienda = fields.Many2one('sale.order', string="Venta relacionada")

    state = fields.Selection([
        ('draft', 'Cotización'),
        ('sent', 'Cotización Enviada'),
        ('sale', 'Orden de Venta'),
        ('cancel', 'Cancelado'),
    ], string="Estado de la venta", readonly=True)