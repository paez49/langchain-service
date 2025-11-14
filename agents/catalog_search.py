"""
Catalog Search Node - Searches for similar products using semantic RAG
"""

from data import search_catalog
from models import State


def catalog_search_node(state: State) -> State:
    """
    Search for similar products in catalog using semantic RAG
    """
    print(f"🔍 CATALOG SEARCH: Searching alternatives for '{state['requested_item']}'")
    
    # Adjust search based on strategy
    k = 3 if state["strategy"] == "fast" else 5 if state["strategy"] == "balanced" else 10
    
    similar_docs = search_catalog(state["requested_item"], k=k)
    state["catalog_candidates"] = similar_docs
    
    print(f"   ✓ Found {len(similar_docs)} candidates (strategy: {state['strategy']})\n")
    return state

