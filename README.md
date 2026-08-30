<div align="center">

# 🤖 Intelligent Multi-Agent Data Engineering Platform

### Intelligent Multi-Agent System for Data Engineering

[![Python 3.14+](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.3+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-000000?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-5.0-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*Ask questions in natural language. Get SQL answers from your database or ETL pipelines from your APIs.*

[Getting Started](#-quick-start) · [Architecture](#-architecture) · [Playbooks](docs/PLAYBOOKS.md) · [Documentation](docs/)

---

</div>

## 🎯 Overview

The **Intelligent Multi-Agent Data Engineering Platform** is a production-grade multi-agent system that processes natural language queries and intelligently routes them to specialized AI agents for execution. The main agent acts as an intelligent router — it understands user intent and delegates tasks to either the **SQL Analyst Agent** (for database queries) or the **ETL Analyst Agent** (for data extraction and transformation workflows).

This project demonstrates modern AI engineering practices:

- Multi-agent orchestration with **LangGraph**
- Intelligent intent classification and query routing
- SQL safety validation to prevent destructive operations
- Tool-based agent architecture with dynamic code generation
- Multi-LLM provider strategy for cost-performance optimization

---

## 🏗️ Architecture

The system follows a hierarchical agent architecture with three interconnected LangGraph workflows:

```
                            ┌─────────────────────┐
                            │   User Question      │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │   Data Agent         │
                            │  (Intent Router)     │
                            └──────────┬──────────┘
                                       │
                       ┌───────────────┼───────────────┐
                       │                               │
            ┌──────────▼──────────┐       ┌────────────▼──────────┐
            │   SQL Analyst       │       │   ETL Analyst         │
            │                     │       │                       │
            │ ├─ Query Curation   │       │ ├─ Extract from API   │
            │ ├─ Schema Context   │       │ ├─ Transform with     │
            │ ├─ SQL Generation   │       │ │   Pandas (LLM-gen)  │
            │ ├─ Safety Validate  │       │ ├─ Load to Files      │
            │ ├─ Execute Query    │       │ └─ Loop Until Done    │
            │ └─ Format Answer    │       │                       │
            └──────────┬──────────┘       └────────────┬──────────┘
                       │                               │
                       ▼                               ▼
               PostgreSQL                       CSV / JSON / Parquet
```

### State Flow

1. **User Input** — Natural language query enters the system
2. **Router Node** — Classifies intent as SQL or ETL via structured LLM output
3. **Agent Dispatch** — Routes to the appropriate sub-agent
4. **Processing** — Each agent executes its specialized pipeline
5. **Output** — Returns structured, human-readable results

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Intelligent Routing** | Automatically classifies queries as SQL or ETL operations |
| **SQL Safety Validation** | Judge agent blocks destructive commands (INSERT, UPDATE, DELETE, DROP, ALTER) |
| **Dynamic Code Generation** | ETL agent generates Pandas code based on data context and user intent |
| **Schema-Aware SQL** | Injects actual database schema into LLM prompts for accurate queries |
| **Multi-Format Support** | CSV, JSON, and Parquet for data extraction and transformation |

### Multi-LLM Strategy

| Tier | Provider | Model | Use Case |
|------|----------|-------|----------|
| **Low** | OpenAI | GPT-5.6-Luna | Routing, curation, safety checks |
| **Medium** | Ollama (Local) | Gemma4:e4b | ETL code generation — zero API cost |
| **High** | OpenAI | GPT-5.6-Terra | Complex reasoning tasks |

### Safety Features

- SQL query inspection before execution
- Blocks destructive database operations
- Structured output validation via Pydantic
- Credentials stored in `.env` (never committed)

---

## 📦 Prerequisites

- **Python** 3.14+
- **PostgreSQL** running locally
- **Ollama** with `gemma4:e4b` model pulled
- **OpenAI API key** (for GPT-5.6 models)

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/suranimayur/AI_Data_Agent_Project_101.git
cd AI_Data_Agent_Project_101

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
uv sync
# or
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env_sample .env
```

Edit `.env` with your credentials:

```env
# PostgreSQL
host=localhost
port=5432
database=ola_data_agent
user=your_username
password=your_password

# OpenAI
OPENAI_API_KEY=sk-your-key-here
```

### 3. Setup Ollama

```bash
ollama pull gemma4:e4b
ollama serve   # Start in background
```

### 4. Seed the Database

```bash
python feed_db.py
```

This creates 5 tables (users, vehicles, rides, payments, ratings) and loads the Ola ride-hailing dataset.

### 5. Run the Agent

```bash
python main.py
```

---

## 📁 Project Structure

```
AI_Data_Agent_Project_101/
│
├── main.py                     # Entry point — invokes the data agent
├── feed_db.py                  # Database seeder (CSV to PostgreSQL)
│
├── agents/                     # LangGraph agent definitions
│   ├── data_agent.py           #    Top-level orchestrator (router)
│   ├── sql_analyst.py          #    SQL generation pipeline (7 nodes)
│   ├── etl_analyst.py          #    ETL tool-calling agent (2 nodes, looping)
│   └── scratch.py              #    Experimentation / testing scratchpad
│
├── Models/                     # Pydantic schemas
│   └── schema.py               #    AgentSchema, RouterSchema, JudgeSchema, etc.
│
├── utils/                      # Utility modules
│   ├── database.py             #    PostgreSQL wrapper
│   ├── llm_pick.py             #    LLM provider selector (OpenAI / Ollama)
│   └── etl_tools.py            #    ETL operations (extract, transform, execute)
│
├── data/                       # Dataset files
│   ├── users.csv               #    Ola users (riders & drivers)
│   ├── vehicles.csv            #    Registered vehicles
│   ├── rides.csv               #    Ride records
│   ├── payments.csv            #    Payment transactions
│   ├── ratings.csv             #    Driver ratings
│   ├── extract/                #    API extraction output
│   └── transform/              #    Transformation output
│
├── docs/                       # Documentation
│   ├── README.md               #    Documentation hub
│   ├── GUIDE.md                #    End-to-end technical guide
│   ├── PLAYBOOKS.md            #    Zero-to-hero learning path
│   └── TECH_STACK.md           #    Technology deep dive
│
├── .env_sample                 # Environment variable template
├── pyproject.toml              # Project config & dependencies
├── requirements.txt            # Pip-compatible dependencies
└── .gitignore                  # Git ignore rules
```

---

## 💻 Usage

### Basic Usage

```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

# Extract data from an API
response = data_agent.invoke({
    "messages": [
        HumanMessage(content="""
            Extract data from 'https://pokeapi.co/api/v2/pokemon'
            and save it to data/extract in CSV format
        """)
    ],
    "route_response": ""
})
print(response)
```

### SQL Query Example

```python
response = data_agent.invoke({
    "messages": [
        HumanMessage(content="Show me the top 5 cities by ride count")
    ],
    "route_response": ""
})
```

### ETL Transformation Example

```python
response = data_agent.invoke({
    "messages": [
        HumanMessage(content="""
            Transform rides.csv to filter only completed rides
            and save as Parquet to data/transform
        """)
    ],
    "route_response": ""
})
```

### Running Individual Agents

```bash
python agents/sql_analyst.py     # Run SQL analyst standalone
python agents/etl_analyst.py     # Run ETL analyst standalone
```

---

## 🤖 Agent Descriptions

### Data Agent (Main Router)

**File:** `agents/data_agent.py`

The orchestrator that receives natural language queries, classifies intent, and delegates to the appropriate sub-agent.

- **Router Node** — Uses structured output to classify query as `sql` or `etl`
- **Conditional Routing** — Dispatches to SQL or ETL agent based on classification
- **Graph Orchestration** — Manages the full workflow using LangGraph

---

### SQL Analyst Agent

**File:** `agents/sql_analyst.py`

A 7-node pipeline that converts natural language to safe, executed SQL:

| Step | Node | Purpose |
|------|------|---------|
| 1 | `curate_question` | Refine user input for SQL generation |
| 2 | `prompt_query_context` | Fetch DB schema and build context prompt |
| 3 | `generate_sql_query` | LLM generates SQL from curated question |
| 4 | `is_safe_sql` | Judge agent validates query safety |
| 5 | `execute_sql_query` | Run validated query on PostgreSQL |
| 6 | `represent_final_answer` | Format results into human-readable response |
| — | `cancelled_sql` | Handle rejected (unsafe) queries |

---

### ETL Analyst Agent

**File:** `agents/etl_analyst.py`

A tool-calling agent that loops until the task is complete:

| Tool | Purpose |
|------|---------|
| `extract_load_tool` | Fetch data from REST APIs and save to files |
| `transform_load_tool` | LLM generates Pandas code and executes transformations |

**Supported formats:** CSV, JSON, Parquet

---

## 📊 Data Models

| Schema | Purpose |
|--------|---------|
| `DataAgentSchema` | Top-level orchestrator state (messages + route response) |
| `AgentSchema` | SQL Analyst state (question to SQL to result lifecycle) |
| `ETLAgentSchema` | ETL Analyst state (message history with add_messages reducer) |
| `RouterSchema` | Intent classification output (`sql` or `etl`) |
| `JudgeSchema` | SQL safety validation output (`Yes` or `No`) |

---

## 📚 Examples

### Example 1: Database Query

**User:** *"What are the different payment methods in our database?"*

1. Router classifies as **SQL**
2. SQL Agent fetches schema context
3. Generates: `SELECT DISTINCT payment_method FROM payments LIMIT 10;`
4. Safety judge validates
5. Executes and formats: *"The database has 4 payment methods: credit_card, debit_card, paypal, apple_pay"*

---

### Example 2: Data Extraction

**User:** *"Extract Pokemon data from PokeAPI and save as CSV"*

1. Router classifies as **ETL**
2. ETL Agent selects `extract_load_tool`
3. Makes API request to `https://pokeapi.co/api/v2/pokemon/`
4. Normalizes nested JSON with `pd.json_normalize()`
5. Saves to `data/extract/extracted_data.csv`

---

### Example 3: Data Transformation

**User:** *"Transform the extracted data to show only Bulbasaur Pokemon"*

1. Router classifies as **ETL**
2. ETL Agent reads data context (first 3 rows)
3. LLM generates Pandas filter code
4. Executes: `df[df['name'] == 'bulbasaur']`
5. Saves result to `data/transform/`

---

## 📚 Documentation

| Document | What You'll Learn |
|----------|-------------------|
| [Technical Guide](docs/GUIDE.md) | Complete code walkthrough with architecture details |
| [Playbooks](docs/PLAYBOOKS.md) | Zero-to-hero learning path for LangChain, LangGraph, Pydantic, PostgreSQL |
| [Tech Stack](docs/TECH_STACK.md) | Deep dive into every library and tool used |
| [Docs Hub](docs/README.md) | Navigation guide for all documentation |

### Learning Path

New to these technologies? Follow this order:

1. [LangChain Fundamentals](docs/PLAYBOOKS.md#-playbook-1-langchain-fundamentals)
2. [LangGraph State Machines](docs/PLAYBOOKS.md#-playbook-2-langgraph--state-machines)
3. [Building Agentic AI Patterns](docs/PLAYBOOKS.md#-playbook-3-building-agentic-ai-patterns)
4. [Pydantic Schemas & Structured Output](docs/PLAYBOOKS.md#-playbook-4-pydantic-schemas--structured-output)
5. [PostgreSQL for Data Agents](docs/PLAYBOOKS.md#-playbook-5-postgresql-for-data-agents)
6. [LLM Providers & Model Routing](docs/PLAYBOOKS.md#-playbook-6-llm-providers--model-routing)

---

## 🛠️ Development

### Adding a New Agent

1. Create agent file in `agents/`
2. Define state schema in `Models/schema.py`
3. Build LangGraph with `StateGraph`
4. Add routing rule in `data_agent.py`
5. Update documentation

### Extending ETL Tools

```python
@tool
def new_tool(param: str) -> str:
    """Tool description for the LLM."""
    # Implementation
    return "result"
```

### Customizing LLM Selection

Edit `utils/llm_pick.py` to add new providers or adjust model parameters.

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Database connection failed` | Verify PostgreSQL is running and `.env` credentials are correct |
| `API key not found` | Ensure `OPENAI_API_KEY` is set in `.env` |
| `SQL query unsafe` | The query contains destructive operations — reformulate as SELECT only |
| `Module not found` | Activate virtual environment and run `pip install -r requirements.txt` |
| `Ollama connection refused` | Run `ollama serve` and ensure `gemma4:e4b` is pulled |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) — LLM framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Agent orchestration
- [Ollama](https://ollama.com/) — Local LLM runtime
- [PostgreSQL](https://postgresql.org/) — Database
- [Pandas](https://pandas.pydata.org/) — Data processing

---

<div align="center">

**Built with love using Agentic AI**

*Ask questions. Get answers. Let the agents do the work.*

</div>
