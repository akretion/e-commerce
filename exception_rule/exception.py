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

import time
import netsvc

from openerp.osv import orm, fields
from openerp.osv.osv import except_osv
from tools.safe_eval import safe_eval as eval
from tools.translate import _
from openerp.tools.config import config

from contextlib import contextmanager
import logging

_logger = logging.getLogger(__name__)

@contextmanager 
def commit(cr): 
    """ 
    Commit the cursor after the ``yield``, or rollback it if an 
    exception occurs. 
 
    Warning: using this method, the exceptions are logged then discarded. 
    """ 
    try: 
        yield 
    except Exception: 
        cr.rollback() 
        _logger.exception('Error during an automatic workflow action.')
    else:
        cr.commit()



class exception_rule(orm.Model):
    _name = "exception.rule"
    _description = "Exceptions Rule"
    _order="active desc, sequence asc"

    def get_available_model(self, cr, uid, context=None):
        return []
    
    def _get_available_model(self, cr, uid, context=None):
        return self.get_available_model(cr, uid, context=context)

    _columns = {
        'name': fields.char('Exception Name', size=64, required=True, translate=True),
        'description': fields.text('Description', translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when applying the test"),
        'model': fields.selection(_get_available_model,
                                  string='Apply on',
                                  required=True),
        'active': fields.boolean('Active'),
        'code': fields.text('Python Code',
                    help="Python code executed to check if the exception apply or not. " \
                         "The code must apply block = True to apply the exception."),
        'send_email': fields.boolean(
            'Notify exception by Email',
            help=("If true, a notification will be send "
                  "by email at the creation of the exception")),
        'email_description': fields.text(
            'Email Description',
            help=("If you want to customize a specific message for this"
                  "exception, you can adapt the email template"
                  "to display this html description")),
    }

    _defaults = {
        'code': """# Python code. Use failed = True to block the sale order.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - order or line: browse_record of the sale order or sale order line
#  - object: same as order or line, browse_record of the sale order or sale order line
#  - pool: ORM model pool (i.e. self.pool)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
"""
    }

class Record2Check(orm.AbstractModel):
    _name = "record2check"
    _description = "Record to Check"
    _line_key = None

    def get_main_error(self, cr, uid, ids, name, args, context=None):
        res = {}
        for current_object in self.browse(cr, uid, ids, context=context):
            if current_object.exceptions_ids:
                exceptions = [(exception.sequence, exception.id) for exception in current_object.exceptions_ids]
                exceptions.sort()
                res[current_object.id] = exceptions[0][1]
            else:
                res[current_object.id] = False
        return res

    _columns = {
        'exceptions_ids': fields.many2many('exception.rule',
                                           string='Exceptions'),
        'ignore_exceptions': fields.boolean('Ignore Exceptions'),
    }


    def test_all_draft_orders(self, cr, uid, context=None):
        ids = self.search(cr, uid, [
            ('state', '=', 'draft'),
            ('exceptions_ids', '!=', False),
            ('date_order', '>', '2014-09-01'),
            ])
        _logger.debug('Start Test Draft Order %s' % len(ids))
        for record_id in ids:     
            with commit(cr):   
                _logger.debug('Test Draft Order %s' % record_id)
                self.test_exceptions(cr, uid, [record_id])
        return True

    def _popup_exceptions(self, cr, uid, object_id, context=None):
        if context is None:
            context = {}
        model_data_obj = self.pool.get('ir.model.data')
        list_obj = self.pool.get('wizard.exception.confirm')
        ctx = context.copy()
        ctx.update({
            'active_id': object_id,
            'active_ids': [object_id],
            'active_model': self._name, 
        })
        list_id = list_obj.create(cr, uid, {}, context=ctx)
        view_id = model_data_obj.get_object_reference(
            cr, uid, 'exception_rule', 'view_wizard_exception_confirm')[1]
        action = {
            'name': _("Exceptions On %s"%self._description),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.exception.confirm',
            'view_id': [view_id],
            'target': 'new',
            'nodestroy': True,
            'res_id': list_id,
        }
        return action

    def test_exceptions(self, cr, uid, ids, context=None):
        """
        Condition method for the workflow from draft to confirm
        """
        exception_ids = self.detect_exceptions(cr, uid, ids, context=context)
        if exception_ids:
            return False
        return True

    def should_notify(self, cr, uid, record, exception_ids, context=None):
        exception_obj = self.pool['exception.rule']
        notify = any(exception.send_email for exception in
                     exception_obj.browse(cr, uid, exception_ids,
                     context=context))
        return notify and not record.exceptions_ids

    def detect_exceptions(self, cr, uid, ids, context=None):
        exception_obj = self.pool['exception.rule']
        email_obj = self.pool['email.template']
        model_data_obj = self.pool['ir.model.data']
        parent_exception_ids = exception_obj.search(cr, uid,
            [('model', '=', self._name)], context=context)
        line_exception_ids = exception_obj.search(cr, uid,
            [('model', '=', self._columns[self._line_key]._obj)], context=context)

        parent_exceptions = exception_obj.browse(cr, uid, parent_exception_ids, context=context)
        line_exceptions = exception_obj.browse(cr, uid, line_exception_ids, context=context)

        exception_ids = False
        for current_object in self.browse(cr, uid, ids):
            if current_object.ignore_exceptions:
                continue
            exception_ids = self._detect_exceptions(cr, uid, current_object,
                parent_exceptions, line_exceptions, context=context)
            should_notify = self.should_notify(cr, uid, current_object, exception_ids,
                                  context=context)
            self.write(cr, uid, [current_object.id], {'exceptions_ids': [(6, 0, exception_ids)]})
            if should_notify:
                model, email_tmpl_id = model_data_obj.get_object_reference(
                                            cr, uid, 'exception_rule',
                                            'email_template_sale_exceptions')
                email_obj.send_mail(cr, uid, email_tmpl_id,
                            current_object.id, force_send=False, context=context)
        return exception_ids

    def _exception_rule_eval_context(self, cr, uid, obj, context=None):
        if context is None:
            context = {}

        return {
                'self': self.pool.get(obj._name),
                'object': obj,
                'obj': obj,
                'pool': self.pool,
                'cr': cr,
                'uid': uid,
                'user': self.pool.get('res.users').browse(cr, uid, uid),
                'time': time,
                # copy context to prevent side-effects of eval
                'context': dict(context),}

    def _rule_eval(self, cr, uid, rule, obj, context):
        expr = rule.code
        space = self._exception_rule_eval_context(cr, uid, obj,
                                                  context=context)
        try:
            eval(expr, space,
                 mode='exec', nocopy=True) # nocopy allows to return 'result'
        except Exception, e:
            if config['debug_mode']: raise
            raise except_osv(_('Error'), _('Error when evaluating the sale exception rule :\n %s \n(%s)') %
                                 (rule.name, e))
        return space.get('failed', False)

    def _detect_exceptions(self, cr, uid, current_object, parent_exceptions, line_exceptions, context=None):
        if context is None:
            context = {}
        exception_obj = self.pool['exception.rule']
        email_obj = self.pool.get('email.template')
        exception_ids = []
        for rule in parent_exceptions:
            if self._rule_eval(cr, uid, rule, current_object, context):
                exception_ids.append(rule.id)

        for line in current_object[self._line_key]:
            for rule in line_exceptions:
                if rule.id in exception_ids:
                    continue  # we do not matter if the exception as already been
                    # found for an order line of this order
                if self._rule_eval(cr, uid, rule, line, context):
                    exception_ids.append(rule.id)
        return exception_ids

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'ignore_exceptions': False,
        })
        return super(Record2Check, self).copy(cr, uid, id, default=default, context=context)

    def remove_exception(self, cr, uid, ids, module, xml_id, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        __, exception_id = model_data_obj.get_object_reference(
                cr, uid, module, xml_id)
        for current_object in self.browse(cr, uid, ids, context=context):
            if current_object.state == 'draft':
                current_object.write({'exceptions_ids': [(3, exception_id)]})
        return True

