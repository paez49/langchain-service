# Multi-Agent Pharmaceutical Substitute Recommender System

A sophisticated AI-powered REST API service that uses a multi-agent architecture to recommend pharmaceutical product substitutes while ensuring regulatory compliance, inventory availability, and optimal logistics.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [System Components](#system-components)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Setup & Installation](#setup--installation)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

---

## 🎯 Overview

This system addresses a critical challenge in pharmaceutical supply chains: **finding suitable substitute products when a requested item is unavailable**. The system considers multiple factors:

- **Regulatory Compliance**: Products must be registered in the destination country
- **Inventory Availability**: Real-time stock levels across multiple warehouses
- **Logistics Optimization**: Delivery times and warehouse locations
- **Cost Analysis**: Unit costs and total order costs
- **Urgency Adaptation**: Different strategies based on urgency level

The system uses **LangChain**, **LangGraph**, and **AWS Bedrock** to orchestrate multiple specialized AI agents that collaborate to make intelligent recommendations.

---

## 🏗️ Architecture

The system implements a **hierarchical multi-agent architecture** using LangGraph:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI REST API                        │
│                  (main.py - Entry Point)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Orchestrator                      │
│              (graph/orchestrator.py)                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. MANAGER AGENT (Strategic Planning)               │  │
│  │     • Analyzes request urgency                        │  │
│  │     • Selects strategy: fast/balanced/exhaustive      │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. CATALOG SEARCH (RAG with Vector Embeddings)      │  │
│  │     • Semantic search for similar products            │  │
│  │     • Uses FAISS vector store                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. SPECIALIZED AGENTS (Sequential Execution)        │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ COMPLIANCE AGENT                              │    │  │
│  │  │ • Verifies regulatory registration            │    │  │
│  │  │ • Checks cold chain requirements              │    │  │
│  │  │ • Validates country-specific rules            │    │  │
│  │  └──────────────────┬───────────────────────────┘    │  │
│  │                     │                                  │  │
│  │  ┌──────────────────▼───────────────────────────┐    │  │
│  │  │ INVENTORY AGENT                               │    │  │
│  │  │ • Checks stock availability                   │    │  │
│  │  │ • Filters by strategy (local/regional/global) │    │  │
│  │  │ • Verifies expiry dates                       │    │  │
│  │  └──────────────────┬───────────────────────────┘    │  │
│  │                     │                                  │  │
│  │  ┌──────────────────▼───────────────────────────┐    │  │
│  │  │ LOGISTICS AGENT                               │    │  │
│  │  │ • Calculates ETAs from warehouses             │    │  │
│  │  │ • Optimizes delivery routes                   │    │  │
│  │  │ • Ranks by fastest delivery time              │    │  │
│  │  └──────────────────┬───────────────────────────┘    │  │
│  │                     │                                  │  │
│  │  ┌──────────────────▼───────────────────────────┐    │  │
│  │  │ COST AGENT                                    │    │  │
│  │  │ • Analyzes unit costs                         │    │  │
│  │  │ • Calculates total order cost                 │    │  │
│  │  │ • Identifies most economical options          │    │  │
│  │  └──────────────────┬───────────────────────────┘    │  │
│  └─────────────────────┼──────────────────────────────┘  │
│                        │                                   │
│                        ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. COORDINATOR AGENT (Synthesis)                    │  │
│  │     • Combines results from all agents                │  │
│  │     • Filters candidates meeting ALL criteria         │  │
│  │     • Calculates multi-criteria scores                │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  5. RECOMMENDATION AGENT (Final Decision)            │  │
│  │     • Negotiates between competing criteria           │  │
│  │     • Generates Top-3 recommendations                 │  │
│  │     • Creates executive report with justification     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Agent Communication Flow

The agents execute **sequentially** to avoid convergence issues in LangGraph:

1. **Manager** → Sets strategy
2. **Catalog Search** → Finds similar products
3. **Compliance** → Filters by regulations
4. **Inventory** → Checks stock
5. **Logistics** → Calculates ETAs
6. **Cost** → Analyzes costs
7. **Coordinator** → Synthesizes all data
8. **Recommendation** → Makes final decision

Each agent updates a **shared state** (TypedDict) that flows through the graph.

---

## ✨ Key Features

### 1. **Adaptive Strategy Selection**
- **Fast Strategy** (high/critical urgency): Local warehouses only, top-3 products
- **Balanced Strategy** (medium urgency): Regional search, top-5 products
- **Exhaustive Strategy** (low urgency): Global search, top-10 products

### 2. **Semantic Product Search (RAG)**
- Uses **FAISS vector store** with AWS Bedrock embeddings
- Natural language queries (e.g., "aspirin for headache" → matches paracetamol)
- Supports ATC code classification

### 3. **Regulatory Compliance**
- Country-specific registration validation
- Cold chain capability checks
- Minimum shelf life requirements

### 4. **Multi-Criteria Scoring**
The coordinator calculates a composite score:
```python
score = (eta_score × 0.35) + 
        (stock_score × 0.25) + 
        (shelf_life_score × 0.25) + 
        (cost_score × 0.15)
```

### 5. **Dynamic Catalog Management**
- Add products via REST API
- Automatic vector store updates
- Supports bulk product uploads

### 6. **LLM-Powered Decision Making**
- Uses AWS Bedrock Nova Micro model
- Generates natural language justifications
- Creates executive-level reports

---

## 🧩 System Components

### **FastAPI REST Service** (`main.py`)
- Exposes HTTP endpoints for product management and recommendations
- Request/response validation with Pydantic models
- Auto-generated OpenAPI documentation (Swagger UI)

### **LangGraph Orchestrator** (`graph/orchestrator.py`)
- Defines agent workflow and connections
- Manages shared state between agents
- Uses `MemorySaver` for conversation persistence

### **Specialized Agents** (`agents/`)
- **Manager Agent**: Strategic planning and urgency analysis
- **Catalog Search**: Semantic similarity search using embeddings
- **Compliance Agent**: Regulatory validation with LLM reasoning
- **Inventory Agent**: Stock availability checks
- **Logistics Agent**: ETA calculation and route optimization
- **Cost Agent**: Cost analysis and budget optimization
- **Coordinator Agent**: Multi-criteria synthesis and scoring
- **Recommendation Agent**: Final decision with "negotiation" simulation

### **Data Layer** (`data/`)
- **catalog.py**: Product catalog with FAISS vector store
- **inventory.py**: Warehouse inventory by lot/SKU
- **logistics.py**: ETA mapping between warehouses and countries
- **regulations.py**: Country-specific compliance rules

### **Services** (`services/`)
- **catalog_service.py**: Product management functions
- **recommendation_service.py**: Main recommendation orchestration

### **Configuration** (`config/`)
- **aws_setup.py**: AWS Bedrock LLM and embeddings configuration

### **Models** (`models/`)
- **types.py**: TypedDict definitions for state and data structures

---

## 🔄 How It Works

### Example Request Flow

**Scenario**: A pharmacy in Colombia needs 200 units of "Aspirin for headache" with high urgency.

```
POST /api/v1/recommendations
{
  "requested_item": "Aspirin 500mg for headache",
  "country": "CO",
  "quantity": 200,
  "urgency": "high"
}
```

#### Step-by-Step Execution:

1. **Manager Agent** 
   - Analyzes: urgency=high, country=CO, quantity=200
   - Decision: "fast" strategy → search only local warehouses
   - LLM reasoning: "High urgency requires immediate delivery"

2. **Catalog Search**
   - Query: "Aspirin 500mg for headache"
   - Vector similarity search → finds: PARA-500, IBU-400, OMEP-20
   - Returns top-3 candidates (fast strategy)

3. **Compliance Agent**
   - Checks Colombia's regulations
   - PARA-500 ✓ (registered), IBU-400 ✓ (registered), OMEP-20 ✓ (registered)
   - All pass compliance

4. **Inventory Agent**
   - Checks stock in Colombian warehouses (BOG-01)
   - PARA-500: 1500 units available, lot L2024-001
   - IBU-400: 2000 units available, lot L2024-010
   - OMEP-20: 500 units available, lot L2024-020

5. **Logistics Agent**
   - Calculates ETAs from BOG-01 to CO
   - All products: 2 days (local warehouse)

6. **Cost Agent**
   - PARA-500: $0.15/unit → $30 total
   - IBU-400: $0.25/unit → $50 total
   - OMEP-20: $0.40/unit → $80 total

7. **Coordinator Agent**
   - Synthesizes all criteria
   - Calculates composite scores:
     - PARA-500: 92.5/100
     - IBU-400: 88.3/100
     - OMEP-20: 85.1/100

8. **Recommendation Agent**
   - Simulates "negotiation" between Speed/Cost/Compliance agents
   - LLM generates final recommendation
   - Output: Top-3 with justifications
   - Suggested action: SUBSTITUTE

#### Response:
```json
{
  "success": true,
  "strategy": "fast",
  "recommendations": [
    {
      "sku": "PARA-500",
      "product_name": "Paracetamol 500mg",
      "warehouse": "BOG-01",
      "stock": 1500,
      "eta_days": 2,
      "cost_usd": 0.15,
      "score": 92.5,
      "justification": "ETA: 2d from BOG-01. Cost: $0.15. Expires: 2026-12-01."
    }
  ],
  "suggested_action": "SUBSTITUTE",
  "final_report": "Executive summary with full analysis..."
}
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.100+ |
| **LLM Orchestration** | LangChain, LangGraph |
| **LLM Provider** | AWS Bedrock (Nova Micro v1) |
| **Embeddings** | AWS Bedrock (Titan Embed Text v2) |
| **Vector Store** | FAISS (CPU) |
| **API Server** | Uvicorn |
| **Data Validation** | Pydantic |
| **AWS SDK** | Boto3 |
| **Language** | Python 3.13+ |

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.13 or higher
- AWS Account with Bedrock access
- AWS credentials configured

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd langchain-service
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure AWS credentials**
```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option 2: AWS CLI
aws configure
```

5. **Verify AWS Bedrock access**
```bash
aws bedrock list-foundation-models --region us-east-1
```

6. **Run the service**
```bash
python main.py
```

The service will start on `http://localhost:8000`

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```http
GET /health
```

#### 2. Root Information
```http
GET /
```

#### 3. Add Product to Catalog
```http
POST /api/v1/products
Content-Type: application/json

{
  "product_description": "Atorvastatin 20mg - ATC Code: C10AA05 - Lipid-lowering agent",
  "sku": "ATOR-20",
  "atc_code": "C10AA05",
  "cold_chain": false,
  "shelf_life_months": 24
}
```

#### 4. Get Substitute Recommendations
```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "requested_item": "Aspirin 500mg for headache",
  "country": "CO",
  "quantity": 200,
  "urgency": "high"
}
```

**Urgency Levels:**
- `low`: Exhaustive global search
- `medium`: Balanced regional search (default)
- `high`: Fast local warehouse search
- `critical`: Fastest possible delivery

**Country Codes:**
- `CO`: Colombia
- `PE`: Peru
- `MX`: Mexico

---

## 💡 Usage Examples

### Example 1: High Urgency Request

```python
import requests

response = requests.post("http://localhost:8000/api/v1/recommendations", json={
    "requested_item": "Paracetamol for fever",
    "country": "CO",
    "quantity": 100,
    "urgency": "critical"
})

result = response.json()
print(f"Strategy: {result['strategy']}")
print(f"Top recommendation: {result['recommendations'][0]['sku']}")
```

### Example 2: Add New Product

```python
import requests

response = requests.post("http://localhost:8000/api/v1/products", json={
    "product_description": "Metformin 850mg - ATC Code: A10BA02 - Oral antidiabetic",
    "sku": "METF-850",
    "atc_code": "A10BA02",
    "cold_chain": False,
    "shelf_life_months": 36
})

print(response.json())
```

### Example 3: Low Urgency with Cost Optimization

```python
import requests

response = requests.post("http://localhost:8000/api/v1/recommendations", json={
    "requested_item": "Anti-inflammatory medication",
    "country": "MX",
    "quantity": 500,
    "urgency": "low"
})

# Will use exhaustive strategy - searches all warehouses globally
```

---

## 📁 Project Structure

```
langchain-service/
│
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
│
├── agents/                      # Specialized AI agents
│   ├── __init__.py
│   ├── manager_agent.py         # Strategic planning agent
│   ├── catalog_search.py        # RAG-based product search
│   ├── compliance_agent.py      # Regulatory validation
│   ├── inventory_agent.py       # Stock availability checker
│   ├── logistics_agent.py       # ETA calculator
│   ├── cost_agent.py            # Cost analyzer
│   ├── coordinator_agent.py     # Multi-criteria synthesizer
│   └── recommendation_agent.py  # Final decision maker
│
├── graph/                       # LangGraph orchestration
│   ├── __init__.py
│   └── orchestrator.py          # Agent workflow definition
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── catalog_service.py       # Product management
│   └── recommendation_service.py # Main orchestration logic
│
├── data/                        # Data sources and models
│   ├── __init__.py
│   ├── catalog.py               # Product catalog + FAISS
│   ├── inventory.py             # Warehouse inventory
│   ├── logistics.py             # ETA mappings
│   └── regulations.py           # Country regulations
│
├── models/                      # Data models and types
│   ├── __init__.py
│   └── types.py                 # TypedDict definitions
│
├── config/                      # Configuration
│   ├── __init__.py
│   └── aws_setup.py             # AWS Bedrock setup
│
└── venv/                        # Virtual environment (excluded)
```

---

## 🎓 Key Concepts

### 1. **LangGraph State Management**
The system uses a shared `State` (TypedDict) that flows through all agents:
```python
class State(TypedDict):
    requested_item: str
    requested_country: str
    strategy: str
    catalog_candidates: List[Document]
    compliance_result: Dict
    inventory_result: Dict
    recommendations: List[SubstituteCandidate]
    # ... more fields
```

### 2. **RAG (Retrieval Augmented Generation)**
The catalog uses semantic search:
- Products are embedded using AWS Bedrock Titan
- Stored in FAISS vector database
- Query: "headache medicine" → retrieves paracetamol, ibuprofen
- More intelligent than keyword matching

### 3. **Multi-Criteria Decision Making**
The coordinator balances:
- **Speed** (35%): Faster delivery = higher score
- **Availability** (25%): More stock = higher score
- **Shelf Life** (25%): Longer expiry = higher score
- **Cost** (15%): Lower cost = higher score

### 4. **Agent Negotiation Pattern**
The recommendation agent simulates negotiation:
- Speed Agent advocates for fastest option
- Cost Agent advocates for cheapest option
- Compliance Agent ensures regulatory adherence
- LLM mediates and makes final decision

---

## 🔧 Configuration

### AWS Bedrock Models

Edit `config/aws_setup.py` to change models:

```python
# LLM for reasoning
llm = ChatBedrock(
    model_id="us.amazon.nova-micro-v1:0",  # Change model here
    temperature=0.2,
)

# Embeddings for semantic search
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0"  # Change embeddings here
)
```

### Adding Countries

Edit `data/regulations.py`:

```python
REGULATIONS = {
    "BR": {  # Brazil
        "registered_skus": ["PARA-500", "IBU-400"],
        "min_shelf_life_months": 12,
        "cold_chain_capable": True,
    }
}
```

### Adding Warehouses

Edit `data/logistics.py`:

```python
LOGISTICS_ETA = {
    ("SAO-01", "BR"): 3,  # São Paulo to Brazil: 3 days
}
```

---

## 🚨 Error Handling

The system handles common scenarios:

1. **No substitutes found**: Returns `WAIT_FOR_RESTOCK` action
2. **Non-compliant products**: Filtered out by compliance agent
3. **Out of stock**: Filtered by inventory agent
4. **Invalid country**: Returns error with valid options
5. **Invalid urgency**: Returns 400 Bad Request

---

## 🤝 Contributing

To extend the system:

1. **Add new agents**: Create in `agents/` and register in orchestrator
2. **Add data sources**: Extend `data/` modules
3. **Modify scoring**: Edit `coordinator_agent.py` score calculation
4. **Add endpoints**: Extend `main.py` with new routes

---

## 📝 License

This project is provided as-is for educational and commercial use.

---

## 🙋 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review agent logs in console output
3. Verify AWS Bedrock credentials and quotas

---

## 🎯 Future Enhancements

Potential improvements:
- [ ] Add authentication and API keys
- [ ] Integrate real ERP/inventory systems
- [ ] Support more countries and regulations
- [ ] Add caching for repeated queries
- [ ] Implement webhook notifications
- [ ] Add batch processing for multiple requests
- [ ] Historical analytics and reporting
- [ ] Machine learning for demand prediction

---

**Built with ❤️ using LangChain, LangGraph, and AWS Bedrock**

