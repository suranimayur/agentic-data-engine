# Intelligent Multi-Agent Data Engineering Platform — Documentation

> **Welcome!** This documentation covers everything you need to understand, build, extend, and master the Intelligent Multi-Agent Data Engineering Platform.

---

## Documentation Map

| Document | Description | Audience |
|----------|-------------|----------|
| [Main README](../README.md) | Project overview, quick start, and architecture | Everyone |
| [Technical Guide](GUIDE.md) | Step-by-step hands-on walkthrough | Developers |
| [Playbooks](PLAYBOOKS.md) | Zero-to-hero learning path for key technologies | Learners |
| [Tech Stack](TECH_STACK.md) | Deep dive into every library and tool | Architects |

---

## Quick Navigation

### New to the project?
1. Start with the [Main README](../README.md) for a high-level overview
2. Follow the [Playbooks](PLAYBOOKS.md) to learn each technology from scratch
3. Build the project using the [Technical Guide](GUIDE.md)

### Want to contribute?
1. Review the [Tech Stack](TECH_STACK.md) to understand the architecture
2. Read the [Technical Guide](GUIDE.md) for code walkthrough

### Want to learn Agentic AI?
1. Start with [Playbook 1: LangChain Fundamentals](PLAYBOOKS.md#-playbook-1-langchain-fundamentals)
2. Progress to [Playbook 2: LangGraph State Machines](PLAYBOOKS.md#-playbook-2-langgraph--state-machines)
3. Master with [Playbook 3: Building Agentic AI](PLAYBOOKS.md#-playbook-3-building-agentic-ai-patterns)

---

## Key Concepts at a Glance

| Concept | What It Is | Where It Lives |
|---------|-----------|----------------|
| **LangGraph** | Framework for building stateful agent workflows | `agents/` — all graph definitions |
| **LangChain** | LLM integration, tool binding, message handling | `utils/llm_pick.py`, `agents/etl_analyst.py` |
| **State Graph** | Directed graph defining agent execution flow | Each `*_agent.py` file |
| **Structured Output** | LLM responses constrained to Pydantic schemas | `Models/schema.py` |
| **Router Pattern** | Conditional routing based on LLM classification | `data_agent.py` |
| **Tool Binding** | Attaching callable tools to an LLM | `etl_analyst.py` |
| **SQL Judge** | Safety validation of generated SQL queries | `sql_analyst.py` |

---

## Prerequisites

- Python 3.14+ installed
- PostgreSQL running locally
- Ollama installed with `gemma4:e4b` model
- OpenAI API key (for GPT-5.6 models)
- Basic Python knowledge

---

## Further Reading

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

*Last updated: August 2026*
