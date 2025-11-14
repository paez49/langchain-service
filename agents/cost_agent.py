"""
Cost Agent - Analyzes costs and optimizes budget
"""

from data import INVENTORY
from models import State


def cost_agent(state: State) -> State:
    """
    COST AGENT: Analyzes costs and optimizes budget
    """
    print(f"💰 COST AGENT: Analyzing costs")
    
    cost_options = []
    
    for doc in state["catalog_candidates"]:
        sku = doc.metadata.get("sku")
        lots = INVENTORY.get(sku, [])
        
        for lot_info in lots:
            if lot_info["stock"] > 0:
                total_cost = lot_info["cost_usd"] * state["requested_quantity"]
                cost_options.append({
                    "sku": sku,
                    "warehouse": lot_info["warehouse"],
                    "unit_cost": lot_info["cost_usd"],
                    "total_cost": total_cost
                })
    
    # Sort by cost
    cost_options.sort(key=lambda x: x["unit_cost"])
    
    state["cost_result"] = {
        "cheapest_unit": cost_options[0]["unit_cost"] if cost_options else 0,
        "options": cost_options[:5]
    }
    
    print(f"   ✓ Lowest cost: ${state['cost_result']['cheapest_unit']:.2f}/unit\n")
    return state

