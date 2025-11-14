"""
Coordinator Agent - Synthesizes results from all specialized agents
"""

from datetime import datetime
from data import INVENTORY, LOGISTICS_ETA, REGULATIONS
from models import State, SubstituteCandidate


def coordinator_agent(state: State) -> State:
    """
    COORDINATOR AGENT: Synthesizes results from all specialized agents
    """
    print("=" * 80)
    print("🎯 COORDINATOR AGENT: Synthesizing results from specialized agents")
    print("=" * 80)
    
    # Filter valid candidates by combining all criteria
    compliance_skus = set(state["compliance_result"]["compliant_skus"])
    inventory_skus = {item["sku"] for item in state["inventory_result"]["inventory"]}
    
    # Intersection: only SKUs that meet ALL criteria
    valid_skus = compliance_skus & inventory_skus
    
    if not valid_skus:
        state["coordinator_synthesis"] = "No substitutes meet all criteria."
        state["compliant_substitutes"] = []
        print("   ⚠️  No valid substitutes found\n")
        return state
    
    # Build complete candidates
    country = state["requested_country"]
    country_rules = REGULATIONS.get(country, {})
    min_shelf_life = country_rules.get("min_shelf_life_months", 6)
    
    candidates = []
    
    for doc in state["catalog_candidates"]:
        sku = doc.metadata.get("sku")
        if sku not in valid_skus:
            continue
        
        lots = INVENTORY.get(sku, [])
        
        for lot_info in lots:
            if lot_info["stock"] <= 0:
                continue
            
            # Calculate shelf life
            expiry_date = datetime.strptime(lot_info["expiry"], "%Y-%m-%d")
            months_remaining = (expiry_date - datetime.now()).days / 30
            
            if months_remaining < min_shelf_life:
                continue
            
            warehouse = lot_info["warehouse"]
            eta_days = LOGISTICS_ETA.get((warehouse, country), 999)
            
            # Multi-criteria scoring
            eta_score = max(0, 100 - eta_days * 5)
            stock_score = min(100, lot_info["stock"] / 10)
            shelf_life_score = min(100, months_remaining * 3)
            cost_score = max(0, 100 - lot_info["cost_usd"] * 100)
            
            total_score = (
                eta_score * 0.35 +
                stock_score * 0.25 +
                shelf_life_score * 0.25 +
                cost_score * 0.15
            )
            
            candidate = SubstituteCandidate(
                sku=sku,
                product_name=doc.page_content.split(" - ")[0],
                warehouse=warehouse,
                country=lot_info["country"],
                lot=lot_info["lot"],
                stock=lot_info["stock"],
                expiry=lot_info["expiry"],
                cost_usd=lot_info["cost_usd"],
                eta_days=eta_days,
                score=round(total_score, 2),
                compliance_rules=[
                    f"Registered in {country}",
                    f"Shelf life: {months_remaining:.1f} months",
                    f"Stock: {lot_info['stock']} units"
                ],
                justification=f"ETA: {eta_days}d from {warehouse}. Cost: ${lot_info['cost_usd']:.2f}. Expires: {lot_info['expiry']}."
            )
            
            candidates.append(candidate)
    
    # Sort by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    state["compliant_substitutes"] = candidates
    
    # Use LLM for synthesis
    summary = f"Found {len(candidates)} valid alternatives. "
    summary += f"Top 3: {', '.join([c['sku'] for c in candidates[:3]])}"
    
    state["coordinator_synthesis"] = summary
    
    print(f"   ✓ {len(candidates)} valid candidates synthesized")
    for i, c in enumerate(candidates[:3], 1):
        print(f"      {i}. {c['sku']} - Score: {c['score']:.1f}")
    print()
    
    return state

