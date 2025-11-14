"""
Logistics Agent - Calculates ETAs and optimizes routes
"""

from data import INVENTORY, LOGISTICS_ETA
from models import State


def logistics_agent(state: State) -> State:
    """
    LOGISTICS AGENT: Calculates ETAs and optimizes routes
    """
    print(f"🚚 LOGISTICS AGENT: Calculating ETAs and routes")
    
    country = state["requested_country"]
    logistics_options = []
    
    for doc in state["catalog_candidates"]:
        sku = doc.metadata.get("sku")
        lots = INVENTORY.get(sku, [])
        
        for lot_info in lots:
            if lot_info["stock"] <= 0:
                continue
            
            warehouse = lot_info["warehouse"]
            eta_days = LOGISTICS_ETA.get((warehouse, country), 999)
            
            logistics_options.append({
                "sku": sku,
                "warehouse": warehouse,
                "eta_days": eta_days,
                "route": f"{warehouse} → {country}"
            })
    
    # Sort by ETA
    logistics_options.sort(key=lambda x: x["eta_days"])
    
    state["logistics_result"] = {
        "fastest_eta": logistics_options[0]["eta_days"] if logistics_options else 999,
        "options": logistics_options[:5]  # Top 5
    }
    
    print(f"   ✓ Fastest ETA: {state['logistics_result']['fastest_eta']} days\n")
    return state

