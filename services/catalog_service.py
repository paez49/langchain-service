"""
Catalog Service - Product management functions
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from config import embeddings
import data


def add_product_to_catalog(
    product_description: str,
    sku: str,
    atc_code: str,
    cold_chain: bool = False,
    shelf_life_months: int = 24
):
    """
    Allows adding new products to the catalog dynamically
    """
    new_doc = Document(
        page_content=product_description,
        metadata={
            "sku": sku,
            "atc": atc_code,
            "cold_chain": cold_chain,
            "shelf_life_months": shelf_life_months
        }
    )
    
    data.catalog_docs.append(new_doc)
    # Recreate vectorstore with all documents
    data.vectorstore = FAISS.from_documents(data.catalog_docs, embeddings)
    
    print(f"✅ Product {sku} added to catalog")
    return new_doc


def bulk_add_products(products: List[Dict[str, Any]]):
    """
    Add multiple products to catalog
    """
    for product in products:
        add_product_to_catalog(
            product_description=product["description"],
            sku=product["sku"],
            atc_code=product["atc"],
            cold_chain=product.get("cold_chain", False),
            shelf_life_months=product.get("shelf_life_months", 24)
        )

