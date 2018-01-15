# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Affiliate Program",
    "summary": "This module allows creation of affiliates and the tracking the sales conversions generated by them.",
    "version": "11.0.1.0.0",
    "category": "Website",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA), Versada",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "data/sale_affiliate_data.xml",
        "security/ir.model.access.csv",
        "views/sale_affiliate_view.xml",
        "views/sale_affiliate_request_view.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [
        "demo/sale_affiliate_demo.xml",
    ],
}
