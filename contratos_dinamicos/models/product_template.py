from odoo import models, fields


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    piso = fields.Char("Piso")
    bloque = fields.Char("Bloque")
    departamento = fields.Char("Departamento")
    ubicacion = fields.Char("Ubicación del inmueble")
    nis = fields.Char("NIS Ande")
    medidor = fields.Char("N° de Medidor")
    dias_gracia = fields.Integer("Días de cobro sin mora", default=5)
    tipo_de_alquiler = fields.Selection(
        [('mensual', 'Mensual'),
        ('por_dia','Por dia')],
        string="Tipo de Alquiler", default=False)

    def get_fecha_formateada(self):
        if self.start_date:
            meses = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            dia = self.start_date.day
            mes = meses.get(self.start_date.month, '')
            anio = self.start_date.year
            return f"{dia} de {mes} de {anio}"
        return ''