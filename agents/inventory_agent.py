"""
Inventory Agent - Verifies stock availability
"""

from data import INVENTORY
from models import State


def inventory_agent(state: State) -> State:
    """
    INVENTORY AGENT: Verifies stock availability
    """
    print(f"📦 INVENTORY AGENT: Checking available stock")
    
    country = state["requested_country"]
    strategy = state["strategy"]
    
    available_inventory = []
    
    for doc in state["catalog_candidates"]:
        sku = doc.metadata.get("sku")
        lots = INVENTORY.get(sku, [])
        
        for lot_info in lots:
            # In "fast" strategy, only consider local warehouses
            if strategy == "fast" and lot_info["country"] != country:
                continue
            
            if lot_info["stock"] > 0:
                available_inventory.append({
                    "sku": sku,
                    "warehouse": lot_info["warehouse"],
                    "stock": lot_info["stock"],
                    "lot": lot_info["lot"],
                    "expiry": lot_info["expiry"]
                })
    
    state["inventory_result"] = {
        "available_count": len(available_inventory),
        "inventory": available_inventory
    }
    
    print(f"   ✓ {len(available_inventory)} lots with stock\n")
    return state

