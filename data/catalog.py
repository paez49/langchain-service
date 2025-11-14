"""
Master Catalog - Pharmaceutical/medical products with metadata
"""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import embeddings

# Master catalog of pharmaceutical products
catalog_docs = [
    Document(
        page_content="Paracetamol 500mg - ATC Code: N02BE01 - Analgesic/Antipyretic - Cold chain: NO - Shelf life: 36 months - Packaging: Blister x30",
        metadata={"sku": "PARA-500", "atc": "N02BE01", "cold_chain": False, "shelf_life_months": 36}
    ),
    Document(
        page_content="Ibuprofen 400mg - ATC Code: M01AE01 - Anti-inflammatory - Cold chain: NO - Shelf life: 24 months - Packaging: Blister x20",
        metadata={"sku": "IBU-400", "atc": "M01AE01", "cold_chain": False, "shelf_life_months": 24}
    ),
    Document(
        page_content="Amoxicillin 500mg - ATC Code: J01CA04 - Antibiotic - Cold chain: NO - Shelf life: 24 months - Packaging: Blister x21",
        metadata={"sku": "AMOX-500", "atc": "J01CA04", "cold_chain": False, "shelf_life_months": 24}
    ),
    Document(
        page_content="Insulin Glargine 100UI/ml - ATC Code: A10AE04 - Antidiabetic - Cold chain: YES (2-8°C) - Shelf life: 30 months - Packaging: 3ml Cartridge",
        metadata={"sku": "INSUL-GLAR", "atc": "A10AE04", "cold_chain": True, "shelf_life_months": 30}
    ),
    Document(
        page_content="Omeprazole 20mg - ATC Code: A02BC01 - Proton pump inhibitor - Cold chain: NO - Shelf life: 36 months - Packaging: Blister x28",
        metadata={"sku": "OMEP-20", "atc": "A02BC01", "cold_chain": False, "shelf_life_months": 36}
    ),
    Document(
        page_content="Losartan 50mg - ATC Code: C09CA01 - Antihypertensive - Cold chain: NO - Shelf life: 24 months - Packaging: Blister x30",
        metadata={"sku": "LOSAR-50", "atc": "C09CA01", "cold_chain": False, "shelf_life_months": 24}
    ),
]

# Initialize vector store with embeddings
vectorstore = FAISS.from_documents(catalog_docs, embeddings)


def search_catalog(query: str, k: int = 5):
    """Search for similar products in catalog using embeddings"""
    return vectorstore.similarity_search(query, k=k)

