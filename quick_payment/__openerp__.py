# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2011-TODAY Akretion (http://www.akretion.com).
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

{
    'name': 'Quick Payment',
    'version': '0.2',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
Quick Payment
==================

Quick Payment is an abstract module that gives the possibility to pay
a record (sale order, invoice,...)  from the record itself.
You need to install the module sale_quick_payment, purchase_quick_payment, 
if you want to pay a sale order, a purchase order. 

The payment will be linked to the record.

This module was originally designed for the e-commerce sector, but it
does not preclude to use it in other sectors.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'payment_method',
    ],
    'data': [
        'wizard/register_payment_view.xml',
    ],
    'demo': [],
    'installable': True,
}
