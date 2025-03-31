{
    "name": "Store Request Management",
    "version": "1.0",
    "summary": "Manage Store Requests and create Purchase Requests upon approval.",
    "author": "Your Name",
    "depends": ["purchase", "mail"],
    "data": [
        # "security/store_request_security.xml",
        "security/ir.model.access.csv",
        "views/store_request_views.xml",
        # "views/purchase_request_views.xml",
        # "views/purchase_request_views.xml",
    ],
    "installable": True,
    "application": False,
}
