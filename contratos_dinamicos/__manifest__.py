{ 
    "name": "Contratos Dinamicos",
    "version": "17.0.1.0.0",
    "depends": ["sale_renting","stock", "account",],
    "author": "Benjamin Aquino, Mauricio Gimenez, Elvio Baez.",
    "description": "Genera contratos de alquiler completo con campos dinámicos",
    "license": "GPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_renting_inherit.xml",
        "views/inventory_view_inherit.xml",
        "views/sale_order_view.xml",
        "report/contrato_dinamico_template.xml",
        "report/contrato_dinamico_report.xml",
    ],
    "installable": True,
    "application": False
}