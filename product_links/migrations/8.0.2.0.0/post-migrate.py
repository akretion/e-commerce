# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def migrate(cr, version):
    """Update database from previous versions, after updating module."""
    cr.execute("""UPDATE product_link SET
        product_tmpl_id=main_product.product_tmpl_id,
        linked_product_tmpl_id=linked_product.product_tmpl_id
    FROM product_product AS main_product, product_product AS linked_product
    WHERE main_product.id = product_link.product_id
        AND linked_product.id = product_link.linked_product_id""")
