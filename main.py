"""
Intelligent Multi-Agent Data Engineering Platform — Entry Point
===============================================================
Invokes the top-level data agent with a user question.
The agent routes the question to either the SQL Analyst
or ETL Analyst sub-agent based on intent classification.
"""

from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage


def main():
    """Run the data agent with a sample user question."""
    response = data_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "I want to extract the data from the API endpoint "
                        "'https://pokeapi.co/api/v2/pokemon' and save it "
                        "to data/extract folder in csv format."
                    )
                )
            ],
            "route_response": "",
        }
    )
    print(response)


if __name__ == "__main__":
    main()
