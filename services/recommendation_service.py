"""
Recommendation Service - Main business logic for substitute recommendations
"""

from graph import app
from observability.middleware import get_observability_middleware


def recommend_substitute(
    requested_item: str, 
    country: str, 
    quantity: int = 100,
    urgency: str = "medium",
    enable_observability: bool = True,
    enable_ai_analysis: bool = False  # AI analysis is expensive, disabled by default
):
    """
    Main function to request substitute recommendations (MULTI-AGENT)
    
    Args:
        requested_item: Name of unavailable product
        country: Destination country code (CO, PE, MX)
        quantity: Required quantity
        urgency: Urgency level ("low", "medium", "high", "critical")
        enable_observability: Whether to track observability metrics
        enable_ai_analysis: Whether to run AI analysis on outputs (more expensive)
    
    Returns:
        Final state with recommendations and observability data
    """
    print("\n" + "=" * 80)
    print(f"🏥 MULTI-AGENT REGULATED SUBSTITUTE RECOMMENDER")
    print("=" * 80)
    print(f"Product: {requested_item}")
    print(f"Country: {country}")
    print(f"Quantity: {quantity} units")
    print(f"Urgency: {urgency.upper()}")
    print("=" * 80 + "\n")
    
    # Initialize observability tracking
    observability = None
    request_id = None
    
    if enable_observability:
        observability = get_observability_middleware(enable_ai_analysis=enable_ai_analysis)
        request_id = observability.start_request_tracking(
            requested_item=requested_item,
            country=country,
            urgency=urgency
        )
        print(f"📊 Observability enabled - Request ID: {request_id}\n")
    
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
        "observability_request_id": request_id,  # Add request ID to state
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
    
    # Finalize observability tracking
    if observability:
        try:
            observability_report = observability.finalize_request(
                strategy=result.get("strategy", "unknown"),
                recommendations_count=len(result.get("recommendations", [])),
                success=True,
                run_ai_analysis=enable_ai_analysis
            )
            
            result["observability"] = observability_report
            
            print("=" * 80)
            print("📈 OBSERVABILITY METRICS")
            print("=" * 80)
            metrics = observability_report["metrics"]
            print(f"Total execution time: {metrics['total_execution_time_ms']:.0f}ms")
            print(f"Total tokens used: {metrics['total_tokens']}")
            print(f"Total cost: ${metrics['total_cost_usd']:.4f}")
            print(f"Agents executed: {', '.join(metrics['agents_executed'])}")
            
            if observability_report.get("drift_analysis") and observability_report["drift_analysis"].get("drift_detected"):
                print("\n⚠️  DRIFT DETECTED:")
                for indicator in observability_report["drift_analysis"].get("drift_indicators", []):
                    print(f"   • {indicator}")
            
            print("=" * 80 + "\n")
        except Exception as e:
            print(f"⚠️  Warning: Observability tracking failed: {e}\n")
    
    return result

