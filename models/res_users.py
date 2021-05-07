# -*- coding: utf-8 -*-
import os.path
from odoo import models, fields, api


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    #@api.multi
    def action_get_attachment_tree_view(self):
        # model, action_id = self.env['ir.model.data'].get_object_reference('base', 'action_attachment')
        # print('model',model,'action_id',action_id)
        # action = self.env[model].browse(action_id)
        # print('ACCION:',action)
        # action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        # action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', ids)])
        print('ACCION id:', self)
        return {'type': 'ir.actions.act_window',
                'name': 'Archivos Adjuntos',
                'res_model': 'ir.attachment',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('res_model', '=', 'res.users'),
                           ('res_id', '=', self.id)],
                'context': {'default_res_model': 'res.users',
                            'default_res_id': self.id}
                }

    #@api.one
    def _get_attachment_number(self):
        print('self', self)
        print('self', self.ids)
        res = dict.fromkeys(self.ids, 0)
        for app_id in self.ids:
            res[app_id] = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'res.users'), ('res_id', '=', app_id)]
            )
            self.archivos_adjuntos = res[app_id]
        return res

    archivos_adjuntos = fields.Integer(compute=_get_attachment_number, string='Archivos Adjuntos')
    archivos_ids = fields.Many2many('ir.attachment', 'arch_usu_rel', 'usuario_id', 'archivo_id', 'Archivos compartidos')


class Ir_Attachment(models.Model):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    extension = fields.Char('Extension', compute='_get_extension')
    usuarios_ids = fields.Many2many('res.users', 'arch_usu_rel', 'archivo_id', 'usuario_id', 'Usuarios')

    def _get_extension(self):
        if os.path.splitext(self.datas_fname)[1] == '' or os.path.splitext(self.datas_fname)[1] is None:
            self.extension = 'ninguna'
        else:
            self.extension = os.path.splitext(self.datas_fname)[1]
