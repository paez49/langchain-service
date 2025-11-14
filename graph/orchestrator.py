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

# Create graph
graph = StateGraph(State)

# 1. Manager Agent decides strategy
graph.set_entry_point("manager")
graph.add_node("manager", manager_agent)

# 2. Catalog search
graph.add_node("catalog_search", catalog_search_node)

# 3. SPECIALIZED AGENTS - Execute sequentially
graph.add_node("compliance_agent", compliance_agent)
graph.add_node("inventory_agent", inventory_agent)
graph.add_node("logistics_agent", logistics_agent)
graph.add_node("cost_agent", cost_agent)

# 4. Coordinator synthesizes results
graph.add_node("coordinator", coordinator_agent)

# 5. Recommendation Agent makes final decision
graph.add_node("recommendation", recommendation_agent)

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

