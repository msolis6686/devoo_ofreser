# -*- coding: utf-8 -*-

# Utilities
import datetime
from datetime import datetime as dt

# Odoo
from odoo import models, fields, api, exceptions


class OfreserOrdenDeTrabajo(models.Model):
    _name = 'ofreser.orden_de_trabajo'
    _description = 'Ofreser - Orden de Trabajo'
    _rec_name = 'numero_comprobante'
    _order = "fecha_servicio desc"

    # FIELDS
    estado = fields.Selection(
        selection=[('en_espera', 'En Espera'),
                   ('en_proceso', 'En Proceso'),
                   ('reprogramar', 'Reprogramar'),
                   ('finalizado', 'Finalizado'),
                   ('cancelado', 'Cancelado')],
        string='Estado',
        default="en_espera"
    )
    numero_comprobante = fields.Char(string='N° de Comprobante')
    usa_certificado = fields.Boolean(string='Usa Certificado', default=True)
    certificado_id = fields.Many2one(
        comodel_name='ofreser.certificado',
        string='N° de Certificado'
    )

    fecha_servicio = fields.Datetime(string='Fecha de Servicio', required=True)
    fecha_vencimiento = fields.Datetime(string='Fecha de Vencimiento')
    nuevo = fields.Selection(
        selection=[('activo', 'Activo'), ('no_activo', 'No activo')],
        string='Nuevo'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True
    )
    domicilio = fields.Char(string='Domicilio', required=True)
    telefono = fields.Char(string='Teléfono',)
    movil = fields.Char(string='Celular',)
    email = fields.Char(string='Email', required=True)
    cuit = fields.Char(string='Cuit')
    rubro_id = fields.Many2one(comodel_name='ofreser.rubro', string='Rubro')
    contacto = fields.Char(string="Contacto")
    turnos = fields.Integer(
        string='Turnos',
        default=0,
        help="Cantidad de turnos asignados a esta orden de trabajo. Cada turno son 30 minutos")
    duracion_turno = fields.Integer(string='Duración de turno', default=30)
    precio = fields.Float(string='Precio')
    factura = fields.Char(string='Factura')
    pagado = fields.Selection(
        selection=[('si', 'Si'), ('no', 'No')],
        string='Pago',
        default='no'
    )
    mano_de_obra_utilizada_ids = fields.One2many(
        comodel_name='ofreser.mano_de_obra_utilizada',
        inverse_name='orden_de_trabajo_id',
        string='Mano de Obra')
    mano_de_obra_utilizada_display = fields.Char(string="Mano de Obra")
    porcentajes_extra_ids = fields.One2many(
        comodel_name='ofreser.porcentaje_extra',
        inverse_name='orden_de_trabajo_id',
        string='Porcentajes Extra')
    maquinas_utilizadas_ids = fields.One2many(
        comodel_name='ofreser.maquina_utilizada',
        inverse_name='orden_de_trabajo_id',
        string='Máquinas utilizadas')
    movilidad_utilizadas_ids = fields.One2many(
        comodel_name='ofreser.movilidad_utilizada',
        inverse_name='orden_de_trabajo_id',
        string='Movilidad Utilizada')
    productos_consumidos_ids = fields.One2many(
        comodel_name='ofreser.producto_consumido',
        inverse_name='orden_de_trabajo_id',
        string='Productos')
    tipos_de_trabajo_display = fields.Char(string="Tipos de Trabajo")
    tipos_de_trabajo_ids = fields.Many2many(
        comodel_name='ofreser.tipo_de_trabajo',
        string='Tipos de Trabajo')
    promotores_ids = fields.One2many(
        comodel_name='ofreser.promotor',
        inverse_name='orden_de_trabajo_id',
        string='Promotores')
    maquinas_ids = fields.Many2many(
        comodel_name='ofreser.maquina',
        string='Máquinas')
    superficie_total_inmueble = fields.Integer(
        string='Superficie Total Inmueble(m2)')
    superficie_total_tratada = fields.Integer(
        string='Superficie Tratada(m2)')
    observaciones = fields.Text('Observaciones')
    firma_archivo_nombre = fields.Char(string="Nombre de Archivo")
    firma_archivo = fields.Binary(string="Firma")
    maximo_porcentaje_mano_de_obra = fields.Integer(
        string='Máximo Porcentaje - M.O.',
        compute='_compute_porcentaje_maximo_mo',
        store=True
    )
    maximo_porcentaje_promotores = fields.Integer(
        string='Máximo Porcentaje - Prom.',
        compute='_compute_porcentaje_maximo_prom',
        store=True
    )
    calendar_event_id = fields.Many2one(
        comodel_name='calendar.event',
        string='Evento Calendario'
    )
    user_es_admin = fields.Boolean(
        string='User es admin',
        compute='_compute_user_es_admin'
    )
    aviso_vencimiento = fields.Boolean(string='Aviso de vencimiento')
    fecha_aviso_vencimiento = fields.Datetime(string='Fecha de aviso')

    ######################################################
    # COMPUTED
    ######################################################
    @api.one
    def _compute_user_es_admin(self):
        # import pdb; pdb.set_trace()
        self.user_es_admin = self.env.user.has_group('devoo_ofreser.grupo_administracion_ordenes')

    ######################################################
    # ONCHANGES
    ######################################################
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.telefono = self.partner_id.phone
            self.movil = self.partner_id.mobile
            self.email = self.partner_id.email
            self.cuit = self.partner_id.cuit
            if self.partner_id.street and self.partner_id.street2:
                self.domicilio = "{street} {street2}".format(self.partner_id.street, self.partner_id.street2)
            else:
                self.domicilio = self.partner_id.street
            # Datos de la última orden de trabajo
            ordenes = self.search([('partner_id', '=', self.partner_id.id)], order="fecha_servicio desc")
            if ordenes:
                ultima_orden = ordenes[0]
                self.contacto = ultima_orden.contacto
                self.rubro_id = ultima_orden.rubro_id
                self.superficie_total_inmueble = ultima_orden.superficie_total_inmueble
                self.tipos_de_trabajo_ids = ultima_orden.tipos_de_trabajo_ids

    ######################################################
    # CONSTRAINS
    ######################################################
    @api.constrains('turnos')
    def validate_a_turnos(self):        
        print('1.- turnos')
        if self.turnos <= 0:
            raise exceptions.ValidationError('La cantidad de turnos debe ser mayor a 0')

    @api.constrains('mano_de_obra_utilizada_ids')
    def validate_b_mano_de_obra_utilizada_ids(self):
        print('2.- mano de obra ids')
        if not self.mano_de_obra_utilizada_ids:
            raise exceptions.ValidationError('Debe seleccionar al menos un operador en Mano de obra utilizada')
        elif not all([mano_obra.user_id.id for mano_obra in self.mano_de_obra_utilizada_ids]):
            raise exceptions.ValidationError('Todos los registros de Mano de Obra deben tener un operador asignado')
        return True

    @api.constrains('tipos_de_trabajo_ids')
    def validate_c_tipos_de_trabajo_ids(self):
        print('3.- tipos de trabajos')
        if not self.tipos_de_trabajo_ids:
            raise exceptions.ValidationError('Debe seleccionar al menos un tipo de trabajo')
        return True

    @api.constrains('fecha_servicio', 'mano_de_obra_utilizada_ids')
    def validate_d_fecha_servicio_libre(self):
        msg = ""
        for mano_obra in self.mano_de_obra_utilizada_ids:
            employee = mano_obra.user_id
            partner = employee.user_id.partner_id

            calendar_duration_mins = self.duracion_turno * self.turnos
            event_start = self.fecha_servicio
            event_stop_dt = fields.Datetime.from_string(self.fecha_servicio) + datetime.timedelta(minutes=calendar_duration_mins)
            event_stop = fields.Datetime.to_string(event_stop_dt)
            concurrent_events = self.env['calendar.event'].search([
                '|', '&', ('start', '<=', event_start), ('stop', '>', event_start),
                '|', '&', ('start', '<', event_stop), ('stop', '>=', event_stop),
                '|', '&', ('start', '>=', event_start), ('stop', '<=', event_stop),
                '&', ('start', '<=', event_start), ('stop', '>=', event_stop),
            ])
            if concurrent_events:
                concurrent_events = concurrent_events.filtered(lambda r: r.id != self.calendar_event_id.id)
                for event in concurrent_events:
                    if partner in event.partner_ids:
                        msg += u"El operador {} tiene el trabajo {} en ese horario\n".format(partner.name, event.name)
        if msg:
            raise exceptions.ValidationError(msg)
        print('4.- validacion fecha servicio y mano de obra')

    @api.constrains('movilidad_utilizadas_ids')
    def validate_movilidad_utilizadas_ids(self):
        max_porcentaje = self.env.ref('devoo_ofreser.porcentaje_maximo_movilidad').porcentaje_maximo
        print('-' * 80)
        print(max_porcentaje)
        for mov in self.movilidad_utilizadas_ids:
            if mov.porcentaje > max_porcentaje:
                raise exceptions.ValidationError('El porcentaje máximo por movilidad es de {}%'.format(max_porcentaje))

    @api.constrains('maquinas_utilizadas_ids')
    def validate_maquinas_utilizadas_ids(self):
        max_porcentaje = self.env.ref('devoo_ofreser.porcentaje_maximo_maquina').porcentaje_maximo
        print('-' * 80)
        print(max_porcentaje)
        for maq in self.maquinas_utilizadas_ids:
            if maq.porcentaje > max_porcentaje:
                raise exceptions.ValidationError('El porcentaje máximo por maquina es de {}%'.format(max_porcentaje))

    ######################################################
    # ORM OVERRIDES
    ######################################################
    @api.model
    def create(self, vals):
        print("Cacho")
        res = super(OfreserOrdenDeTrabajo, self).create(vals)
        res.numero_comprobante = self.env['ir.sequence'].next_by_code(
            'orden_de_trabajo_sequence')
        # Validar porcentajes si es que tiene un tipo de trabajo asignado
        if res.tipos_de_trabajo_ids:
            porcentaje_maximo_mano_obra = min([tipo.porcentaje_maximo_mano_obra for tipo in res.tipos_de_trabajo_ids])
            suma_porcentaje_mano_obra = sum([mano_obra.porcentaje for mano_obra in res.mano_de_obra_utilizada_ids])
            res.validar_porcentajes('Mano de Obra', porcentaje_maximo_mano_obra, suma_porcentaje_mano_obra)

            porcentaje_maximo_promotores = min([tipo.porcentaje_maximo_promotores for tipo in res.tipos_de_trabajo_ids])
            suma_porcentaje_promotores = sum([promotor.porcentaje for promotor in res.promotores_ids])
            res.validar_porcentajes('Promotores', porcentaje_maximo_promotores, suma_porcentaje_promotores)
        # Crear calendar.event
        calendar_name = u"{} - {}".format(res.numero_comprobante, res.partner_id.name)

        partner_ids = []
        for mo_utilizada in res.mano_de_obra_utilizada_ids:
            if mo_utilizada.user_id.user_id:
                partner_ids.append(mo_utilizada.user_id.user_id.partner_id.id)
            elif mo_utilizada.user_id.partner_id:
                partner_ids.append(mo_utilizada.user_id.partner_id.id)

        calendar_partner_ids = [
            (6, 0, partner_ids)
        ]
        # (6, 0, [mo_utilizada.user_id.user_id.partner_id.id for mo_utilizada in res.mano_de_obra_utilizada_ids if mo_utilizada.user_id.user_id])
        # import pdb; pdb.set_trace()
        calendar_duration_mins = res.duracion_turno * res.turnos
        calendar_stop = fields.Datetime.from_string(res.fecha_servicio) + datetime.timedelta(minutes=calendar_duration_mins)

        calendar_event_vals = {
            'name': calendar_name,
            'partner_ids': calendar_partner_ids,
            'start': res.fecha_servicio,
            'stop': fields.Datetime.to_string(calendar_stop),
            'start_datetime': res.fecha_servicio,
            'location': res.domicilio,
            'user_id': self.env.user.id,
        }
        calendar_event_res = self.env['calendar.event'].create(calendar_event_vals)
        res.calendar_event_id = calendar_event_res.id
        # Generar el display de mano de obra y tipos de trabajo
        res.mano_de_obra_utilizada_display = res.get_mano_de_obra_display()
        res.tipos_de_trabajo_display = res.get_tipo_de_trabajo_display()
        # Actualiazr el email
        if res.partner_id and res.email:
            res.actualizar_partner_email(res.partner_id.id, res.email)
        # Actualiazr el cuit
        if res.partner_id and res.cuit:
            res.actualizar_partner_cuit(res.partner_id.id, res.cuit)
        # Actualizar info del certificado
        if res.certificado_id:
            res.set_certificado()
        return res

    @api.multi
    def write(self, vals):
        res = super(OfreserOrdenDeTrabajo, self).write(vals)
        # self.validar_tipos_de_trabajo()

        # Previene el loop de writes una vez que se escribe este valor
        if 'mano_de_obra_utilizada_display' in vals:
            return res
        # Previene el loop de writes una vez que se escribe este valor
        if 'tipos_de_trabajo_display' in vals:
            return res

        # Validar porcentajes si es que tiene un tipo de trabajo asignado
        if self.tipos_de_trabajo_ids:
            porcentaje_maximo_mano_obra = min([tipo.porcentaje_maximo_mano_obra for tipo in self.tipos_de_trabajo_ids])
            suma_porcentaje_mano_obra = sum([mano_obra.porcentaje for mano_obra in self.mano_de_obra_utilizada_ids])
            self.validar_porcentajes('Mano de Obra', porcentaje_maximo_mano_obra, suma_porcentaje_mano_obra)

            porcentaje_maximo_promotores = min([tipo.porcentaje_maximo_promotores for tipo in self.tipos_de_trabajo_ids])
            suma_porcentaje_promotores = sum([promotor.porcentaje for promotor in self.promotores_ids])
            self.validar_porcentajes('Promotores', porcentaje_maximo_promotores, suma_porcentaje_promotores)
        # Calcular el promotor y cambiar automaticamente en clientes
        if self.partner_id:
            porcentajes = [
                (prom.promotor_id.id, prom.porcentaje, prom.promotor_id.name) for prom in self.promotores_ids
            ] if self.promotores_ids else None
            if porcentajes:
                maximo = porcentajes[0]
                for porcentaje in porcentajes:
                    if porcentaje[1] > maximo[1]:
                        maximo = porcentaje
                self.partner_id.promotor_id = self.env['hr.employee'].browse(maximo[0])
        # Modificar el event.calendar con los datos de la orden
        if self.calendar_event_id:
            calendar_partner_ids = [(6, 0, [mo_utilizada.user_id.user_id.partner_id.id for mo_utilizada in self.mano_de_obra_utilizada_ids])]
            calendar_duration_mins = self.duracion_turno * self.turnos
            calendar_stop = fields.Datetime.from_string(self.fecha_servicio) + datetime.timedelta(minutes=calendar_duration_mins)
            calendar_stop = fields.Datetime.to_string(calendar_stop)
            self.calendar_event_id.partner_ids = calendar_partner_ids
            # import pdb; pdb.set_trace()
            # self.calendar_event_id.start = self.fecha_servicio
            # self.calendar_event_id.stop = calendar_stop
            self.calendar_event_id.write({'start': self.fecha_servicio, 'stop': calendar_stop})
            self.calendar_event_id.location = self.domicilio
            self.calendar_event_id.duration = self.calendar_event_id._get_duration(self.calendar_event_id.start, self.calendar_event_id.stop)
        # Generar el display de mano de obra y tipos de trabajo
        self.mano_de_obra_utilizada_display = self.get_mano_de_obra_display()
        self.tipos_de_trabajo_display = self.get_tipo_de_trabajo_display()
        # Actualiazr el email
        if self.partner_id and self.email:
            self.actualizar_partner_email(self.partner_id.id, self.email)
        # Actualiazr el cuit
        if self.partner_id and self.cuit:
            self.actualizar_partner_cuit(self.partner_id.id, self.cuit)
        # Actualizar info del certificado
        if self.certificado_id:
            print('entro a set_certificado')
            self.set_certificado()

        # Propagar cambios en liquidaciones
        liquidacion = self.env['ofreser.liquidacion'].search([('orden_de_trabajo_id', '=', self.id)])
        if liquidacion:
            for liquidacion in liquidacion.mano_de_obra_liquidacion_ids:
                # liquidacion.empleado_id
                # ver si se encuentra el empleado en las liquidaciones
                # si no esta en las liquidaciones armar valores para nueva liquidacion
                for mo in self.mano_de_obra_utilizada_ids:
                    if liquidacion.empleado_id == mo.user_id:
                        liquidacion.porcentaje_num_mano_de_obra = mo.porcentaje
                        liquidacion.porcentaje_mano_de_obra = mo.porcentaje / 100 * self.precio

                for prom in self.promotores_ids:
                    if liquidacion.empleado_id == prom.promotor_id:
                        liquidacion.porcentaje_num_promocion = prom.porcentaje
                        liquidacion.porcentaje_promocion = prom.porcentaje / 100 * self.precio

                for mov in self.movilidad_utilizadas_ids:
                    if liquidacion.empleado_id == mov.responsable_id:
                        liquidacion.porcentaje_num_movilidad = mov.porcentaje
                        liquidacion.porcentaje_movilidad = mov.porcentaje / 100 * self.precio

                for maq in self.maquinas_utilizadas_ids:
                    if liquidacion.empleado_id == maq.responsable_id:
                        liquidacion.porcentaje_num_maquina = maq.porcentaje
                        liquidacion.porcentaje_maquina = maq.porcentaje / 100 * self.precio

                liquidacion.total_a_pagar = sum([
                    liquidacion.porcentaje_mano_de_obra,
                    liquidacion.porcentaje_maquina,
                    liquidacion.porcentaje_movilidad,
                    liquidacion.porcentaje_promocion,
                    liquidacion.porcentaje_extra
                ])

        return res

    @api.multi
    def unlink(self):
        # import pdb; pdb.set_trace()
        for record in self:
            if record.calendar_event_id:
                record.calendar_event_id.unlink()
            if record.certificado_id:
                record.certificado_id.unlink()

            super(OfreserOrdenDeTrabajo, record).unlink()

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Cambia el comportamiento del agrupamiento en las busquedas del group by
        Cuando se agrupa por fecha de servicio
        """

        if 'fecha_servicio:day' in groupby:
            orderby = 'fecha_servicio DESC' + (orderby and (',' + orderby) or '')

        return super(OfreserOrdenDeTrabajo, self).read_group(domain, fields, groupby, offset=0, limit=limit, orderby=orderby, lazy=lazy)

    ######################################################
    # COMPUTES
    ######################################################
    @api.one
    @api.depends('tipos_de_trabajo_ids')
    def _compute_porcentaje_maximo_mo(self):
        if self.tipos_de_trabajo_ids:
            self.maximo_porcentaje_mano_de_obra = min([tipo.porcentaje_maximo_mano_obra for tipo in self.tipos_de_trabajo_ids])

    @api.one
    @api.depends('tipos_de_trabajo_ids')
    def _compute_porcentaje_maximo_prom(self):
        if self.tipos_de_trabajo_ids:
            self.maximo_porcentaje_promotores = min([tipo.porcentaje_maximo_promotores for tipo in self.tipos_de_trabajo_ids])

    ######################################################
    # ACTIONS
    ######################################################
    @api.multi
    def registrar_pago_orden(self):
        """Marca que la orden esta pagada, para ser llamada desde la vista tree"""
        for rec in self:
            rec.pagado = 'si'

    @api.multi
    def iniciar_orden_de_trabajo(self):
        self.estado = 'en_proceso'

    @api.multi
    def send_mail(self):
        # TODO: cambiar user_id por user_ids segun los operarios
        # que participen en el trabajo
        user_id = self.mano_de_obra_id.id
        base_domain = self.env['ir.config_parameter'].search(
            [('key', '=', 'web.base.url')]).value
        body = """
            <div style="max-width:600px; margin: 0 auto">
              <div>Orden de trabajo {0}</div>
              <div>Cliente: {1}</div>
              <div>Dirección: {2}</div>
              <div>Teléfono: {3}</div>
              <a href="{4}/odtindividual/{5}">
                <div>Ver más</div>
              </a>
            </div>
        """
        body = body.format(
            self.numero_comprobante,
            self.partner_id.name,
            self.domicilio,
            self.telefono,
            base_domain,
            str(self.id))

        asunto = "Orden de Trabajo %s - %s" % (
            self.numero_comprobante, self.partner_id.name)
        mail_details = {
            'subject': asunto,
            'body': body,
            'partner_ids': [(user_id)]
        }

        mail = self.env['mail.thread']
        mail.message_post(
            type="notification",
            subtype="mt_comment",
            **mail_details)

    @api.multi
    def finalizar_orden_de_trabajo(self):
        """Se llama al finalizar la orden de trabajo

        Crea los valores de las liquidación y la liquidación con esos valores
        Cambia el estado del certificado a Usado
        """
        if self.usa_certificado and not self.certificado_id:
            mess = "Para finalizar la orden debe seleccionar un certificado"
            raise exceptions.ValidationError(mess)
        self.estado = 'finalizado'

        # Crear liquidación con la informacion de la orden de trabajo
        liquidacion = self.env['ofreser.liquidacion']

        empleados = []

        empleados = self.sumar_lista_empleados(
            empleados,
            self.mano_de_obra_utilizada_ids,
            'user_id',
            'porcentaje_mano_de_obra',
            'mano_de_obra_utlizada_id'
        )

        empleados = self.sumar_lista_empleados(
            empleados,
            self.promotores_ids,
            'promotor_id',
            'porcentaje_promocion',
            'promotor_id'
        )

        empleados = self.sumar_lista_empleados(
            empleados,
            self.maquinas_utilizadas_ids,
            'responsable_id',
            'porcentaje_maquina',
            'maquina_utilizada_id'
        )

        empleados = self.sumar_lista_empleados(
            empleados,
            self.movilidad_utilizadas_ids,
            'responsable_id',
            'porcentaje_movilidad',
            'movilidad_utilizadas_id'
        )

        empleados = self.sumar_lista_empleados(
            empleados,
            self.porcentajes_extra_ids,
            'user_id',
            'porcentaje_extra',
            'extras_id'
        )

        vals_liquidacion = {
            'orden_de_trabajo_id': self.id,
            'mano_de_obra_liquidacion_ids': self.get_liquidaciones(empleados)
        }
        # import pdb; pdb.set_trace()
        # raise exceptions.UserError('but not yet')

        liquidacion.create(vals_liquidacion)

        # Cambiar el estado del certificado utilizado
        if self.usa_certificado:
            self.certificado_id.estado = 'usado'

    @api.multi
    def reprogramar_orden_de_trabajo(self):
        self.estado = 'reprogramar'

    @api.multi
    def cancelar_orden_de_trabajo(self):
        self.estado = 'cancelado'

    @api.multi
    def see_liquidacion(self):
        res_id = self.env['ofreser.liquidacion'].search(
            [('orden_de_trabajo_id', '=', self.id)]
        ).id
        liquidacion_view_id = self.env.ref(
            'devoo_ofreser.ofreser_liquidacion_form_view').id
        context = {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Liquidacion',
            'res_model': 'ofreser.liquidacion',
            'views': [(liquidacion_view_id, 'form')],
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': res_id,
            'context': context
        }

    @api.multi
    def a_espera_orden_de_trabajo(self):
        self.estado = 'en_espera'

    ######################################################
    # METODOS
    ######################################################
    def get_fecha(self):
        if self.fecha_servicio:
            tiempo_gmt = dt.strptime(self.fecha_servicio, '%Y-%m-%d %H:%M:%S')
            tiempo_local = tiempo_gmt - datetime.timedelta(hours=3)
            return tiempo_local.strftime('%d/%m/%Y %H:%M')
        else:
            return ''

    def sumar_lista_empleados(self, empleados, campos, campo_modelo, nombre_campo, rel):
        """Devuelve una lista de diccionarios por empleado con el empleado id y los demas valores
        son los porcentajes que le corresponden por cada concepto si participa de el
        Agrega a la liquidacion el campo rel, para que se relacione con objeto en particular y accederlo desde otras instancias
        NOTE: hubiera sido mas fácil hacer un loop por todos y simplemente devolver 0 si no tenía ese concepto
        """
        for empleado in campos:
            # campo es el mano_de_obra_utilizada,
            # asi que tiene que ir con gettatr de campo requerido
            empleado_id = getattr(empleado, campo_modelo).id
            # Agrega al empleado el nuevo concepto
            if any(e['empleado_id'] == empleado_id for e in empleados):
                for e in empleados:
                    if e.get('empleado_id') and e.get('empleado_id') == empleado_id:
                        e[nombre_campo] = empleado.porcentaje
                        e[rel] = empleado.id
            # Crea el empleado con el concepto nuevo
            else:
                empleados.append({
                    'empleado_id': empleado_id,
                    nombre_campo: empleado.porcentaje,
                    rel: empleado.id
                })
        return empleados

    def get_liquidaciones(self, empleados):
        mano_de_obra_liquidaciones = []
        for empleado in empleados:
            # import pdb; pdb.set_trace()
            total_porcentajes = (empleado.get('porcentaje_mano_de_obra') or 0) \
                + (empleado.get('porcentaje_maquina') or 0) \
                + (empleado.get('porcentaje_movilidad') or 0) \
                + (empleado.get('porcentaje_extra') or 0) \
                + (empleado.get('porcentaje_promocion') or 0)

            total_a_pagar = self.get_monto(total_porcentajes)
            mano_de_obra_liquidaciones.append((0, 0, {
                'empleado_id': empleado['empleado_id'],
                'porcentaje_num_mano_de_obra': empleado.get('porcentaje_mano_de_obra'),
                'porcentaje_mano_de_obra': self.get_monto(empleado.get('porcentaje_mano_de_obra')),
                'mano_de_obra_utlizada_id': empleado.get('mano_de_obra_utlizada_id'),
                'porcentaje_num_maquina': empleado.get('porcentaje_maquina'),
                'porcentaje_maquina': self.get_monto(empleado.get('porcentaje_maquina')),
                'maquina_utilizada_id': empleado.get('maquina_utilizada_id'),
                'porcentaje_num_movilidad': empleado.get('porcentaje_movilidad'),
                'porcentaje_movilidad': self.get_monto(empleado.get('porcentaje_movilidad')),
                'movilidad_utilizadas_id': empleado.get('movilidad_utilizadas_id'),
                'porcentaje_num_promocion': empleado.get('porcentaje_promocion'),
                'porcentaje_promocion': self.get_monto(empleado.get('porcentaje_promocion')),
                'promotor_id': empleado.get('promotor_id'),
                'porcentaje_extra': self.get_monto(empleado.get('porcentaje_extra')),
                'total_a_pagar': total_a_pagar,
                'monto_pagado': '',
                'saldo_a_pagar': '',
            }))

        return mano_de_obra_liquidaciones

    def get_monto(self, porcentaje):
        return (porcentaje or 0) * self.precio / 100

    def validar_porcentajes(self, campo, porcentaje_maximo, suma_porcentajes):
        if suma_porcentajes > porcentaje_maximo:
            mess = "La suma de los porcentajes del campo {} es mayor al porcentaje máximo ({})".format(campo, porcentaje_maximo)
            raise exceptions.ValidationError(mess)
        print('El porcentaje maximo para esto es: ', porcentaje_maximo)

    def get_mano_de_obra_display(self):
        """Genera un string con los nombres de los operadores que participaron
        en el trabajo.
        Sirve para mostrarlos en vista tree y poder buscar por ese campo
        """
        operadores = ''
        for mo_utilizada in self.mano_de_obra_utilizada_ids:
            operadores += '{}/'.format(mo_utilizada.user_id.name)
        return operadores

    def get_tipo_de_trabajo_display(self):
        """Genera un string con los nombres de los tipos_de_trabajo de la orden.
        Sirve para mostrarlos en vista tree como string.
        """
        tipos = ''
        for tipo in self.tipos_de_trabajo_ids:
            tipos += u'{}/'.format(tipo.name)
        return tipos

    @api.multi
    def actualizar_partner_email(self, partner_id, email):
        partner = self.env['res.partner'].search([('id', '=', partner_id)])
        partner.write({'email': email})

    @api.multi
    def actualizar_partner_cuit(self, partner_id, cuit):
        partner = self.env['res.partner'].search([('id', '=', partner_id)])
        partner.write({'cuit': cuit})

    @api.multi
    def set_certificado(self):
        certificados_anteriores = self.env['ofreser.certificado'].search([('orden_de_trabajo_id', '=', self.id)])
        if certificados_anteriores:
            for cert in certificados_anteriores:
                cert.orden_de_trabajo_id = None

        self.certificado_id.orden_de_trabajo_id = self.id


class OfreserPorcentajeMaximo(models.Model):
    _name = 'ofreser.porcentaje_maximo'
    _description = 'Porcentaje Maximo'

    item_id = fields.Many2one(
        comodel_name='ofreser.porcentaje_maximo_item',
        string='Objeto'
    )
    porcentaje_maximo = fields.Float(string='Porcentaje Máximo')


class OfreserPorcentajeMaximoItem(models.Model):
    _name = 'ofreser.porcentaje_maximo_item'
    _description = 'Porcentaje Maximo de Item'

    name = fields.Char(string='Nombre')
