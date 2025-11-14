"""
Recommendation Service - Main business logic for substitute recommendations
"""

from graph import app


def recommend_substitute(
    requested_item: str, 
    country: str, 
    quantity: int = 100,
    urgency: str = "medium"
):
    """
    Main function to request substitute recommendations (MULTI-AGENT)
    
    Args:
        requested_item: Name of unavailable product
        country: Destination country code (CO, PE, MX)
        quantity: Required quantity
        urgency: Urgency level ("low", "medium", "high", "critical")
    
    Returns:
        Final state with recommendations
    """
    print("\n" + "=" * 80)
    print(f"🏥 MULTI-AGENT REGULATED SUBSTITUTE RECOMMENDER")
    print("=" * 80)
    print(f"Product: {requested_item}")
    print(f"Country: {country}")
    print(f"Quantity: {quantity} units")
    print(f"Urgency: {urgency.upper()}")
    print("=" * 80 + "\n")
    
    state = {
        "requested_item": requested_item,
        "requested_country": country,
        "requested_quantity": quantity,
        "urgency": urgency,
        "strategy": None,
        "compliance_result": None,
        "inventory_result": None,
        "logistics_result": None,
        "cost_result": None,
        "catalog_candidates": [],
        "agent_decisions": [],
        "compliant_substitutes": [],
        "coordinator_synthesis": None,
        "recommendations": [],
        "suggested_action": "",
        "final_report": None,
    }
    
    # Configuration required by checkpointer
    config = {"configurable": {"thread_id": "1"}}
    result = app.invoke(state, config)
    
    print("\n" + "=" * 80)
    print("📊 FINAL EXECUTIVE REPORT")
    print("=" * 80)
    print(f"\n{result['final_report']}\n")
    
    if result["recommendations"]:
        print("🎯 Top-3 Recommended Substitutes:")
        print("-" * 80)
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"\n{i}. {rec['sku']} - {rec['product_name']}")
            print(f"   Score: {rec['score']:.1f}/100")
            print(f"   Warehouse: {rec['warehouse']} | Lot: {rec['lot']} | Stock: {rec['stock']} units")
            print(f"   {rec['justification']}")
            print(f"   Compliance: {', '.join(rec['compliance_rules'])}")
    
    print("\n" + "=" * 80)
    print(f"💼 SUGGESTED ACTION: {result['suggested_action']}")
    print(f"🎯 Applied strategy: {result['strategy'].upper()}")
    print("=" * 80 + "\n")
    
    return result

