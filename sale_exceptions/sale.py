# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Akretion LTDA.
#    Copyright (C) 2010-2013 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright (C) 2012 Camptocamp SA (Guewen Baconnier)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class exception_rule(orm.Model):
    _inherit = "exception.rule"

    def get_available_model(self, cr, uid, context=None):
        result = super(exception_rule, self).get_available_model(cr, uid, context=context)
        result += [
            ('sale.order', 'Sale Order'),
            ('sale.order.line', 'Sale Order Line'),
        ]
        return result
 
    _columns = {
        'sale_order_ids': fields.many2many('sale.order',
                                           string='Sale Orders', readonly=True),
    }


class sale_order(orm.Model):
    _inherit = ["sale.order", "record2check"]
    _name = "sale.order"
    _line_key = "order_line"

    _order = 'main_exception_id asc, date_order desc, name desc'

    def _get_main_error(self, cr, uid, ids, name, args, context=None):
        return self.get_main_error(cr, uid, ids, name, args, context=context)

    _columns = {
        'main_exception_id': fields.function(_get_main_error,
                        type='many2one',
                        relation="exception.rule",
                        string='Main Exception',
                        store={
                            'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['exceptions_ids', 'state'], 10),
                        }),
    } 

    def action_button_confirm(self, cr, uid, ids, context=None):
        exception_ids = self.detect_exceptions(cr, uid, ids, context=context)
        if exception_ids:
            return self._popup_exceptions(cr, uid, ids[0],  context=context)
        else:
            return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)



