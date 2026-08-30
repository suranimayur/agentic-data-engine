# End-to-End Technical Guide

> A comprehensive, hands-on walkthrough of the Intelligent Multi-Agent Data Engineering Platform project.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Data Layer](#2-data-layer)
3. [Schema Definitions](#3-schema-definitions)
4. [Utility Modules](#4-utility-modules)
5. [SQL Analyst Agent](#5-sql-analyst-agent)
6. [ETL Analyst Agent](#6-etl-analyst-agent)
7. [Data Agent Orchestrator](#7-data-agent-orchestrator)
8. [Running the Project](#8-running-the-project)
9. [Example Walkthroughs](#9-example-walkthroughs)
10. [Extending the Project](#10-extending-the-project)

---

## 1. Architecture Overview

The Intelligent Multi-Agent Data Engineering Platform is a multi-agent system built with LangGraph. It routes natural language questions to specialized sub-agents:

```
                    ┌──────────────────────────┐
                    │      User Question        │
                    │  (Natural Language)        │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │    Router Node (LLM)      │
                    │  Classifies: SQL vs ETL   │
                    └────────────┬─────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │                               │
                 ▼                               ▼
    ┌────────────────────┐         ┌────────────────────┐
    │   SQL Analyst      │         │   ETL Analyst      │
    │                    │         │                    │
    │ 1. Curate Question │         │ 1. LLM Node        │
    │ 2. Build Context   │         │ 2. Tool Node       │
    │ 3. Generate SQL    │         │    - extract_load   │
    │ 4. Safety Check    │         │    - transform_load │
    │ 5. Execute Query   │         │ 3. Loop until done │
    │ 6. Format Answer   │         │                    │
    └────────────────────┘         └────────────────────┘
                 │                               │
                 ▼                               ▼
         PostgreSQL DB                    API / Files
```

---

## 2. Data Layer

The project uses a PostgreSQL database modeled after a ride-hailing platform.

### Tables

**users** — Registered users (riders and drivers)
| Column | Type | Description |
|--------|------|-------------|
| user_id | INTEGER (PK) | Unique user identifier |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| email | VARCHAR(255) | Unique email |
| phone | VARCHAR(50) | Phone number |
| city | VARCHAR(100) | City of residence |
| province | VARCHAR(50) | Province/state |
| user_type | VARCHAR(20) | "rider" or "driver" |
| signup_date | DATE | Registration date |
| is_active | BOOLEAN | Active status |

**vehicles** — Vehicles registered by drivers
| Column | Type | Description |
|--------|------|-------------|
| vehicle_id | INTEGER (PK) | Unique vehicle ID |
| driver_id | INTEGER (FK) | References users.user_id |
| make | VARCHAR(50) | Manufacturer |
| model | VARCHAR(50) | Model name |
| year | INTEGER | Manufacturing year |
| license_plate | VARCHAR(20) | Unique plate |
| color | VARCHAR(30) | Vehicle color |
| is_active | BOOLEAN | Active status |

**rides** — Completed and cancelled rides
| Column | Type | Description |
|--------|------|-------------|
| ride_id | INTEGER (PK) | Unique ride ID |
| rider_id | INTEGER (FK) | References users.user_id |
| driver_id | INTEGER (FK) | References users.user_id |
| requested_at | TIMESTAMP | Request time |
| pickup_time | TIMESTAMP | Pickup time |
| dropoff_time | TIMESTAMP | Dropoff time |
| distance_km | DECIMAL(10,2) | Trip distance |
| fare | DECIMAL(10,2) | Trip fare |
| status | VARCHAR(30) | completed, cancelled |

**payments** — Payment records
| Column | Type | Description |
|--------|------|-------------|
| payment_id | INTEGER (PK) | Unique payment ID |
| ride_id | INTEGER (FK) | References rides.ride_id |
| amount | DECIMAL(10,2) | Payment amount |
| payment_method | VARCHAR(50) | credit_card, paypal, etc. |
| payment_status | VARCHAR(30) | completed, pending |

**ratings** — Driver ratings
| Column | Type | Description |
|--------|------|-------------|
| rating_id | INTEGER (PK) | Unique rating ID |
| ride_id | INTEGER (FK) | References rides.ride_id |
| rating | INTEGER | 1-5 rating |
| comment | TEXT | Feedback text |

---

## 3. Schema Definitions

File: `Models/schema.py`

### AgentSchema (SQL Analyst)

```python
class AgentSchema(BaseModel):
    messages: list                       # Conversation history
    user_question: str                   # Original user input
    curated_question: str = ""           # Refined for SQL generation
    prompt_query_context: str = ""       # Full prompt with DB schema
    generated_sql_query: str = ""        # SQL from LLM
    is_safe_sql: Literal["Yes","No"]     # Safety result
    comments: str = ""                   # Safety comments
    sql_query_execution_result: str = "" # Query result
    final_answer: str = ""              # Formatted response
```

### RouterSchema

```python
class RouterSchema(BaseModel):
    answer: Literal["sql","etl"]         # Classification
    comments: str                        # Explanation
```

### JudgeSchema

```python
class JudgeSchema(BaseModel):
    answer: Literal["Yes","No"]          # Is SQL safe?
    comment: str                         # Safety details
```

---

## 4. Utility Modules

### LLM Selector (`utils/llm_pick.py`)

```python
def pick_llm(level: str):
    if level == "low":      # Fast, cheap
        return ChatOpenAI(model_name="gpt-5.6-luna", temperature=0)
    elif level == "medium": # Local, free
        return ChatOllama(model="gemma4:e4b", temperature=0)
    elif level == "high":   # Most capable
        return ChatOpenAI(model="gpt-5.6-terra", temperature=0)
```

### Database Utility (`utils/database.py`)

```python
class DatabaseUtil:
    def schema_details(self, schema_name):
        # Fetches tables, columns, types, sample data
        # Returns formatted string for LLM context

    def execute_sql(self, query):
        # Executes SQL and returns results
```

### ETL Tools (`utils/etl_tools.py`)

```python
class ETLTools:
    def extract_load(self, url, output_folder, format):
        # API request -> normalize JSON -> save to file

    def transform_load_context(self, file_path):
        # Read file -> return top 3 rows for LLM context

    def execute_code(self, code):
        # Execute dynamically generated pandas code
```

---

## 5. SQL Analyst Agent

File: `agents/sql_analyst.py`

7-node pipeline: `START -> curate -> context -> generate -> safety -> [execute|cancel] -> format -> END`

### Node Breakdown

| Node | Purpose |
|------|---------|
| `curate_question` | Refine user input for SQL generation |
| `prompt_query_context` | Fetch DB schema, build context prompt |
| `generate_sql_query` | LLM generates SQL from context |
| `is_safe_sql` | Judge validates query safety |
| `execute_sql_query` | Run query on PostgreSQL |
| `represent_final_answer` | Format results for user |
| `cancelled_sql` | Handle unsafe queries |

---

## 6. ETL Analyst Agent

File: `agents/etl_analyst.py`

Tool-calling loop: `START -> llm_node -> [tool_node -> llm_node (loop) | END]`

### Tools

| Tool | Purpose |
|------|---------|
| `extract_load_tool` | Fetch data from API, save to file |
| `transform_load_tool` | LLM generates pandas code, executes it |

---

## 7. Data Agent Orchestrator

File: `agents/data_agent.py`

3-node router: `START -> router_node -> [sql_node | etl_node] -> END`

The router uses structured output to classify questions as "sql" or "etl".

---

## 8. Running the Project

```bash
# 1. Install dependencies
uv sync

# 2. Configure
cp .env_sample .env
# Edit .env with your credentials

# 3. Setup Ollama
ollama pull gemma4:e4b
ollama serve

# 4. Seed database
python feed_db.py

# 5. Run agent
python main.py
```

---

## 9. Example Walkthroughs

### SQL: "What payment methods do we have?"

1. Router: "sql"
2. Curate: "Retrieve distinct payment_method from payments table"
3. Schema: [Full DB context injected]
4. SQL: `SELECT DISTINCT payment_method FROM public.payments LIMIT 10;`
5. Safety: Yes (SELECT only)
6. Result: `[('credit_card',), ('debit_card',), ('paypal',), ('apple_pay',)]`
7. Answer: "4 payment methods: credit_card, debit_card, paypal, apple_pay"

### ETL: "Extract Pokemon data"

1. Router: "etl"
2. LLM calls `extract_load_tool(url="https://pokeapi.co/api/v2/pokemon/", ...)`
3. Tool fetches API, normalizes JSON, saves CSV
4. LLM confirms: "Data successfully extracted"

---

## 10. Extending the Project

### Adding a New Agent

1. Create `agents/new_agent.py`
2. Define schema in `Models/schema.py`
3. Build LangGraph with `StateGraph`
4. Add routing in `data_agent.py`

### Adding New ETL Tools

```python
@tool
def new_tool(param: str) -> str:
    """Tool description."""
    return "result"
```

### Swapping LLM Providers

Edit `utils/llm_pick.py` to add new providers.
