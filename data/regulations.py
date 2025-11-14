"""
Regulatory Rules by Country
"""

REGULATIONS = {
    "CO": {  # Colombia
        "registered_skus": ["PARA-500", "IBU-400", "OMEP-20", "AMOX-500"],
        "min_shelf_life_months": 6,
        "cold_chain_capable": True,
    },
    "PE": {  # Peru
        "registered_skus": ["PARA-500", "OMEP-20", "LOSAR-50"],
        "min_shelf_life_months": 8,
        "cold_chain_capable": True,
    },
    "MX": {  # Mexico
        "registered_skus": ["IBU-400", "AMOX-500", "PARA-500"],
        "min_shelf_life_months": 6,
        "cold_chain_capable": False,
    },
}

