"""
Scratchpad — Experimentation & Testing
=======================================
Quick test script for validating the SQL safety judge.
Run this file to test the judge with a sample SQL query.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_pick import pick_llm
from Models.schema import JudgeSchema


def test_sql_judge(sql_query: str):
    """
    Test the SQL safety judge with a given query.

    Args:
        sql_query: The SQL query to evaluate for safety.
    """
    llm = pick_llm("medium")
    llm_judge = llm.with_structured_output(JudgeSchema)

    prompt = f"""You are SQL Judge for Security. Evaluate the safety of this SQL query.
Rules:
- Query should ONLY be for data retrieval (SELECT).
- Must NOT contain data manipulation commands (INSERT, UPDATE, DELETE, DROP, ALTER).
- Must NOT have SQL injection vulnerabilities.
- If safe, respond with "Yes". If unsafe, respond with "No".
- Provide a comment explaining your decision.

SQL Query to evaluate:
{sql_query}
"""
    response = llm_judge.invoke(prompt).model_dump()
    return response


if __name__ == "__main__":
    # Test with a safe query
    test_query = "SELECT * FROM users WHERE age > 30;"
    result = test_sql_judge(test_query)
    print(f"Query: {test_query}")
    print(f"Safe: {result['answer']}")
    print(f"Comment: {result['comment']}")
