"""
Recommendation Agent - Makes final decision with negotiation between criteria
"""

from langchain_core.prompts import ChatPromptTemplate
from config import llm
from models import State, AgentDecision


def recommendation_agent(state: State) -> State:
    """
    RECOMMENDATION AGENT: Makes final decision considering "negotiation" between criteria
    """
    print("=" * 80)
    print("🤝 RECOMMENDATION AGENT: Negotiating final decision between criteria")
    print("=" * 80)
    
    if not state["compliant_substitutes"]:
        state["recommendations"] = []
        state["suggested_action"] = "WAIT_FOR_RESTOCK"
        state["final_report"] = "No substitutes found that meet regulatory and availability requirements."
        print("   ❌ No recommendations possible\n")
        return state
    
    # Simulate "negotiation" between agents using LLM
    top_candidates = state["compliant_substitutes"][:5]
    
    # Prepare arguments from each "specialist agent"
    speed_advocate = f"SPEED AGENT: Recommends {top_candidates[0]['sku']} for ETA of {top_candidates[0]['eta_days']} days"
    cost_advocate = f"COST AGENT: Recommends cheapest option (${min([c['cost_usd'] for c in top_candidates]):.2f}/unit)"
    compliance_advocate = f"COMPLIANCE AGENT: All candidates are compliant: {', '.join([c['sku'] for c in top_candidates[:3]])}"
    
    # LLM acts as mediator
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are the RECOMMENDATION AGENT MEDIATOR. "
         "Listen to the arguments from specialized agents and make the final decision. "
         "You must balance: speed (Speed Agent), cost (Cost Agent), compliance (Compliance Agent). "
         f"The request urgency is: {state['urgency']}. "
         f"The chosen strategy was: {state['strategy']}. "
         "Decide the Top-3 and explain your reasoning in 2-3 sentences."),
        ("user",
         f"{speed_advocate}\n{cost_advocate}\n{compliance_advocate}\n\n"
         f"Available candidates:\n" +
         "\n".join([f"- {c['sku']}: Score={c['score']:.1f}, ETA={c['eta_days']}d, Cost=${c['cost_usd']:.2f}" 
                    for c in top_candidates[:3]]) +
         "\n\nWhich do you recommend as first option and why?")
    ])
    
    chain = prompt | llm
    negotiation_result = chain.invoke({}).content
    
    print(f"💬 Negotiation between agents:")
    print(f"   {negotiation_result[:150]}...")
    print()
    
    # Generate agent decisions
    state["agent_decisions"] = [
        AgentDecision(
            agent_name="Speed Agent",
            decision=top_candidates[0]["sku"],
            priority_score=100.0 - top_candidates[0]["eta_days"] * 5,
            reasoning=f"Minimize ETA: {top_candidates[0]['eta_days']} days"
        ),
        AgentDecision(
            agent_name="Cost Agent",
            decision=min(top_candidates, key=lambda x: x["cost_usd"])["sku"],
            priority_score=100.0 - min([c["cost_usd"] for c in top_candidates]) * 100,
            reasoning="Minimize total cost"
        ),
        AgentDecision(
            agent_name="Compliance Agent",
            decision=top_candidates[0]["sku"],
            priority_score=100.0,
            reasoning="All candidates comply with regulations"
        )
    ]
    
    # Top-3
    state["recommendations"] = top_candidates[:3]
    
    # Determine action
    if len(state["recommendations"]) == 1:
        state["suggested_action"] = "SUBSTITUTE"
    else:
        warehouses = set(r["warehouse"] for r in state["recommendations"])
        state["suggested_action"] = "SPLIT_WAREHOUSE" if len(warehouses) > 1 else "SUBSTITUTE"
    
    # Final executive report
    candidates_text = "\n".join([
        f"{i+1}. {r['sku']} - {r['product_name']}\n"
        f"   Score: {r['score']:.1f}/100\n"
        f"   {r['justification']}\n"
        f"   Compliance: {', '.join(r['compliance_rules'])}"
        for i, r in enumerate(state["recommendations"])
    ])
    
    report_prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are an expert assistant in regulated pharmaceutical supplies. "
         "Generate a professional executive report explaining the recommendations."),
        ("user", 
         f"REQUEST:\n"
         f"Product: {state['requested_item']}\n"
         f"Country: {state['requested_country']}\n"
         f"Quantity: {state['requested_quantity']}\n"
         f"Urgency: {state['urgency']}\n"
         f"Applied strategy: {state['strategy']}\n\n"
         f"ALTERNATIVES:\n{candidates_text}\n\n"
         f"AGENT ANALYSIS:\n{negotiation_result}\n\n"
         f"ACTION: {state['suggested_action']}\n\n"
         "Generate an executive report of 3-4 paragraphs.")
    ])
    
    report = (report_prompt | llm).invoke({}).content
    state["final_report"] = report
    
    print(f"   ✅ Final decision: {state['suggested_action']}")
    print(f"   ✅ Top recommendation: {state['recommendations'][0]['sku']}\n")
    
    return state

