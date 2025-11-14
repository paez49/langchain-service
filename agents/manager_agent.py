"""
Manager Agent - Analyzes request and decides optimal strategy
"""

from langchain_core.prompts import ChatPromptTemplate
from config import llm
from models import State


def manager_agent(state: State) -> State:
    """
    MANAGER AGENT: Analyzes request and decides optimal strategy
    """
    print("=" * 80)
    print("🎯 MANAGER AGENT: Analyzing request and defining strategy")
    print("=" * 80)
    
    urgency = state.get("urgency", "medium")
    quantity = state["requested_quantity"]
    
    # Use LLM to decide strategy
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a Manager Agent expert in pharmaceutical logistics. "
         "Analyze the request and decide the best strategy: "
         "'fast' (priority on speed, local warehouses only), "
         "'balanced' (balance between cost/speed), or "
         "'exhaustive' (exhaustive global search, including special imports)."),
        ("user", 
         f"Product: {state['requested_item']}\n"
         f"Country: {state['requested_country']}\n"
         f"Quantity: {quantity}\n"
         f"Urgency: {urgency}\n\n"
         "Decide the strategy and briefly explain why.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({}).content
    
    # Extract strategy from response
    if "fast" in response.lower():
        strategy = "fast"
    elif "exhaustive" in response.lower():
        strategy = "exhaustive"
    else:
        strategy = "balanced"
    
    state["strategy"] = strategy
    
    print(f"📊 Urgency: {urgency}")
    print(f"🎯 Selected strategy: {strategy.upper()}")
    print(f"💬 Reasoning: {response[:200]}...")
    print()
    
    return state

