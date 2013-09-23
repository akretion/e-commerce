# -*- coding: utf-8 -*-
###############################################################################
#
#   exception_rule for OpenERP 
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#   Copyright Camptocamp SA
#   @author: Guewen Baconnier
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import netsvc
from openerp.osv import fields, orm
    

class WizardExceptionConfirm(orm.TransientModel):
    _name = 'wizard.exception.confirm'

    def _links_get(self, cr, uid, context=None):
        """Gets links value for reference field"""
        obj = self.pool.get('res.request.link')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['object', 'name'], context)
        return [(r['object'], r['name']) for r in res]


    _columns = {
        'record': fields.reference('Record', selection=_links_get, size=128),
        'exception_ids': fields.many2many('exception.rule', string='Exceptions to resolve', readonly=True),
        'ignore': fields.boolean('Ignore Exceptions'),
    }

    def default_get(self, cr, uid, fields, context):
        res = super(WizardExceptionConfirm, self).default_get(cr, uid, fields, context=context)
        order_obj = self.pool.get(context['active_model'])
        record_id = context['active_id']
        record = order_obj.browse(cr, uid, record_id, context=context)
        exception_ids = [e.id for e in record.exceptions_ids]
        res.update({
            'exception_ids': [(6, 0, exception_ids)],
            'record': "%s,%s"%(context['active_model'], context['active_id']), 
            })
        return res

    def action_confirm(self, cr, uid, ids, context):
        form = self.browse(cr, uid, ids[0], context=context)
        if form.ignore:
            form.record.write({'ignore_exceptions': True})
        return {'type': 'ir.actions.act_window_close'}

