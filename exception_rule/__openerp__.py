# -*- coding: utf-8 -*-
###############################################################################
#
#   exception_rule for OpenERP 
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
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
    'name': 'Exceptions Rule',
    'version': '0.1',
    'category': 'Generic Modules/Sale',
    'description': """
Abstract module that add the concept of exception, exception can be use in different model
like the sale order or the purchase order. The aim is to add some check before validating the object
""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'base'
    ],
    'init_xml': [
                ],
    'update_xml': [
        'exception_view.xml',
        'wizard/exception_confirm_view.xml',
        'security/ir.model.access.csv',
        ],
    'demo_xml': [],
    'installable': True,
}
