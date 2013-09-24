# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2011-2013 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.osv import orm, fields
import decimal_precision as dp


class register_payment(orm.TransientModel):
    _name = 'register.payment'
    _description = 'Wizard to register a payment'

    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'amount': fields.float('Amount',
                               digits_compute=dp.get_precision('Sale Price'),
                               required =True),
        'date': fields.datetime('Payment Date', required=True),
        'description': fields.char('Description', size=64),
    }

    def _get_journal_id(self, cr, uid, context):
        if context is None or not context.get('active_model'):
            return None
        model_obj = self.pool.get(context['active_model'])
        record = model_obj.browse(cr, uid, context['active_id'],
                                    context=context)
        if record and record.payment_method_id:
            return record.payment_method_id.journal_id.id
        return None

    def _get_amount(self, cr, uid, context):
        if context is None or not context.get('active_model'):
            return None
        model_obj = self.pool.get(context['active_model'])
        record = model_obj.browse(cr, uid, context['active_id'],
                                    context=context)
        if record and record.residual:
            return record.residual
        return 0

    _defaults = {
        'journal_id': _get_journal_id,
        'amount': _get_amount,
        'date': fields.datetime.now,
    }

    def register_payment(self, cr, uid, ids, context):
        """ Register a payment """
        wizard = self.browse(cr, uid, ids[0], context=context)
        model_obj = self.pool.get(context['active_model'])
        model_obj.add_payment(cr, uid,
                             context['active_id'],
                             wizard.journal_id.id,
                             wizard.amount,
                             wizard.date,
                             description=wizard.description,
                             context=context)
        return {'type': 'ir.actions.act_window_close'}

    def register_payment_and_confirm(self, cr, uid, ids, context):
        """ Register a payment and confirm the sale order, purchase order... """
        self.register_payment(cr, uid, ids, context)
        model_obj = self.pool.get(context['active_model'])
        return model_obj.action_button_confirm(cr, uid,
                                              [context['active_id']],
                                              context=context)
