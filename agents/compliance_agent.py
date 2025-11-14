"""
Compliance Agent - Verifies regulatory compliance
"""

from langchain_core.prompts import ChatPromptTemplate
from config import llm
from data import REGULATIONS
from models import State


def compliance_agent(state: State) -> State:
    """
    COMPLIANCE AGENT: Verifies regulatory compliance
    """
    print(f"👮 COMPLIANCE AGENT: Verifying {state['requested_country']} regulations")
    
    country = state["requested_country"]
    country_rules = REGULATIONS.get(country, {})
    
    compliant_skus = []
    violations = []
    
    for doc in state["catalog_candidates"]:
        sku = doc.metadata.get("sku")
        cold_chain = doc.metadata.get("cold_chain", False)
        
        # Verify registration
        if sku not in country_rules.get("registered_skus", []):
            violations.append(f"{sku}: Not registered in {country}")
            continue
        
        # Verify cold chain
        if cold_chain and not country_rules.get("cold_chain_capable", False):
            violations.append(f"{sku}: Requires cold chain not available")
            continue
        
        compliant_skus.append(sku)
    
    # Use LLM to generate reasoning
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Compliance Agent. Summarize the regulatory findings in 1-2 sentences."),
        ("user", f"Compliant: {compliant_skus}\nViolations: {violations}")
    ])
    
    reasoning = (prompt | llm).invoke({}).content if violations else "All candidates comply with regulations."
    
    state["compliance_result"] = {
        "compliant_skus": compliant_skus,
        "violations": violations,
        "reasoning": reasoning
    }
    
    print(f"   ✓ {len(compliant_skus)} compliant products\n")
    return state

