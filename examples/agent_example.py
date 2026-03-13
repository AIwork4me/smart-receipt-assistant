#!/usr/bin/env python
"""
Agent Usage Example for Smart Receipt Assistant

This script demonstrates how to use the LangChain Agent for
intelligent receipt processing.

Usage:
    uv run python examples/agent_example.py
"""

import os
import json
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import create_receipt_agent


def example_agent_basic():
    """Basic agent usage example."""
    print("=" * 60)
    print("Example 1: Basic Agent Usage")
    print("=" * 60)

    # Create the agent
    print("\nCreating receipt agent...")
    agent = create_receipt_agent(verbose=True)

    # Find a sample invoice
    sample_dir = Path(__file__).parent.parent / "examples" / "sample_invoices"
    sample_files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.jpg"))

    if not sample_files:
        print("No sample files found. Please add sample invoices to examples/sample_invoices/")
        return

    sample_file = str(sample_files[0])
    print(f"\nProcessing: {sample_file}")

    # Process receipt using the agent
    print("\nInvoking agent...")
    try:
        result = agent.process(sample_file)
        print("\nAgent Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(f"Agent Error: {e}")


def example_agent_with_custom_llm():
    """Example using a custom LLM with the agent."""
    print("\n" + "=" * 60)
    print("Example 2: Agent with Custom LLM")
    print("=" * 60)

    from langchain_openai import ChatOpenAI

    # Create a custom LLM (e.g., using a different model)
    # Note: Replace with your actual LLM configuration
    try:
        custom_llm = ChatOpenAI(
            model="gpt-4",  # or your preferred model
            temperature=0.1,
        )

        # Create agent with custom LLM
        agent = create_receipt_agent(
            llm=custom_llm,
            verbose=True
        )

        print("Agent created with custom LLM")

    except Exception as e:
        print(f"Could not create custom LLM: {e}")
        print("Skipping this example...")


def example_agent_natural_language():
    """Example using natural language queries with the agent."""
    print("\n" + "=" * 60)
    print("Example 3: Natural Language Queries")
    print("=" * 60)

    # Create agent
    agent = create_receipt_agent(verbose=True)

    # Example natural language queries
    queries = [
        "Please process this invoice and tell me the total amount",
        "What type of receipt is this?",
        "Extract all the information from this receipt",
    ]

    # Find a sample invoice
    sample_dir = Path(__file__).parent.parent / "examples" / "sample_invoices"
    sample_files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.jpg"))

    if not sample_files:
        print("No sample files found.")
        return

    sample_file = str(sample_files[0])

    print(f"\nUsing file: {sample_file}")
    print("\nNote: The agent will use tools to process the request intelligently")

    for query in queries:
        print(f"\n--- Query: {query} ---")
        full_query = f"{query} File: {sample_file}"

        try:
            result = agent.invoke(full_query)
            output = result.get("output", "No output")
            print(f"Response: {output[:500]}..." if len(output) > 500 else f"Response: {output}")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Smart Receipt Assistant - Agent Usage Examples")
    print("=" * 60)

    # Check for API keys
    if not os.getenv("PADDLEOCR_ACCESS_TOKEN"):
        print("\nWarning: PADDLEOCR_ACCESS_TOKEN not set. OCR will fail.")

    if not os.getenv("AISTUDIO_API_KEY"):
        print("Warning: AISTUDIO_API_KEY not set. Agent will not work properly.")

    # Run examples
    example_agent_basic()
    example_agent_natural_language()

    print("\n" + "=" * 60)
    print("Agent examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
