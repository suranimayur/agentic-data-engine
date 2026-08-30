"""
ETL Analyst Agent
=================
A tool-calling LangGraph agent that handles data extraction,
transformation, and loading operations.

Graph Flow:
    START -> llm_node -> is_tool_call? -> [tool_node -> llm_node (loop) | END]

Key Features:
    - extract_load_tool: Fetch data from REST APIs
    - transform_load_tool: Generate and execute pandas code dynamically
    - Tool loop: LLM decides when to call tools and when to stop
"""

from langchain_core.messages import HumanMessage
import os
import sys
import re

# Ensure project root is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from Models.schema import ETLAgentSchema
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool


# ---------------------------------------------------------------------------
# Tool 1: Extract & Load from API
# ---------------------------------------------------------------------------

@tool
def extract_load_tool(url: str, output_folder: str, format: str) -> str:
    """
    Extract data from a REST API endpoint and save to a local file.

    Args:
        url: The API endpoint URL to fetch data from.
        output_folder: The folder where extracted data will be saved.
        format: Output format — "csv", "json", or "parquet".

    Returns:
        Success or error message.
    """
    etl_tools = ETLTools()
    return etl_tools.extract_load(url, output_folder, format)


# ---------------------------------------------------------------------------
# Tool 2: Transform & Load with LLM-generated pandas code
# ---------------------------------------------------------------------------

@tool
def transform_load_tool(
    input_file_path: str,
    output_folder: str,
    output_format: str,
    user_question: str,
) -> str:
    """
    Transform data using LLM-generated pandas code.

    Reads the input file, provides sample data to the LLM for context,
    generates appropriate transformation code, and executes it.

    Args:
        input_file_path: Path to the input data file.
        output_folder: Directory where transformed data will be saved.
        output_format: Output format — "csv", "json", or "parquet".
        user_question: Natural language description of the transformation.

    Returns:
        Summary of the transformation including the executed code.
    """
    etl_tools = ETLTools()

    # Get sample data for LLM context
    top_3_rows = etl_tools.transform_load_context(input_file_path)

    # Generate pandas code using the LLM
    llm = pick_llm("medium")
    prompt = f"""You are a Python data analyst who uses pandas to analyze data.
Provide ONLY the pandas code — no explanations or comments.

Create a pandas DataFrame from: {input_file_path}
Save the transformed data to: {output_folder}

User's transformation request: {user_question}

Data context (first 3 rows):
{top_3_rows}
"""
    response = llm.invoke(prompt).content

    # Clean markdown code fences from LLM response
    pandas_code = response.strip()
    pandas_code = re.sub(r"^```(?:python)?\s*", "", pandas_code)
    pandas_code = re.sub(r"\s*```$", "", pandas_code).strip()

    # Execute the generated code
    result = etl_tools.execute_code(pandas_code)

    return (
        f"Data transformed and saved to {output_folder} in {output_format}.\n\n"
        f"Pandas code executed:\n{pandas_code}\n\n"
        f"Execution result: {result}"
    )


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

tools = [extract_load_tool, transform_load_tool]

# Bind tools to the LLM so it can decide when to call them
_llm = pick_llm("medium")
llm_bind = _llm.bind_tools(tools)


# ---------------------------------------------------------------------------
# Node: LLM — Decide next action (tool call or final answer)
# ---------------------------------------------------------------------------

def llm_node(state: ETLAgentSchema) -> dict:
    """
    Invoke the LLM with the conversation history.

    The LLM decides whether to:
    - Call a tool (returns tool_calls in the response)
    - Provide a final answer (no tool_calls)
    """
    system_message = SystemMessage(
        content=(
            "You are a Python data analyst with access to tools that can "
            "extract and transform/load data. Use the appropriate tool based "
            "on the user's question. Once the operation is complete, inform "
            "the user and end the conversation."
        )
    )
    response = llm_bind.invoke([system_message] + state.messages)
    return {"messages": [response]}


# ---------------------------------------------------------------------------
# Node: Tool — Execute requested tools
# ---------------------------------------------------------------------------

def tool_node(state: ETLAgentSchema) -> dict:
    """
    Execute all tool calls requested by the LLM.

    Maps tool call names to actual tool functions, invokes each one,
    and returns the results as ToolMessage objects.
    """
    tools_by_name = {t.name: t for t in tools}
    tool_calls = state.messages[-1].tool_calls

    results = []
    for tool_call in tool_calls:
        selected_tool = tools_by_name[tool_call["name"]]
        observation = selected_tool.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=observation, tool_call_id=tool_call["id"])
        )

    return {"messages": results}


# ---------------------------------------------------------------------------
# Conditional Edge: Continue tool loop or finish
# ---------------------------------------------------------------------------

def is_tool_call(state: ETLAgentSchema) -> str:
    """Check if the LLM wants to call more tools."""
    tool_calls = state.messages[-1].tool_calls
    return "tool_node" if tool_calls else "end"


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

etl_analyst_graph = StateGraph(ETLAgentSchema)

# Nodes
etl_analyst_graph.add_node("llm_node", llm_node)
etl_analyst_graph.add_node("tool_node", tool_node)

# Edges
etl_analyst_graph.add_edge(START, "llm_node")
etl_analyst_graph.add_conditional_edges(
    "llm_node",
    is_tool_call,
    {"tool_node": "tool_node", "end": END},
)
etl_analyst_graph.add_edge("tool_node", "llm_node")  # Loop back after tools

# Compile the graph
etl_analyst = etl_analyst_graph.compile()


# ---------------------------------------------------------------------------
# Standalone execution for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from IPython.display import Image

    # Generate and save the graph visualization
    img = Image(etl_analyst.get_graph().draw_mermaid_png())
    with open("etl_analyst_graph.png", "wb") as f:
        f.write(img.data)

    # Test with a sample extraction request
    response = etl_analyst.invoke(
        {
            "messages": [
                HumanMessage(
                    content="I want to extract data from API endpoint "
                    "https://pokeapi.co/api/v2/pokemon/ and save it "
                    "to data/extract folder in csv format."
                )
            ]
        }
    )
    print(response)
