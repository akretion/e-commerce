# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
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

""" r0.2: Migration 8.0.1.0.1 => 8.0.1.0.2
    migrate the model from product.product to product.template
"""
__name__ = ("product.link:: V8 change the linked model product.product to "
            "product.template")


def migrate(cr, version):
    if version:
        cr.execute("ALTER TABLE product_link "
                   "RENAME COLUMN product_id TO old_product_id")
        cr.execute("ALTER TABLE product_link "
                   "RENAME COLUMN linked_product_id TO old_linked_product_id")
