# -*- coding: utf-8 -*-
# instala unidecode!!!
import unidecode
import datetime as dt
import json
from datetime import datetime
from openerp import http
from openerp.http import request

import base64
# esto no me esta importando posta
from cStringIO import StringIO
from werkzeug.utils import redirect


class website_archivos(http.Controller):
    @http.route(['/page/archivos/',
                 '/page/archivos/<string:vista>'], type='http', auth="user", website=True, csrf=False)
    def archivos(self, vista=None, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        adjunto_orm = request.env['ir.attachment']
        print('adjunto_orm :', adjunto_orm)
        ####################
        adjuntos_ids = adjunto_orm.search([('res_model', '=', 'res.users'), ('res_id', '=', uid)])
        adjuntos_usuario = adjunto_orm.browse(adjuntos_ids.ids)
        ####################
        usuario = request.env['res.users'].browse(uid)
        adjuntos_ids = adjunto_orm.search([('id', 'in', usuario.archivos_ids.ids)])
        #        ides=adjuntos_ids.ids
        adjuntos_privados = adjunto_orm.browse(adjuntos_ids.ids)
        ####################
        adjuntos_ids = adjunto_orm.search([('usuarios_ids', '=', False), ('res_model', '=', 'res.users'), ('res_id', '!=', uid)])
        #        ides.extend(adjuntos_ids.ids)
        adjuntos_publicos = adjunto_orm.browse(adjuntos_ids.ids)
        ####################
        valores = {'adjuntos_publicos': adjuntos_publicos,
                   'adjuntos_personales': adjuntos_usuario,
                   'adjuntos_privados': adjuntos_privados
                   }
        print('valores:', valores)
        if vista is None:
            vista = 'lista'
        values = {'error': {},
                  'usuario': usuario,
                  'valores': valores,
                  'vista': vista
                  }
        return request.render("devoo_ofreser.archivos_page", values)

    @http.route(['/attachment/download'], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "file_type", "res_model", "res_id", "type", "url", "mimetype"]
        )
        print('attachment', attachment)
        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/page/archivos')

        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            codificacion = unidecode.unidecode(attachment["datas"])
            data = StringIO(base64.standard_b64decode(codificacion))
            return http.send_file(data, filename=attachment['name'], as_attachment=True, mimetype=attachment['mimetype'])
        else:
            return request.not_found()

    @http.route(['/attachment/subir'], type='http', auth="user", website=True, csrf=False)
    def subir(self, **post):
        print('post:', post)
        values = post['ufile']
        print('val:', values)
        print('val read:', values.filename)
        if values:
            adjunto_orm = request.env['ir.attachment']
            usuario_orm = request.env['res.users'].browse(request.uid)
            adjunto_orm.create({'name': unidecode.unidecode(values.filename),
                                'res_model': 'res.users',
                                'res_id': request.uid,
                                'description': 'Archivo subido por el usuario',
                                'datas': base64.encodestring(values.read()),
                                'res_name': usuario_orm.partner_id.name,
                                'datas_fname': unidecode.unidecode(values.filename)
                                })
            print('creadooo')
            return request.redirect("/page/archivos")


class OrdenDeTrabajoTablero(http.Controller):
    @http.route(['/odttablero'], type="http", auth="user", website=True)
    def orden_de_trabajo_tablero(self, data={}, **post):
        """Devuelve las ordenes de trabajo

        Ordenadas por fecha y hora; y según correspondan al usuario a menos que sea administrador
        """
        # planes = http.request.env['saas_portal.plan'].sudo().search([])
        # base_url = http.request.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')]).value
        ordenes_model = request.env['ofreser.orden_de_trabajo']
        estado = post.get('estado')

        if estado == 'en_espera':
            ordenes = ordenes_model.search([('estado', '=', 'en_espera')])
        elif estado == 'en_proceso':
            ordenes = ordenes_model.search([('estado', '=', 'en_proceso')])
        elif estado == 'reprogramar':
            ordenes = ordenes_model.search([('estado', '=', 'reprogramar')])
        elif estado == 'finalizado':
            ordenes = ordenes_model.search([('estado', '=', 'finalizado')])
        elif estado == 'cancelado':
            ordenes = ordenes_model.search([('estado', '=', 'cancelado')])
        else:
            ordenes = ordenes_model.search([('estado', '=', 'en_espera')])
            estado = 'en_espera'

        if not request.env.user.has_group('devoo_ofreser.grupo_administracion_ordenes'):
            print('-----------------------------------------------------------------------')
            print('Grupo operador')
            print('-----------------------------------------------------------------------')
            # import pdb; pdb.set_trace()
            # ordenes = ordenes_model.search([])
            ordenes = ordenes.filtered(lambda r: request.env.user.id in [mo.user_id.user_id.id for mo in r.mano_de_obra_utilizada_ids])
        ordenes = ordenes.sorted(key=lambda r: r.fecha_servicio)
        values = {'ordenes': ordenes, 'estado': estado}
        return http.request.render('devoo_ofreser.orden_de_trabajo_tablero', values)

    @http.route(['/odttablero/busqueda'], type="http", auth="user", website=True, csrf=False)
    def orden_de_trabajo_tablero_busqueda(self, data={}, **post):
        """Devuelve las ordenes de trabajo que coincidan con el nombre de un cliente

        Ordenadas por fecha y hora; y según correspondan al usuario a menos que sea administrador
        """
        ordenes = request.env['ofreser.orden_de_trabajo'].search([('partner_id.name', 'ilike', post.get('texto'))])

        # filtra por usuario a menos que sea administrador
        if not request.env.user.has_group('devoo_ofreser.grupo_administracion_ordenes'):
            ordenes = ordenes.filtered(lambda r: request.env.user.id in [mo.user_id.user_id.id for mo in r.mano_de_obra_utilizada_ids])
        # ordena las ordenes por fecha
        ordenes = ordenes.sorted(key=lambda r: r.fecha_servicio)

        values = {'ordenes': ordenes}

        return http.request.render('devoo_ofreser.orden_de_trabajo_tablero', values)

    @http.route(['/odttablero/filtro_fecha'], type="http", auth="user", website=True, csrf=False)
    def orden_de_trabajo_tablero_filtro_fecha(self, data={}, **post):
        """Devuelve las ordenes de trabajo de una determinada fecha

        Ordenadas por fecha y hora; y según correspondan al usuario a menos que sea administrador
        """

        fecha = post.get('fecha_tablero')
        if fecha:
            fecha_ini = datetime.strptime(fecha, '%d/%m/%Y') + dt.timedelta(hours=3)
            fecha_fin = fecha_ini + dt.timedelta(hours=24)
            fecha_ini = fecha_ini.strftime('%Y-%m-%d %H:%M:%S')
            fecha_fin = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            ordenes = request.env['ofreser.orden_de_trabajo'].search([('fecha_servicio', '>', fecha_ini), ('fecha_servicio', '<', fecha_fin)])
            ordenes = ordenes.sorted(key=lambda r: r.fecha_servicio)
        else:
            ordenes = request.env['ofreser.orden_de_trabajo'].search([])

        # filtra por usuario a menos que sea administrador
        if not request.env.user.has_group('devoo_ofreser.grupo_administracion_ordenes'):
            ordenes = ordenes.filtered(lambda r: request.env.user.id in [mo.user_id.user_id.id for mo in r.mano_de_obra_utilizada_ids])
        # ordena las ordenes por fecha
        ordenes = ordenes.sorted(key=lambda r: r.fecha_servicio)
        values = {'ordenes': ordenes, 'fecha_filtro': fecha}
        return http.request.render('devoo_ofreser.orden_de_trabajo_tablero', values)


class OrdenDeTrabajoIndividual(http.Controller):
    @http.route(['/odtindividual/<int:orden_id>'], type="http", auth="user", website=True)
    def orden_de_trabajo_individual(self, data={}, **post):
        print('------------------------------------------------')
        print('post: %s' % post)
        orden = request.env['ofreser.orden_de_trabajo'].browse(post.get('orden_id'))
        rubros = request.env['ofreser.rubro'].search([]).sorted(key=lambda r: r.name)
        categoria_productos_usables = request.env.ref('devoo_ofreser.productos_categoria_usables')
        productos_usables = request.env['product.template'].search([('categ_id', '=', categoria_productos_usables.id)])
        tipos_de_trabajos = request.env['ofreser.tipo_de_trabajo'].search([])
        moviles = request.env['fleet.vehicle'].search([])
        maquinas = request.env['ofreser.maquina'].search([])
        empleados = request.env['hr.employee'].search([])
        values = {'orden': orden,
                  'rubros': rubros,
                  'empleados': empleados,
                  'productos_usables': productos_usables,
                  'tipos_de_trabajos': tipos_de_trabajos,
                  'moviles': moviles,
                  'maquinas': maquinas,
                  'pagado': True if post.get('pagado') else False
                  }
        return http.request.render('devoo_ofreser.orden_de_trabajo_individual', values)

    @http.route(['/odtindividual/<int:orden_id>/guardar'], type='http', auth="user", website=True, csrf=False)
    def guardar(self, **post):
        self.guardar_orden(redireccion='/odtablero', **post)
        return json.dumps({'status':200})
        return request.redirect("/odttablero/")

    def get_records_a_borrar(self, orden, lista_ids, campo):
        vals = []
        records = getattr(orden, campo)
        # print('records: {}'.format(records))
        # import pdb; pdb.set_trace()
        for record in records:
            if record.id not in lista_ids:
                vals.append((2, record.id))
        # print('cosas a borrar')
        # print('campo: {campo}, ids: {ids}'.format(campo=campo, ids=vals))
        return vals

    def get_values_for_lists(self, items, relacion_campo):
        vals = {}
        for key_field, val_field in items.items():
            field_name = key_field.split('--')[0]
            if relacion_campo[field_name][1] == 'int':
                final_val = int(val_field) if val_field else ''
            elif relacion_campo[field_name][1] == 'float':
                final_val = float(val_field) if val_field else ''

            vals[relacion_campo[field_name][0]] = final_val
        return vals

    @http.route(['/odtindividual/<int:orden_id>/iniciar'], type='http', auth="user", website=True, csrf=False)
    def iniciar(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        orden.iniciar_orden_de_trabajo()
        return request.redirect("/odtindividual/%s" % orden_id)

    @http.route(['/odtindividual/<int:orden_id>/reprogramar'], type='http', auth="user", website=True, csrf=False)
    def reprogramar(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        orden.reprogramar_orden_de_trabajo()
        return request.redirect("/odttablero")

    @http.route(['/odtindividual/<int:orden_id>/a_espera'], type='http', auth="user", website=True, csrf=False)
    def a_espera(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        orden.a_espera_orden_de_trabajo()
        return request.redirect("/odttablero")

    @http.route(['/odtindividual/<int:orden_id>/cancelar'], type='http', auth="user", website=True, csrf=False)
    def cancelar(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        orden.cancelar_orden_de_trabajo()
        return request.redirect("/odttablero")

    @http.route(['/odtindividual/<int:orden_id>/guardar/finalizar'], type='http', auth="user", website=True, csrf=False)
    def finalizar(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        orden.finalizar_orden_de_trabajo()

        print('-------------------------------------------------------------------------------------------------------------')
        print('-------------------------------------------------------------------------------------------------------------')
        print('------------------------------------------------------TOY ACA------------------------------------------------')
        print('-------------------------------------------------------------------------------------------------------------')
        print('-------------------------------------------------------------------------------------------------------------')
        self.guardar_orden(redireccion='/odtablero', **post)
        return json.dumps({'status':200})
        return request.redirect("/odttablero/")

    @http.route(['/buscarelemento'], type='http', auth="user", csrf=False)
    def buscar_elemento(self, **post):
        print('-----------------------------------------------')
        print('ENTRA AL SEARCH')
        print('post: %s' % post)
        input = post.get('input')
        model_input = post.get('tipo')
        responsable = False
        uom = False
        if model_input == 'mano_obra_utilizada' or model_input == 'promotor':
            model = 'hr.employee'
            field = 'name'
        elif model_input == 'tipo_trabajo':
            model = 'ofreser.tipo_de_trabajo'
            field = 'name'
        elif model_input == 'producto_consumido':
            model = 'product.template'
            field = 'name'
            uom = 'uom_id'
        elif model_input == 'maquina_utilizada':
            model = 'ofreser.maquina'
            field = 'name'
            responsable = 'responsable_id'
        elif model_input == 'movilidad_utilizada':
            model = 'fleet.vehicle'
            field = 'license_plate'
            responsable = 'conductor_id'
        elif model_input == 'extra':
            model = 'hr.employee'
            field = 'name'
        elif model_input == 'rubro':
            model = 'ofreser.rubro'
            field = 'name'
        elementos = request.env[model].search([(field, 'ilike', input)])
        print('elementos encontrados: %s' % elementos)
        res = {}
        if responsable:
            print('devuelve responsable')
            res['elementos'] = [(el.id, el.name, getattr(el, responsable).name) for el in elementos]
        elif uom:
            print('devuelve uom')
            res['elementos'] = [(el.id, el.name, getattr(el, uom).name) for el in elementos]
        else:
            res['elementos'] = [(el.id, el.name) for el in elementos]
        return json.dumps(res)

    @http.route(['/buscarresponsable'], type='http', auth="user", csrf=False)
    def buscar_responsable(self, **post):
        print('-----------------------------------------------')
        print('ENTRA AL SEARCH')
        print('post: %s' % post)
        record_id = int(post.get('id'))
        model_input = post.get('tipo')
        if model_input == 'maquina_utilizada':
            model = 'ofreser.maquina'
            field = 'responsable_id'
        elif model_input == 'movilidad_utilizada':
            model = 'fleet.vehicle'
            field = 'conductor_id'

        record = request.env[model].search([('id', '=', record_id)])
        responsable_name = getattr(record, field).name
        # elementos = request.env[model].search([(field, '=', record_id)])
        print('elementos encontrados: %s' % responsable_name)
        res = {}
        res['elementos'] = [responsable_name]
        return json.dumps(res)

    @http.route(['/buscaruom'], type='http', auth="user", csrf=False)
    def buscar_uom(self, **post):
        print('-----------------------------------------------')
        print('ENTRA AL SEARCH')
        print('post: %s' % post)
        record_id = int(post.get('id'))
        model = 'product.template'

        record = request.env[model].search([('id', '=', record_id)])
        product_uom = record.uom_id.name
        # elementos = request.env[model].search([(field, '=', record_id)])
        print('elementos encontrados: %s' % product_uom)
        res = {}
        res['elementos'] = [product_uom]
        return json.dumps(res)

    # Devuelve la fecha en formato de Odoo y en hora de GMT
    def convertir_formato_fecha(self, fecha):
        server_format = '%Y-%m-%d %H:%M:%S'
        input_format = '%d/%m/%Y %H:%M'
        dt_local = datetime.strptime(fecha, input_format)
        dt_utc = dt_local + dt.timedelta(hours=3)
        return dt_utc.strftime(server_format)

    @http.route(['/get_porcentaje_maximo/<int:orden_id>'], type='http', auth="user", csrf=False)
    def get_porcentaje_maximo_mo(self, **post):
        orden_id = post.get('orden_id')
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)
        porcentaje_maximo_mano_obra = min([tipo.porcentaje_maximo_mano_obra for tipo in orden.tipos_de_trabajo_ids])
        res = {'porcentaje_maximo': porcentaje_maximo_mano_obra}
        return json.dumps(res)

    def guardar_orden(self, redireccion, **post):
        orden_id = post.get('orden_id')
        print('----------------------GUARDAR ID: %s--------------------------' % orden_id)
        print('post: %s' % post)
        orden = request.env['ofreser.orden_de_trabajo'].browse(orden_id)

        campos = ['mano_obra_utilizada',
                  'tipo_trabajo',
                  'producto_consumido',
                  'maquina_utilizada',
                  'movilidad_utilizada',
                  'extra',
                  'promotor']
        relacion_campo = {
            'mano_obra_utilizada_item': ['user_id', 'int'],
            'cantidad_mano_obra_utilizada': ['porcentaje', 'float'],
            'tipo_trabajo_item': ['tipo_de_trabajos_ids', 'int'],
            'producto_consumido_item': ['product_id', 'int'],
            'cantidad_producto_consumido': ['cantidad', 'float'],
            'maquina_utilizada_item': ['maquina_id', 'int'],
            'cantidad_maquina_utilizada': ['porcentaje', 'float'],
            'movilidad_utilizada_item': ['movilidad_id', 'int'],
            'cantidad_movilidad_utilizada': ['porcentaje', 'float'],
            'extra_item': ['user_id', 'int'],
            'cantidad_extra': ['porcentaje', 'float'],
            'promotor_item': ['promotor_id', 'int'],
            'cantidad_promotor': ['porcentaje', 'float'],
        }
        relacion_campo_borrar = {
            'mano_obra_utilizada': 'mano_de_obra_utilizada_ids',
            'tipo_trabajo': 'tipos_de_trabajo_ids',
            'producto_consumido': 'productos_consumidos_ids',
            'maquina_utilizada': 'maquinas_utilizadas_ids',
            'movilidad_utilizada': 'movilidad_utilizadas_ids',
            'extra': 'porcentajes_extra_ids',
            'promotor': 'promotores_ids',
        }
        listas = {
            'mano_obra_utilizada': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'tipo_trabajo': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'producto_consumido': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'maquina_utilizada': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'movilidad_utilizada': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'extra': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            },
            'promotor': {
                'ids': [],
                'a_modificar': [],
                'nuevas': [],
                'a_borrar': [],
                'completa': []
            }
        }
        post_ordenado = {}
        for campo in campos:
            for campo in campos:
                post_ordenado[campo] = {}

        for key, item in post.items():
            for campo in campos:
                if campo in key:
                    key_id = key.split('--')[1]
                    if key_id in post_ordenado[campo]:
                        post_ordenado[campo][key_id][key] = item
                    else:
                        post_ordenado[campo][key_id] = {}
                        post_ordenado[campo][key_id][key] = item
        # import pdb; pdb.set_trace()
        for campo in post_ordenado:
            for key, val in post_ordenado[campo].items():
                if 'nuevo' not in key:
                    vals = self.get_values_for_lists(val, relacion_campo)
                    listas[campo]['a_modificar'].append((1, int(key), vals))
                    listas[campo]['ids'].append(int(key))
                else:
                    vals = self.get_values_for_lists(val, relacion_campo)
                    listas[campo]['nuevas'].append((0, 0, vals))

                # print('campo: {campo}, campo relacionado: {relacion}'.format(campo=campo, relacion=relacion_campo_borrar[campo]))
                listas[campo]['a_borrar'] = self.get_records_a_borrar(orden, listas[campo]['ids'], relacion_campo_borrar[campo])
                # print('listas de borrado: {}'.format(listas[campo]['a_borrar']))
                # listas[campo]['a_borrar'] = []
            listas[campo]['completa'] = listas[campo]['nuevas'] + listas[campo]['a_modificar'] + listas[campo]['a_borrar']
        print('----------------------------------------------------------------')
        # print('listas: {}'.format(listas['promotor']))
        print('---------------LISTAS TRABAJO----------------------')
        print(listas['tipo_trabajo'])
        tipos_ids = [tipo_id[2]['tipo_de_trabajos_ids'] for tipo_id in listas['tipo_trabajo']['completa'] if tipo_id[0] != 2]
        # Handle Rubros
        rubro_name = post.get('rubro_name')
        rubro_id = post.get('rubro_id')
        if not rubro_id and rubro_name:
            rubro = request.env['ofreser.rubro'].create({'name': rubro_name})
            rubro_id = rubro.id
        superficie_total_inmueble = int(post.get('superficie_total_inmueble')) if post.get('superficie_total_inmueble') else 0
        superficie_total_tratada = int(post.get('superficie_total_tratada')) if post.get('superficie_total_tratada') else 0
        vals = {'fecha_servicio': self.convertir_formato_fecha(post.get('fecha_servicio')) if post.get('fecha_servicio') else None,
                'fecha_vencimiento': self.convertir_formato_fecha(post.get('fecha_vencimiento')) if post.get('fecha_vencimiento') else None,
                'numero_certificado': post.get('numero_certificado'),
                'certificado_id': self.get_certificado_id(post.get('numero_certificado')),
                'email': post.get('email'),
                'cuit': post.get('cuit'),
                'domicilio': post.get('domicilio'),
                'telefono': post.get('telefono'),
                'movil': post.get('movil'),
                # 'rubro_id': post.get('rubro'),
                'rubro_id': rubro_id,
                'precio': post.get('precio'),
                'factura': post.get('factura'),
                'pagado': 'si' if post.get('pagado') == 'True' else 'no',
                'superficie_total_inmueble': superficie_total_inmueble,
                'superficie_total_tratada': superficie_total_tratada,
                'mano_de_obra_utilizada_ids': listas['mano_obra_utilizada']['completa'],
                'productos_consumidos_ids': listas['producto_consumido']['completa'],
                'tipos_de_trabajo_ids': [(6, 0, list(set(tipos_ids)))],
                'movilidad_utilizadas_ids': listas['movilidad_utilizada']['completa'],
                'maquinas_utilizadas_ids': listas['maquina_utilizada']['completa'],
                'porcentajes_extra_ids': listas['extra']['completa'],
                'promotores_ids': listas['promotor']['completa'],
                'observaciones': post.get('observaciones'),
                }
        print('------------------------------------------------------------')
        # print('vals: {vals}'.format(vals=vals))
        for key, val in vals.items():
            print(key, val)
            print('------------------------------------------------------------')
        firma = post.get('firma_archivo')
        if firma:
            vals['firma_archivo'] = base64.encodestring(firma.read())
            vals['firma_archivo_nombre'] = unidecode.unidecode(firma.filename)

        # TODO: uncomment line after finished
        # if finalizar:
        #     print('---------------------------------')
        #     print('------------FINALIZAR------------')
        #     print('---------------------------------')
        orden.write(vals)
        return request.redirect(redireccion)

    def get_certificado_id(self, numero_certificado):
        certificado = request.env['ofreser.certificado'].search([('numero', '=', numero_certificado)])
        if not certificado:
            certificado = request.env['ofreser.certificado'].create({'numero': numero_certificado})
        return certificado.id
