"""
Simulated Inventory Data
Inventory by warehouse/lot/country
"""

INVENTORY = {
    "PARA-500": [
        {"warehouse": "BOG-01", "country": "CO", "lot": "L2024-001", "stock": 1500, "expiry": "2026-12-01", "cost_usd": 0.15},
        {"warehouse": "LIM-01", "country": "PE", "lot": "L2024-002", "stock": 800, "expiry": "2026-10-15", "cost_usd": 0.18},
    ],
    "IBU-400": [
        {"warehouse": "BOG-01", "country": "CO", "lot": "L2024-010", "stock": 2000, "expiry": "2026-08-20", "cost_usd": 0.25},
        {"warehouse": "MEX-01", "country": "MX", "lot": "L2024-011", "stock": 1200, "expiry": "2026-09-10", "cost_usd": 0.22},
    ],
    "OMEP-20": [
        {"warehouse": "BOG-01", "country": "CO", "lot": "L2024-020", "stock": 500, "expiry": "2027-03-01", "cost_usd": 0.40},
        {"warehouse": "LIM-01", "country": "PE", "lot": "L2024-021", "stock": 300, "expiry": "2027-02-15", "cost_usd": 0.42},
    ],
    "AMOX-500": [
        {"warehouse": "BOG-01", "country": "CO", "lot": "L2024-030", "stock": 0, "expiry": "2026-11-01", "cost_usd": 0.35},  # Out of stock
        {"warehouse": "MEX-01", "country": "MX", "lot": "L2024-031", "stock": 600, "expiry": "2026-12-20", "cost_usd": 0.38},
    ],
    "LOSAR-50": [
        {"warehouse": "LIM-01", "country": "PE", "lot": "L2024-040", "stock": 900, "expiry": "2026-07-01", "cost_usd": 0.30},
    ],
}

