# Playbooks — Zero to Hero

> Master the technologies behind this project from scratch.

---

## Table of Contents

| Playbook | Topic | Time |
|----------|-------|------|
| [Playbook 1](#-playbook-1-langchain-fundamentals) | LangChain Fundamentals | 30-45 min |
| [Playbook 2](#-playbook-2-langgraph--state-machines) | LangGraph & State Machines | 45-60 min |
| [Playbook 3](#-playbook-3-building-agentic-ai-patterns) | Building Agentic AI Patterns | 60-90 min |
| [Playbook 4](#-playbook-4-pydantic-schemas--structured-output) | Pydantic & Structured Output | 20-30 min |
| [Playbook 5](#-playbook-5-postgresql-for-data-agents) | PostgreSQL for Data Agents | 30-40 min |
| [Playbook 6](#-playbook-6-llm-providers--model-routing) | LLM Providers & Routing | 20-30 min |

---

## Playbook 1: LangChain Fundamentals

### What is LangChain?

LangChain is a framework for building LLM-powered applications. It provides:
- **Chat Models** — Interface with LLM providers
- **Messages** — Standardized message formats
- **Tools** — Functions that LLMs can call
- **Structured Output** — Constraining LLM responses to schemas

### Level 0: Chat Models

```python
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

llm = ChatOpenAI(model_name="gpt-4", temperature=0)
response = llm.invoke("What is the capital of France?")
print(response.content)
```

### Level 1: Messages

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

messages = [
    SystemMessage(content="You are a helpful data analyst."),
    HumanMessage(content="What tables are in our database?"),
]
response = llm.invoke(messages)
```

### Level 2: Tools

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Weather in {city}: 25C, sunny"

llm_with_tools = llm.bind_tools([get_weather])
response = llm_with_tools.invoke("What's the weather in London?")
print(response.tool_calls)
```

### Level 3: Structured Output

```python
from pydantic import BaseModel, Field
from typing import Literal

class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(description="Confidence score 0-1")

llm_structured = llm.with_structured_output(SentimentResult)
result = llm_structured.invoke("I love this product!")
print(result.sentiment)  # "positive"
```

---

## Playbook 2: LangGraph & State Machines

### What is LangGraph?

LangGraph builds stateful, multi-step AI workflows as directed graphs:
- **Nodes** = Processing steps
- **Edges** = Connections
- **State** = Data flowing through the graph

### Level 0: Basic Graph

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

class MyState(BaseModel):
    input: str = ""
    output: str = ""

def process(state: MyState):
    state.output = f"Processed: {state.input}"
    return state

graph = StateGraph(MyState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

app = graph.compile()
result = app.invoke({"input": "Hello"})
print(result.output)  # "Processed: Hello"
```

### Level 1: Conditional Edges

```python
class RouterState(BaseModel):
    question: str = ""
    route: str = ""

def router(state):
    state.route = "sql" if "database" in state.question else "etl"
    return state

def route_decision(state):
    return "sql_handler" if state.route == "sql" else "etl_handler"

graph = StateGraph(RouterState)
graph.add_node("router", router)
graph.add_conditional_edges("router", route_decision, {
    "sql_handler": "sql_handler",
    "etl_handler": "etl_handler",
})
```

### Level 2: Tool-Calling Loop

```python
from langchain_core.messages import SystemMessage, ToolMessage

def llm_node(state):
    system = SystemMessage(content="You have tools available.")
    response = llm_with_tools.invoke([system] + state.messages)
    return {"messages": [response]}

def tool_node(state):
    results = []
    for tool_call in state.messages[-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
    return {"messages": results}

def should_continue(state):
    return "tool_node" if state.messages[-1].tool_calls else END

graph.add_edge("tools", "llm")  # Loop back after tools
```

---

## Playbook 3: Building Agentic AI Patterns

### Pattern 1: Router Agent

```
User Input -> LLM Classifies -> Route to Handler
```

### Pattern 2: ReAct Agent (Reason + Act)

```
Think -> Act -> Observe -> Think -> Act -> ... -> Done
```

### Pattern 3: Judge Agent

```
Generate -> Judge -> Execute / Reject
```

### Pattern 4: Multi-Agent Orchestration

```
Orchestrator -> [SQL Agent | ETL Agent | Future Agent]
```

### Pattern 5: Context-Augmented Generation

```
User Query -> Fetch Context -> Augmented Prompt -> LLM -> Response
```

---

## Playbook 4: Pydantic Schemas & Structured Output

### Basic Models

```python
from pydantic import BaseModel, Field
from typing import Literal

class RouterSchema(BaseModel):
    answer: Literal["sql", "etl"]
    comments: str

# Constrain LLM output
llm_structured = llm.with_structured_output(RouterSchema)
result = llm_structured.invoke("Extract data from API")
print(result.answer)  # "etl"
```

---

## Playbook 5: PostgreSQL for Data Agents

### Schema Introspection

```python
# Get all tables
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

# Get columns
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'")
```

### Safe Query Execution

```python
def execute_sql(self, query):
    cursor.execute(query)
    result = cursor.fetchall()
    return str(result)
```

---

## Playbook 6: LLM Providers & Model Routing

### Multi-Provider Strategy

| Level | Provider | Model | Use Case |
|-------|----------|-------|----------|
| Low | OpenAI | GPT-5.6-Luna | Routing, curation |
| Medium | Ollama | Gemma4:e4b | Code generation (local) |
| High | OpenAI | GPT-5.6-Terra | Complex reasoning |

### Dynamic Selection

```python
def pick_llm(level: str):
    if level == "low":
        return ChatOpenAI(model_name="gpt-5.6-luna", temperature=0)
    elif level == "medium":
        return ChatOllama(model="gemma4:e4b", temperature=0)
    elif level == "high":
        return ChatOpenAI(model="gpt-5.6-terra", temperature=0)
```
