from datetime import date, timedelta

TODAY = date.today()

RFP_LISTINGS = [
    {
        "id": "RFP-001",
        "title": "Supply of LV Power & Control Cables for Metro Depot",
        "source_url": "https://example-lstk1.com/tenders",
        "due_date": TODAY + timedelta(days=45),
        "scope_of_supply": [
            {
                "line_id": 1,
                "description": "4C 16sqmm Cu XLPE 1.1kV armoured feeder cable",
                "quantity_m": 5000,
                "required_specs": {
                    "conductor": "copper",
                    "insulation": "XLPE",
                    "voltage_kV": 1.1,
                    "cores": 4,
                    "size_sqmm": 16,
                    "armoured": True,
                },
            },
            {
                "line_id": 2,
                "description": "2C 4sqmm Cu PVC 1.1kV unarmoured control cable",
                "quantity_m": 3000,
                "required_specs": {
                    "conductor": "copper",
                    "insulation": "PVC",
                    "voltage_kV": 1.1,
                    "cores": 2,
                    "size_sqmm": 4,
                    "armoured": False,
                },
            },
        ],
        "tests_and_acceptance": [
            "routine_electrical_tests",
            "insulation_resistance_test",
        ],
    },
    {
        "id": "RFP-002",
        "title": "Supply of Aluminium Power Cables for Industrial Plant",
        "source_url": "https://example-lstk2.com/rfps",
        "due_date": TODAY + timedelta(days=120),  # will usually be filtered (> 3 months)
        "scope_of_supply": [
            {
                "line_id": 1,
                "description": "3.5C 95sqmm Al XLPE 1.1kV armoured main incomer cable",
                "quantity_m": 2000,
                "required_specs": {
                    "conductor": "aluminium",
                    "insulation": "XLPE",
                    "voltage_kV": 1.1,
                    "cores": 3.5,
                    "size_sqmm": 95,
                    "armoured": True,
                },
            }
        ],
        "tests_and_acceptance": [
            "routine_electrical_tests",
            "type_test",
            "fire_resistance_test",
        ],
    },
]
