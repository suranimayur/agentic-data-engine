"""
SQL Analyst Agent
=================
A 7-node LangGraph agent that converts natural language questions into
safe, executed SQL queries against a PostgreSQL database.

Pipeline Flow:
    START -> curate_question -> prompt_query_context -> generate_sql_query
    -> is_safe_sql -> [execute_sql_query | cancelled_sql]
    -> represent_final_answer -> END

Key Features:
    - Question curation: Refines user input for better SQL generation
    - Schema injection: Fetches actual DB schema for accurate queries
    - Safety validation: Judge agent blocks dangerous SQL (DROP, DELETE, etc.)
    - Answer formatting: Converts raw results into human-readable responses
"""

from langchain_core.messages import HumanMessage, AIMessage
import os
import sys
from langgraph.graph import StateGraph, START, END

# Ensure project root is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_pick import pick_llm
from Models.schema import AgentSchema, JudgeSchema
from utils.database import DatabaseUtil


# ---------------------------------------------------------------------------
# Helper: Build PostgreSQL connection details from environment variables
# ---------------------------------------------------------------------------

def _get_db_connection() -> dict:
    """Build PostgreSQL connection config from environment variables."""
    return {
        "host": os.environ["host"],
        "port": os.environ["port"],
        "user": os.environ["user"],
        "password": os.environ["password"],
        "database": os.environ["database"],
    }


# ---------------------------------------------------------------------------
# Node 1: Curate Question
# ---------------------------------------------------------------------------

def curate_question(state: AgentSchema) -> AgentSchema:
    """
    Refine the user's natural language question for SQL generation.

    Uses the LLM to transform vague or informal questions into clear,
    specific queries that can be accurately converted to SQL.
    """
    llm = pick_llm("low")
    response = llm.invoke(
        f"Curate the following question for SQL query generation: "
        f"{state.user_question}"
    ).content

    state.curated_question = response
    state.messages = state.messages + [
        HumanMessage(content=f"Curated Question: {state.curated_question}")
    ]
    return state


# ---------------------------------------------------------------------------
# Node 2: Build Prompt with DB Context
# ---------------------------------------------------------------------------

def prompt_query_context(state: AgentSchema) -> AgentSchema:
    """
    Build a comprehensive prompt that includes the database schema.

    This is the RAG-like pattern: the LLM receives actual database
    structure (table names, columns, data types, sample data) as context
    so it can generate accurate SQL queries.
    """
    conn_details = _get_db_connection()
    obj = DatabaseUtil(conn_details)
    schema_info = obj.schema_details("public")

    prompt = (
        "You are an SQL analyst agent. Your task is to convert the user's natural "
        "language query into Postgres SQL query that can be executed on the database. "
        "You are provided with the user's original query and the schema details of the "
        "database, including table names, column names, data types, and sample data for "
        "each table so that you can understand the structure of the database and generate "
        "an accurate SQL query.\n"
        "Unless the user explicitly asks for a specific number of rows, always limit the "
        "output to 10 rows.\n"
        "Note - Just generate the SQL query without any explanation or additional text "
        "because this query will be executed directly on the database. The output should "
        "be SQL ready to be executed without any modifications.\n\n"
        f"Original query: {state.curated_question}\n\n"
        f"Database schema:\n{schema_info}"
    )

    state.prompt_query_context = prompt
    return state


# ---------------------------------------------------------------------------
# Node 3: Generate SQL Query
# ---------------------------------------------------------------------------

def generate_sql_query(state: AgentSchema) -> AgentSchema:
    """Generate a SQL query from the curated question and schema context."""
    llm = pick_llm("low")
    generated_sql = (llm.invoke(state.prompt_query_context).content or "").strip()
    state.generated_sql_query = generated_sql
    return state


# ---------------------------------------------------------------------------
# Node 4: SQL Safety Validation
# ---------------------------------------------------------------------------

def is_safe_sql(state: AgentSchema) -> AgentSchema:
    """
    Validate the generated SQL query for safety using a judge agent.

    Checks for data manipulation commands, SQL injection, and malicious patterns.
    Uses structured output (JudgeSchema) for deterministic Yes/No answers.
    """
    llm = pick_llm("low")
    llm_judge = llm.with_structured_output(JudgeSchema)

    prompt = f"""You are SQL Judge for Security. Evaluate the safety of this SQL query.
Rules:
- Query should ONLY be for data retrieval (SELECT).
- Must NOT contain data manipulation commands (INSERT, UPDATE, DELETE, DROP, ALTER).
- Must NOT have SQL injection vulnerabilities.
- If safe, respond with "Yes". If unsafe, respond with "No".
- Provide a comment explaining your decision.

SQL Query to evaluate:
{state.generated_sql_query}
"""

    response = llm_judge.invoke(prompt).model_dump()
    state.is_safe_sql = response["answer"]
    state.comments = response["comment"]
    return state


# ---------------------------------------------------------------------------
# Node 5a: Handle Unsafe SQL
# ---------------------------------------------------------------------------

def cancelled_sql(state: AgentSchema) -> AgentSchema:
    """Handle rejected SQL queries (deemed unsafe by the judge)."""
    state.final_answer = "The generated SQL query is deemed unsafe."
    state.messages = state.messages + [
        AIMessage(content=f"Final Answer: {state.final_answer}")
    ]
    return state


# ---------------------------------------------------------------------------
# Node 5b: Execute SQL Query
# ---------------------------------------------------------------------------

def execute_sql_query(state: AgentSchema) -> AgentSchema:
    """Execute the validated SQL query against PostgreSQL."""
    conn_details = _get_db_connection()
    obj = DatabaseUtil(conn_details)
    execution_result = obj.execute_sql(state.generated_sql_query)
    state.sql_query_execution_result = execution_result
    return state


# ---------------------------------------------------------------------------
# Node 6: Format Final Answer
# ---------------------------------------------------------------------------

def represent_final_answer(state: AgentSchema) -> AgentSchema:
    """
    Convert raw SQL results into a human-readable response.

    Uses the LLM to interpret query results and provide a clear,
    concise answer that directly addresses the user's original question.
    """
    llm = pick_llm("low")

    prompt = f"""You are an SQL analyst agent. Provide a final answer based on the
SQL query execution result. Your response should be clear, concise, and
directly address the user's original question.

Original user question: {state.user_question}

Curated question: {state.curated_question}

SQL query execution result: {state.sql_query_execution_result}
"""
    llm_response = llm.invoke(prompt).content
    state.final_answer = llm_response
    state.messages = state.messages + [
        AIMessage(content=f"Final Answer: {state.final_answer}")
    ]
    return state


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

sql_agent_graph = StateGraph(AgentSchema)

# Register all nodes
sql_agent_graph.add_node("curate_question", curate_question)
sql_agent_graph.add_node("prompt_query_context", prompt_query_context)
sql_agent_graph.add_node("generate_sql_query", generate_sql_query)
sql_agent_graph.add_node("is_safe_sql", is_safe_sql)
sql_agent_graph.add_node("cancelled_sql", cancelled_sql)
sql_agent_graph.add_node("execute_sql_query", execute_sql_query)
sql_agent_graph.add_node("represent_final_answer", represent_final_answer)

# Linear flow for the first 4 nodes
sql_agent_graph.add_edge(START, "curate_question")
sql_agent_graph.add_edge("curate_question", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql_query")
sql_agent_graph.add_edge("generate_sql_query", "is_safe_sql")


# Conditional edge: route based on safety validation
def is_safe_sql_edge(state: AgentSchema) -> str:
    """Route to execution if safe, or cancellation if unsafe."""
    return "execute_sql_query" if state.is_safe_sql.lower() == "yes" else "cancelled_sql"


sql_agent_graph.add_conditional_edges(
    "is_safe_sql",
    is_safe_sql_edge,
    {
        "execute_sql_query": "execute_sql_query",
        "cancelled_sql": "cancelled_sql",
    },
)

# Terminal edges
sql_agent_graph.add_edge("cancelled_sql", END)
sql_agent_graph.add_edge("execute_sql_query", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer", END)

# Compile the graph into a runnable agent
sql_analyst = sql_agent_graph.compile()


# ---------------------------------------------------------------------------
# Standalone execution for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from IPython.display import Image

    # Generate and save the graph visualization
    img = Image(sql_analyst.get_graph().draw_mermaid_png())
    with open("sql_analyst_graph.png", "wb") as f:
        f.write(img.data)

    # Test with a sample question
    input_schema = {
        "user_question": "What are the different types of payment methods we have in the database?",
    }

    sql_analyst_response = sql_analyst.invoke(input_schema)

    print("=== Messages ===")
    print(sql_analyst_response["messages"])
    print("\n=== Generated SQL ===")
    print(sql_analyst_response["generated_sql_query"])
    print("\n=== Execution Result ===")
    print(sql_analyst_response["sql_query_execution_result"])
    print("\n=== Final Answer ===")
    print(sql_analyst_response["final_answer"])
