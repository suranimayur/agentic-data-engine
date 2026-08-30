# Technology Stack — Deep Dive

> Every technology, library, and tool used in the Intelligent Multi-Agent Data Engineering Platform project.

---

## Core Frameworks

### LangChain (>= 1.3.16)
- **Role:** LLM integration, tool binding, message handling
- **Key usage:** ChatOpenAI, ChatOllama, @tool decorator, with_structured_output()

### LangGraph (>= 1.2.11)
- **Role:** Stateful agent workflow orchestration
- **Key usage:** StateGraph, conditional edges, compiled graphs

### Pydantic (>= 2.13.4)
- **Role:** Data validation, schema definition, structured output
- **Key usage:** BaseModel, Field, Literal types

---

## LLM Providers

### OpenAI (langchain-openai >= 1.6.0)
- **Models:** GPT-5.6-Luna (low), GPT-5.6-Terra (high)
- **Requires:** OPENAI_API_KEY

### Ollama (langchain-ollama >= 1.1.0)
- **Model:** gemma4:e4b (medium)
- **Requires:** Ollama running locally

---

## Data Layer

### PostgreSQL (psycopg2 >= 2.9.12)
- **Role:** Primary database
- **5 tables:** users, vehicles, rides, payments, ratings

### Pandas (>= 3.0.5)
- **Role:** Data manipulation, transformation, file I/O

---

## Build & Dependencies

### uv (uv_build >= 0.12.5)
- **Role:** Fast Python package manager

### pyproject.toml
- **Role:** Project config and dependency management

---

## Version Requirements

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.14+ | Runtime |
| LangChain | 1.3.16+ | LLM framework |
| LangGraph | 1.2.11+ | Agent orchestration |
| Pydantic | 2.13.4+ | Data validation |
| psycopg2 | 2.9.12+ | PostgreSQL driver |
| Pandas | 3.0.5+ | Data processing |
| python-dotenv | 1.0.0+ | Environment variables |

---

## Architecture Decisions

### Why Two LLM Providers?
- OpenAI for routing/curation (fast, cheap)
- Ollama for code generation (zero API cost, local)

### Why LangGraph?
- Explicit state management
- Conditional routing
- Visual graph output
- Composable sub-graphs

### Why Pydantic?
- Type safety
- Structured output constraints
- Self-documenting schemas
