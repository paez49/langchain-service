"""
Multi-Agent Orchestrator System using LangGraph
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models import State
from agents import (
    manager_agent,
    catalog_search_node,
    compliance_agent,
    inventory_agent,
    logistics_agent,
    cost_agent,
    coordinator_agent,
    recommendation_agent,
)
from observability.agent_wrapper import with_observability

# Wrap agents with observability tracking
manager_agent_wrapped = with_observability("manager_agent")(manager_agent)
catalog_search_wrapped = with_observability("catalog_search")(catalog_search_node)
compliance_agent_wrapped = with_observability("compliance_agent")(compliance_agent)
inventory_agent_wrapped = with_observability("inventory_agent")(inventory_agent)
logistics_agent_wrapped = with_observability("logistics_agent")(logistics_agent)
cost_agent_wrapped = with_observability("cost_agent")(cost_agent)
coordinator_agent_wrapped = with_observability("coordinator_agent")(coordinator_agent)
recommendation_agent_wrapped = with_observability("recommendation_agent")(recommendation_agent)

# Create graph
graph = StateGraph(State)

# 1. Manager Agent decides strategy (with observability)
graph.set_entry_point("manager")
graph.add_node("manager", manager_agent_wrapped)

# 2. Catalog search (with observability)
graph.add_node("catalog_search", catalog_search_wrapped)

# 3. SPECIALIZED AGENTS - Execute sequentially (with observability)
graph.add_node("compliance_agent", compliance_agent_wrapped)
graph.add_node("inventory_agent", inventory_agent_wrapped)
graph.add_node("logistics_agent", logistics_agent_wrapped)
graph.add_node("cost_agent", cost_agent_wrapped)

# 4. Coordinator synthesizes results (with observability)
graph.add_node("coordinator", coordinator_agent_wrapped)

# 5. Recommendation Agent makes final decision (with observability)
graph.add_node("recommendation", recommendation_agent_wrapped)

# Graph connections
graph.add_edge("manager", "catalog_search")

# After catalog_search, execute specialized agents sequentially
# (This avoids convergence issues in LangGraph)
graph.add_edge("catalog_search", "compliance_agent")
graph.add_edge("compliance_agent", "inventory_agent")
graph.add_edge("inventory_agent", "logistics_agent")
graph.add_edge("logistics_agent", "cost_agent")

# Cost agent (last agent) passes to coordinator
graph.add_edge("cost_agent", "coordinator")

# Coordinator passes to recommendation
graph.add_edge("coordinator", "recommendation")

# Recommendation is the final node
graph.add_edge("recommendation", END)

# Compile graph with memory
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

print("✅ Multi-Agent System Graph compiled successfully!")
print("   Architecture: Manager → Catalog → Compliance → Inventory → Logistics → Cost → Coordinator → Recommendation")

