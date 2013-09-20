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


class record2pay(orm.AbstractModel):
    _name = 'record2pay'
    _date_key = None
    _movekey2record = None

    def _get_amount(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            #TODO add support when payment is linked to many record
            paid_amount = 0
            for line in record.payment_ids:    
                paid_amount += line.credit - line.debit
            res[record.id] = {
                    'amount_paid': paid_amount, 
                    'residual': record.amount_total - paid_amount,
                    }
        return res

    def _payment_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cursor, user, ids, context=context):
            res[record.id] = bool(record.payment_ids)
        return res

    _columns = {
        'payment_ids': fields.many2many('account.move.line',
                                        string='Payments Entries'),
        'payment_method_id': fields.many2one('payment.method',
                                             'Payment Method',
                                             ondelete='restrict'),
        'residual': fields.function(
            _get_amount,
            digits_compute=dp.get_precision('Account'),
            string='Balance',
            store=False,
            multi='payment'),
        'amount_paid': fields.function(
            _get_amount,
            digits_compute=dp.get_precision('Account'),
            string='Amount Paid',
            store=False,
            multi='payment'),
        'payment_exists': fields.function(
            _payment_exists,
            string='Has automatic payment',
            type='boolean',
            help="It indicates that record has at least one payment."),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['payment_ids'] = False
        return super(record2pay, self).copy(cr, uid, id,
                                            default, context=context)

    def add_payment(self, cr, uid, ids, journal_id, amount,
                    date=None, description=None, context=None):
        """ Generate payment move lines of a certain amount linked
        with the record. """
        if isinstance(ids, Iterable):
            assert len(ids) == 1, "one record at a time can be paid"
            ids = ids[0]
        journal_obj = self.pool.get('account.journal')

        record = self.browse(cr, uid, ids, context=context)
        if date is None and self._date_key:
            date = record[self._date_key]
        journal = journal_obj.browse(cr, uid, journal_id, context=context)
        self._add_payment(cr, uid, record, journal, amount, date, description, context=context)
        return True

    def _add_payment(self, cr, uid, record, journal, amount, date, description, context=None):
        """ Generate move lines entries to pay the record. """
        move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        period_id = period_obj.find(cr, uid, dt=date, context=context)[0]
        period = period_obj.browse(cr, uid, period_id, context=context)
        move_name = description or self._get_payment_move_name(cr, uid, journal,
                                                period, context=context)
        move_vals = self._prepare_payment_move(cr, uid, move_name, record,
                                               journal, period, date,
                                               context=context)
        move_lines = self._prepare_payment_move_line(cr, uid, move_name, record,
                                                     journal, period, amount,
                                                     date, context=context)

        move_vals['line_id'] = [(0, 0, line) for line in move_lines]
        move_obj.create(cr, uid, move_vals, context=context)

    def _get_payment_move_name(self, cr, uid, journal, period, context=None):
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        sequence = journal.sequence_id

        if not sequence:
            raise osv.except_osv(
                _('Configuration Error'),
                _('Please define a sequence on the journal %s.') %
                journal.name)
        if not sequence.active:
            raise osv.except_osv(
                _('Configuration Error'),
                _('Please activate the sequence of the journal %s.') %
                journal.name)

        ctx = context.copy()
        ctx['fiscalyear_id'] = period.fiscalyear_id.id
        name = seq_obj.next_by_id(cr, uid, sequence.id, context=ctx)
        return name

    def _prepare_payment_move(self, cr, uid, move_name, record, journal,
                              period, date, context=None):
        return {'name': move_name,
                'journal_id': journal.id,
                'date': date,
                'ref': record.name,
                'period_id': period.id,
                }

    def _prepare_payment_move_line(self, cr, uid, move_name, record, journal,
                                   period, amount, date, context=None):
        """ """
        partner_obj = self.pool.get('res.partner')
        currency_obj = self.pool.get('res.currency')
        partner = partner_obj._find_accounting_partner(record.partner_id)

        company = journal.company_id

        currency_id = False
        amount_currency = 0.0
        if journal.currency and journal.currency.id != company.currency_id.id:
            currency_id = journal.currency.id
            amount_currency, amount = (amount,
                                       currency_obj.compute(cr, uid,
                                                            currency_id,
                                                            company.currency_id.id,
                                                            amount,
                                                            context=context))

        # payment line (bank / cash)
        debit_line = {
            'name': move_name,
            'debit': amount,
            'credit': 0.0,
            'account_id': journal.default_credit_account_id.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': amount_currency,
            'currency_id': currency_id,
        }

        # payment line (receivable)
        credit_line = {
            'name': move_name,
            'debit': 0.0,
            'credit': amount,
            'account_id': partner.property_account_receivable.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': -amount_currency,
            'currency_id': currency_id,
            self._movekey2record: [(4, record.id)],
        }
        return debit_line, credit_line

    def onchange_payment_method_id(self, cr, uid, ids, payment_method_id, context=None):
        if not payment_method_id:
            return {}
        result = {}
        method_obj = self.pool.get('payment.method')
        method = method_obj.browse(cr, uid, payment_method_id, context=context)
        if method.payment_term_id:
            result['payment_term'] = method.payment_term_id.id
        return {'value': result}

    def action_view_payments(self, cr, uid, ids, context=None):
        """ Return an action to display the payment linked
        with the record """

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        payment_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            payment_ids += [move.id for move in so.payment_ids]

        ref = mod_obj.get_object_reference(cr, uid, 'account',
                                           'action_move_journal_line')
        action_id = False
        if ref:
            __, action_id = ref
        action = act_obj.read(cr, uid, [action_id], context=context)[0]

        # choose the view_mode accordingly
        if len(payment_ids) > 1:
            action['domain'] = str([('id', 'in', payment_ids)])
        else:
            ref = mod_obj.get_object_reference(cr, uid, 'account',
                                               'view_move_form')
            action['views'] = [(ref[1] if ref else False, 'form')]
            action['res_id'] = payment_ids[0] if payment_ids else False
        return action

    def action_cancel(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.payment_ids:
                raise osv.except_osv(
                    _('Cannot cancel this record!'),
                    _('Automatic payment entries are linked '
                      'with the record.'))
        return super(record2pay, self).action_cancel(cr, uid, ids, context=context)
