"""
Data Agent — Top-Level Orchestrator
====================================
Routes user questions to the appropriate sub-agent (SQL or ETL)
based on LLM-based intent classification.

Graph Flow:
    START -> router_node -> route_edge -> [sql_node | etl_node] -> END

The router uses structured output (RouterSchema) to classify each
question as either "sql" or "etl", then dispatches accordingly.
"""

from langchain_core.messages import HumanMessage
import os
import sys

# Ensure project root is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_pick import pick_llm
from Models.schema import RouterSchema, DataAgentSchema
from langgraph.graph import StateGraph, START, END
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import sql_analyst


# ---------------------------------------------------------------------------
# Initialize LLM router with structured output
# ---------------------------------------------------------------------------

_llm = pick_llm("medium")
llm_router = _llm.with_structured_output(RouterSchema)


# ---------------------------------------------------------------------------
# Node: Router — Classify user intent
# ---------------------------------------------------------------------------

def router_node(state: DataAgentSchema) -> dict:
    """
    Classify the user's question as SQL or ETL using the LLM router.

    Extracts the last message from the conversation and uses structured
    output to get a deterministic classification.
    """
    message = state.messages[-1].content
    route_response = llm_router.invoke(message).model_dump()
    return {"route_response": route_response["answer"]}


# ---------------------------------------------------------------------------
# Node: ETL — Delegate to ETL Analyst sub-agent
# ---------------------------------------------------------------------------

def etl_node(state: DataAgentSchema) -> dict:
    """Delegate the question to the ETL Analyst agent."""
    message = state.messages[-1].content
    response = etl_analyst.invoke(
        {"messages": [HumanMessage(content=message)]}
    )
    return {"messages": state.messages + [response]}


# ---------------------------------------------------------------------------
# Node: SQL — Delegate to SQL Analyst sub-agent
# ---------------------------------------------------------------------------

def sql_node(state: DataAgentSchema) -> dict:
    """Delegate the question to the SQL Analyst agent."""
    message = state.messages[-1].content

    input_schema = {
        "messages": [],
        "user_question": message,
        "curated_question": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe_sql": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": "",
    }

    response = sql_analyst.invoke(input_schema)
    return {"messages": state.messages + [response]}


# ---------------------------------------------------------------------------
# Conditional Edge: Route based on classification
# ---------------------------------------------------------------------------

def route_edge(state: DataAgentSchema) -> str:
    """
    Route to the appropriate sub-agent based on the router's classification.

    Returns:
        str: "sql_node" or "etl_node" depending on the route_response.
    """
    route = state.route_response.lower()
    if route == "sql":
        return "sql_node"
    elif route == "etl":
        return "etl_node"
    else:
        raise ValueError(f"Invalid router response: {state.route_response}")


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

data_agent_graph = StateGraph(DataAgentSchema)

# Nodes
data_agent_graph.add_node("router_node", router_node)
data_agent_graph.add_node("etl_node", etl_node)
data_agent_graph.add_node("sql_node", sql_node)

# Edges
data_agent_graph.add_edge(START, "router_node")
data_agent_graph.add_conditional_edges(
    "router_node",
    route_edge,
    {"etl_node": "etl_node", "sql_node": "sql_node"},
)
data_agent_graph.add_edge("etl_node", END)
data_agent_graph.add_edge("sql_node", END)

# Compile the graph
data_agent = data_agent_graph.compile()


# ---------------------------------------------------------------------------
# Standalone execution for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from IPython.display import Image

    # Generate and save the graph visualization
    img = Image(data_agent.get_graph().draw_mermaid_png())
    with open("data_agent_graph.png", "wb") as f:
        f.write(img.data)

    # Test with a sample question
    response = data_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content="I want to extract data from API endpoint "
                    "https://pokeapi.co/api/v2/pokemon/ and save it "
                    "to data/extract folder in csv format."
                )
            ],
            "route_response": "",
        }
    )
    print(response)
