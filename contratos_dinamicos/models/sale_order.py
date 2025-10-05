from odoo import models, fields,api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import logging
_logger = logging.getLogger(__name__)



class ContratoDinamico(models.Model):
    _name = "contrato.dinamico"
    _description = "Contrato Dinamico"

    name = fields.Char(string="Nombre del Contrato", required=True)
    contract_template = fields.Html()

    state = fields.Selection([
        ('draft', 'Cotización'),
        ('sent', 'Cotización Enviada'),
        ('sale', 'Orden de Venta'),
        ('cancel', 'Cancelado'),
    ], string="Estado de la venta", readonly=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    contrato_dinamico = fields.Many2one("contrato.dinamico", string="Tipo de Contrato",
                                        help="Selecciona el contrato dinamico correspondiente")
                                        
    contrato_formateado = fields.Html()

    propietario_vivienda = fields.Many2one('info.vendedor', string="Propietario de la Vivienda",
                                           help="Selecciona el propietario de la vivienda")

    es_mensual = fields.Boolean(
            compute="_compute_es_mensual",
            store=True)

    @api.depends('order_line.product_template_id.tipo_de_alquiler')
    def _compute_es_mensual(self):
        for order in self:
            tipos = order.order_line.mapped('product_template_id.tipo_de_alquiler')
            order.es_mensual = 'mensual' in tipos


    @api.model
    def write(self, vals):
        """ Sobreescribe el campo 'state' en info.vendedor cuando cambia el state de sale.order """
        res = super(SaleOrder, self).write(vals)

        # Si el estado cambia, actualizamos 'state' en info.vendedor
        if 'state' in vals:
            for order in self:
                if order.propietario_vivienda:
                    # Actualiza el estado de 'info.vendedor' con el nuevo 'state' de 'sale.order'
                    order.propietario_vivienda.write({'state': order.state})
        return res
    

    @api.model
    def write(self, vals):
        """ Sobreescribe el campo 'state' en contrato.dinamico cuando cambia el state de sale.order """
        res = super(SaleOrder, self).write(vals)

        # Si el estado cambia, actualizamos 'state' en contrato.dinamico
        if 'state' in vals:
            for order in self:
                if order.contrato_dinamico:
                    # Actualiza el estado de 'contrato.dinamico' con el nuevo 'state' de 'sale.order'
                    order.contrato_dinamico.write({'state': order.state})
        return res
    
    @api.model
    def write(self, vals):
        """ Sobreescribe el campo 'state' en sale.order.line cuando cambia el state de sale.order """
        res = super(SaleOrder, self).write(vals)

        # Si el estado cambia, actualizamos 'state' en sale.order.line
        if 'state' in vals:
            for order in self:
                if order.state == 'sale':  # Cuando el estado es 'sale'
                    # Actualiza el estado de todas las líneas del pedido
                    for line in order.order_line:
                        line.write({'state': 'sale'})  # Aseguramos que las líneas tienen el estado 'sale'
                    
                    # Si el estado es 'sale', ocultamos la posibilidad de agregar productos y otras secciones.
                    # Esto se hará en la vista XML de la siguiente manera
        return res

    @api.depends('order_line.product_template_id.tipo_de_alquiler',
                 'rental_start_date', 'rental_return_date')
    def _compute_duration(self):
        for order in self:
            tipos = order.order_line.mapped('product_template_id.tipo_de_alquiler')

            # default para evitar ValueError
            order.remaining_hours = 0

            # Caso: no hay tipo de alquiler
            if not any(tipos):
                order.duration_days = 0
                order.rental_start_date = False
                order.rental_return_date = False
                continue

            # Caso: alquiler mensual
            if 'mensual' in tipos:
                order.duration_days = 30
                continue

            # Caso: alquiler por día (usar lógica nativa)
            if 'por_dia' in tipos:
                if order.rental_start_date and order.rental_return_date:
                    diff = fields.Datetime.from_string(order.rental_return_date) - fields.Datetime.from_string(order.rental_start_date)
                    order.duration_days = diff.days + 1  # incluir el día final
                else:
                    order.duration_days = 0

                continue

    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    MESES = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
    }


    def _formatear_fecha(self,fecha_str):
        """Convierte '2024-11-01' -> '1 de NOVIEMBRE de 2024 (1/11/2024)'"""
        if not fecha_str:
            return False
        fecha_dt = fields.Date.from_string(fecha_str)
        dia = fecha_dt.day
        mes = self.MESES[fecha_dt.month]
        anio = fecha_dt.year
        fecha_larga = f"{dia} de {mes} de {anio}"
        fecha_corta = f"{dia}/{fecha_dt.month}/{anio}"
        return f"{fecha_larga} ({fecha_corta})"


    def reemplazar_campos(self):

        contrato_anterior = self.contrato_dinamico.contract_template or ""

        dia = datetime.now().day
        mes = datetime.now().month
        anio = datetime.now().year

        texto = f'a los {dia} días del mes de {self.meses[mes]} del {anio}'

        #Fecha actual
        contrato_anterior = contrato_anterior.replace('FECHA_DE_HOY', texto)

        #SECCION FICHA DEL PRODUCTO / MODULO INVENTARIO

        for lineas in self.order_line:
            producto = lineas.product_id

            # Piso del departamento
            if producto.piso:
                contrato_anterior = contrato_anterior.replace('PISO_ID', producto.piso)
            else:
                contrato_anterior = contrato_anterior.replace('PISO_ID', 'No se especifico el piso del departamento en la ficha del producto')

            # Bloque del departamento
            
            if producto.bloque:
                contrato_anterior = contrato_anterior.replace('BLOQUE_ID', producto.bloque)
            else:
                contrato_anterior = contrato_anterior.replace('BLOQUE_ID', 'No se especifico el bloque del departamento en la ficha del producto')
            
            # Departamento
            if producto.departamento:
                contrato_anterior = contrato_anterior.replace('DEPARTAMENTO_ID', producto.departamento)
            else:
                contrato_anterior = contrato_anterior.replace('DEPARTAMENTO_ID', 'No se ingreso ninguna descripcion del departamento en la ficha del producto')

            # Ubicacion
            if producto.ubicacion:
                contrato_anterior = contrato_anterior.replace('UBICACION_ID', producto.ubicacion)
            else:
                contrato_anterior = contrato_anterior.replace('UBICACION_ID', 'No se especifico la ubicacion del departamento en la ficha del producto')

            # NIS de la ANDE
            if producto.nis:
                contrato_anterior = contrato_anterior.replace('NIS_ID', producto.nis)
            else:
                contrato_anterior = contrato_anterior.replace('NIS_ID', 'No se especifico el NIS de la ANDE en la ficha del producto')

            # Numero 
            if producto.medidor:
                contrato_anterior = contrato_anterior.replace('NUMERO_MEDIDOR_ID', producto.medidor)
            else:
                contrato_anterior = contrato_anterior.replace('NUMERO_MEDIDOR_ID', 'No se ingreso el numero del medidor en la ficha del producto')
            
            if producto.dias_gracia:
                contrato_anterior = contrato_anterior.replace('DIAS_DE_COBRO_SINMORA', str(producto.dias_gracia))
            else:
                contrato_anterior = contrato_anterior.replace('DIAS_DE_COBRO_SINMORA', 'No se especifico la cantidad de dias sin mora en la ficha del producto')
            

        # SECCION MODULO CONTRATOS

        # Numero del Contrato
        contrato_anterior = contrato_anterior.replace('NUMERO_CONTRATO', self.name)

        # Fecha de Inicio de Contrato
        if self.rental_start_date:
            fecha_inicio_fmt = self._formatear_fecha(self.rental_start_date)
            contrato_anterior = contrato_anterior.replace('FECHA_INICIO_CONTRATO', fecha_inicio_fmt)
        else:
            contrato_anterior = contrato_anterior.replace('FECHA_INICIO_CONTRATO', 'No se indicó la fecha de inicio del contrato')

        # Fecha Fin de Contrato
        if self.rental_return_date:
            fecha_fin_fmt = self._formatear_fecha(self.rental_return_date)
            contrato_anterior = contrato_anterior.replace('FECHA_FIN_CONTRATO', fecha_fin_fmt)
        else:
            contrato_anterior = contrato_anterior.replace('FECHA_FIN_CONTRATO', 'No se indicó la fecha de fin del contrato')

        # Nombre del cliente
        if self.partner_id.name:
            contrato_anterior = contrato_anterior.replace('NOMBRE_CLIENTE', self.partner_id.name)
        else:
            contrato_anterior = contrato_anterior.replace('NOMBRE_CLIENTE', 'No se ingreso el nombre del cliente en la ficha del contacto')
        
        # Correo del cliente
        if self.partner_id.email:
            contrato_anterior = contrato_anterior.replace('EMAIL_CLIENTE', self.partner_id.email)
        else: 
            contrato_anterior = contrato_anterior.replace('EMAIL_CLIENTE', 'No se ingreso el correo electronico del cliente en la ficha del contacto')
        
        # RUC/CI del cliente
        if self.partner_id.vat:
            contrato_anterior = contrato_anterior.replace('N_IDENTIFICACION_CLIENTE', self.partner_id.vat)
        else:
            contrato_anterior = contrato_anterior.replace('N_IDENTIFICACION_CLIENTE', 'No se ingreso el numero de RUC/CI del cliente en la ficha del contacto')
        
        # Telefono o Movil del cliente
        if self.partner_id.mobile or self.partner_id.phone:
            contrato_anterior = contrato_anterior.replace('TELEFONO_CLIENTE', self.partner_id.mobile or self.partner_id.phone)
        else:
            contrato_anterior = contrato_anterior.replace('TELEFONO_CLIENTE', 'No se ingreso el numero de telefono del cliente en la ficha del contacto')

        # Ciudad del cliente
        if self.partner_id.city:
            contrato_anterior = contrato_anterior.replace('CIUDAD_ID', self.partner_id.city)
        else:
            contrato_anterior = contrato_anterior.replace('CIUDAD_ID', 'La ciudad del empleado se encuentra vacia en la ficha del contacto')

        # Calle 1 y 2 de la direccion del cliente

        # Obtener los valores de street y street2 si existen
        street = self.partner_id.street or ''
        street2 = self.partner_id.street2 or ''

        # Generar la direccion
        if street and street2:
            direccion_formateada = f"{street}, {street2}."
        elif street:
            direccion_formateada = street
        elif street2:
            direccion_formateada = street2
        else:
            direccion_formateada = ''

        contrato_anterior = contrato_anterior.replace('CALLE_1', direccion_formateada)
        contrato_anterior = contrato_anterior.replace('CALLE_2', '')  # Si existe CALLE_2, se limpia

        if self.user_id:
            contrato_anterior = contrato_anterior.replace('NOMBRE_VENDEDOR', self.user_id.name)
        else:
            contrato_anterior = contrato_anterior.replace('NOMBRE_VENDEDOR', 'No hay un vendedor asignado, debe especificar el vendedor en la pagina "Otra informacion"')

        if self.user_id.login:
            contrato_anterior = contrato_anterior.replace('EMAIL_VENDEDOR', self.user_id.login)
        else:
            contrato_anterior = contrato_anterior.replace('EMAIL_VENDEDOR', 'No hay un correo registrado del vendedor asignado. Debe completarlo en la pagina "Otra informacion"')
        
        if self.user_id.phone:
            contrato_anterior = contrato_anterior.replace('TELEFONO_VENDEDOR', self.user_id.phone)
        else:
            contrato_anterior = contrato_anterior.replace('TELEFONO_VENDEDOR', 'No hay un numero de telefono registrado del vendedor asignado. Debe completarlo en la pagina "Otra informacion"')

        if self.user_id.numero_de_identificacion:
            contrato_anterior = contrato_anterior.replace('N_IDENTIFICACION_VENDEDOR', self.user_id.numero_de_identificacion)
        else:
            contrato_anterior = contrato_anterior.replace('N_IDENTIFICACION_VENDEDOR', 'No hay un numero de identificacion registrado del vendedor asignado. Debe completarlo en la pagina "Otra informacion"')


        self.contrato_formateado = contrato_anterior
        return self.contrato_formateado
    
    alquiler_state = fields.Selection([
        ('reservado', 'Reservado'),
        ('en_uso', 'En uso'),
        ('mantenimiento', 'Mantenimiento'),
        ('disponible', 'Disponible'),
    ], string="Estado del alquiler", default="disponible")          


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'
    
    state = fields.Selection([
        ('draft', 'Cotización'),
        ('sent', 'Cotización Enviada'),
        ('sale', 'Orden de Venta'),
        ('cancel', 'Cancelado'),
    ], string="Estado de la venta", readonly=True)


