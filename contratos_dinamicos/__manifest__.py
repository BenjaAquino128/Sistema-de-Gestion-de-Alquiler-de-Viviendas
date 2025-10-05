{ 
    "name": "Contratos Dinamicos",
    "version": "17.0.1.0.0",
    "depends": ["sale_renting","stock", "account",],
    "author": "Benjamin Aquino, Mauricio Gimenez, Elvio Baez.",
    "description": "Genera contratos de alquiler completo con campos dinámicos",
    "license": "GPL-3",
    "data": [
        "security/ir.model.access.csv",
        "report/contrato_dinamico_template.xml",
        "report/contrato_dinamico_report.xml",
        "report/recibo_pago_inh.xml",
        "views/info_vendedor_view.xml",
        "views/contrato_dinamico.xml", 
        "views/sale_renting_inherit.xml",
        "views/product_tempĺate_inh.xml",
        "views/sale_order_view.xml",
        "views/res_user_inh.xml",
    ],
    "installable": True,
    "application": False
}