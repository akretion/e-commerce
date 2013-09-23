# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Sébastien Beau
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright 2013 Camptocamp SA (Guewen Baconnier)
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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
from collections import Iterable
import decimal_precision as dp


class sale_order(orm.Model):
    _inherit = ['sale.order', 'record2pay']
    _name = 'sale.order'
    _date_key = 'date_order'
    _movekey2record = 'sale_ids'
    _payment_term_key = 'payment_term'
    _invoice_type = 'out_invoice'

    def _payment_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = bool(record.payment_ids)
        return res

    _columns = {
        'payment_exists': fields.function(
            _payment_exists,
            string='Has automatic payment',
            type='boolean',
            help="It indicates that record has at least one payment."),
    }

    def automatic_payment(self, cr, uid, ids, amount=None, context=None):
        """ Create the payment entries to pay a sale order, respecting
        the payment terms.
        If no amount is defined, it will pay the residual amount of the sale
        order. """
        if isinstance(ids, Iterable):
            assert len(ids) == 1, "one sale order at a time can be paid"
            ids = ids[0]
        sale = self.browse(cr, uid, ids, context=context)
        method = sale.payment_method_id
        if not method:
            raise osv.except_osv(
                _('Configuration Error'),
                _("An automatic payment can not be created for the sale "
                  "order %s because it has no payment method.") % sale.name)

        if not method.journal_id:
            raise osv.except_osv(
                _('Configuration Error'),
                _("An automatic payment should be created for the sale order %s "
                  "but the payment method '%s' has no journal defined.") %
                (sale.name, method.name))

        journal = method.journal_id
        date = sale.date_order
        if amount is None:
            amount = sale.residual
        if sale.payment_term:
            term_obj = self.pool.get('account.payment.term')
            amounts = term_obj.compute(cr, uid, sale.payment_term.id,
                                       amount, date_ref=date,
                                       context=context)
        else:
            amounts = [(date, amount)]

        # reversed is cosmetic, compute returns terms in the 'wrong' order
        for date, amount in reversed(amounts):
            self._add_payment(cr, uid, sale, journal,
                              amount, date, context=context)
        return True

