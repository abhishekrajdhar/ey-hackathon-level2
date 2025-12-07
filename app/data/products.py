from datetime import date

PRODUCT_SPECS = [
    {
        "sku": "AP-CABLE-001",
        "name": "AP Copper XLPE 1.1kV 4C 16sqmm",
        "category": "Power Cable",
        "specs": {
            "conductor": "copper",
            "insulation": "XLPE",
            "voltage_kV": 1.1,
            "cores": 4,
            "size_sqmm": 16,
            "application": "feeder",
            "armoured": True,
        },
    },
    {
        "sku": "AP-CABLE-002",
        "name": "AP Copper XLPE 1.1kV 4C 25sqmm",
        "category": "Power Cable",
        "specs": {
            "conductor": "copper",
            "insulation": "XLPE",
            "voltage_kV": 1.1,
            "cores": 4,
            "size_sqmm": 25,
            "application": "feeder",
            "armoured": True,
        },
    },
    {
        "sku": "AP-CABLE-003",
        "name": "AP Aluminium XLPE 1.1kV 3.5C 95sqmm",
        "category": "Power Cable",
        "specs": {
            "conductor": "aluminium",
            "insulation": "XLPE",
            "voltage_kV": 1.1,
            "cores": 3.5,
            "size_sqmm": 95,
            "application": "main_incomer",
            "armoured": True,
        },
    },
    {
        "sku": "AP-CABLE-004",
        "name": "AP Copper PVC 1.1kV 2C 4sqmm",
        "category": "Control Cable",
        "specs": {
            "conductor": "copper",
            "insulation": "PVC",
            "voltage_kV": 1.1,
            "cores": 2,
            "size_sqmm": 4,
            "application": "control",
            "armoured": False,
        },
    },
]
