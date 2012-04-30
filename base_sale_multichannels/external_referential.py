# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_sale_multichannels for OpenERP                                       #
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import osv, fields
#from base_external_referentials.external_osv import ExternalSesssion



class external_referential(osv.osv):
    _inherit = "external.referential"

    _columns = {
        'last_imported_product_id': fields.integer('Last Imported Product Id', help=("Product are imported one by one." 
                                                                "This is the magento id of the last product imported."
                                                                "If you clear it all product will be imported")),
        'last_imported_partner_id': fields.integer('Last Imported Partner Id', help=("Partners are imported one by one."
                                                                "This is the magento id of the last partner imported."
                                                                "If you clear it all partners will be imported")),
        'import_all_attributs': fields.boolean('Import all attributs', help=("If the option is uncheck only the attributs" 
                                                                        "that doesn't exist in OpenERP will be imported")), 
        'import_image_with_product': fields.boolean('With image', help=("If the option is check the product's image and"
                                                                    "the product will be imported at the same time and"
                                                                    "so the step '7-import images' is not needed")),
        'import_links_with_product': fields.boolean('With links', help=("If the option is check the product's links"
                                                                 "(Up-Sell, Cross-Sell, Related) and the product will be imported"
                                                                 "at the same time and so the step '8-import links' is not needed")),
        'ext_file_referential_id': fields.many2one('external.referential', 'External Referential File'),
        }

    def import_customer_groups(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'res.partner', context=context)
        return True 

    def import_product_categories(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'product.category', context=context)
        return True 

    def import_customers(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'res.partner', context=context)
        return True 

#    def import_product_attributes_sets(self, cr, uid, ids, context=None):
#        return self.import_resources(cr, uid, ids, 'TODO', context=context)
#
#    def import_product_attributes_groups(self, cr, uid, ids, context=None):
#        return self.import_resources(cr, uid, ids, 'TODO', context=context)
#
#    def import_product_attributes(self, cr, uid, ids, context=None):
#        return self.import_resources(cr, uid, ids, 'TODO', context=context)

    def import_products(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'product.product', context=context)
        return True 

#If we want to support that feature we need to add a dependancy on product_images_olbs
    def import_product_images(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'product.image', context=context)
        return True 

    def import_product_links(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'product.link', context=context)
        return True 






