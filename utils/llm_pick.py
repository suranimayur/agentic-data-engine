"""
LLM Provider Selector
=====================
Provides a unified interface to select between different LLM providers
(OpenAI and Ollama) based on task complexity levels.

Usage:
    from utils.llm_pick import pick_llm
    llm = pick_llm("medium")  # Returns ChatOllama with gemma4:e4b
"""

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

# Load environment variables from .env file (OPENAI_API_KEY, etc.)
load_dotenv()


def pick_llm(level: str):
    """
    Select an LLM provider based on the task complexity level.

    This function implements a cost-performance optimization strategy:
    - "low":    Fast & cheap models for simple tasks (routing, classification, safety checks)
    - "medium": Balanced local models for code generation (zero API cost)
    - "high":   Most capable models for complex reasoning tasks

    Args:
        level (str): The complexity level. Must be "low", "medium", or "high".

    Returns:
        ChatOpenAI | ChatOllama: A configured LangChain chat model instance.

    Raises:
        ValueError: If an invalid level is provided.

    Examples:
        >>> llm = pick_llm("low")     # GPT-5.6-Luna (OpenAI, fast)
        >>> llm = pick_llm("medium")  # Gemma4:e4b (Ollama, local)
        >>> llm = pick_llm("high")    # GPT-5.6-Terra (OpenAI, powerful)
    """
    if level.lower() == "low":
        return ChatOpenAI(
            model_name="gpt-5.6-luna",
            temperature=0,
            reasoning_effort="none",
        )
    elif level.lower() == "medium":
        return ChatOllama(
            model="gemma4:e4b",
            temperature=0,
        )
    elif level.lower() == "high":
        return ChatOpenAI(
            model="gpt-5.6-terra",
            temperature=0,
        )
    else:
        raise ValueError(
            f"Invalid level '{level}'. Choose from 'low', 'medium', or 'high'."
        )


if __name__ == "__main__":
    # Quick test: invoke the medium-tier LLM with a simple question
    llm_obj = pick_llm("medium")
    response = llm_obj.invoke("Hello, what is the capital city of Mongolia?")
    print(response.content)
