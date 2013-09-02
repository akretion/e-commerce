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

    _columns = {
        #'sale_id': fields.many2one('sale.order', 'Sale'),
        'exception_ids': fields.many2many('exception.rule', string='Exceptions to resolve', readonly=True),
        'ignore': fields.boolean('Ignore Exceptions'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(WizardExceptionConfirm, self).default_get(cr, uid, fields, context=context)
        order_obj = self.pool.get('sale.order')
        sale_id = context.get('active_id', False)
        if sale_id:
            sale = order_obj.browse(cr, uid, sale_id, context=context)
            exception_ids = [e.id for e in sale.exceptions_ids]
            res.update({'exception_ids': [(6, 0, exception_ids)]})
        return res

    def action_confirm(self, cr, uid, ids, context):
        form = self.browse(cr, uid, ids[0], context=context)
        if form.ignore:
            self.pool.get(context['active_model']).write(cr, uid,
                    context['active_id'],
                    {'ignore_exceptions': True},
                    context=context)
        return {'type': 'ir.actions.act_window_close'}

