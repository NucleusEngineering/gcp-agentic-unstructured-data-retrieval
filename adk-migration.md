Here is a migration guide (`migrate_to_adk.md`) to help you transition your custom Vertex AI SDK implementation to the **Google Agent Development Kit (ADK)** framework.

This guide assumes you want to keep your existing "Enterprise Search" fix but leverage ADK for orchestration, state management, and structure.

-----

````markdown
# Migration Guide: Custom SDK to Google ADK

## Overview
This document outlines the steps to migrate the current "Nelly Hackathon" agent from a raw `vertexai` SDK implementation to the **Google Agent Development Kit (ADK)**.

**Goal:** Replace manual loop orchestration and tool definitions with ADK's managed runtime, while preserving the custom Vertex AI Search logic.

## Phase 1: Installation & Setup

First, add the ADK library to your project. Note that ADK requires Python 3.10+.

```bash
poetry add google-adk
````

## Phase 2: Adapt the Tools (`src/agents/tools.py`)

In your current setup, you manually define `Tool` objects in the agent class. In ADK, you decorate functions to make them discoverable.

**Action:** Update `src/agents/tools.py` to use the `@adk.tool` decorator.

```python
# src/agents/tools.py (Migrated)
from google.adk import tool
from src.search.vertex_client import VertexSearchClient

# Initialize the client once (global or singleton pattern recommended)
search_client = VertexSearchClient()

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the Nelly Hackathon knowledge base to find information and answer user questions.
    
    Args:
        query: A detailed search query crafted from the user's question.
    """
    # We reuse your existing, fixed VertexSearchClient logic!
    return search_client.search(query)
```

*Note: You do not need to change `src/search/vertex_client.py`. Your Enterprise Edition logic stays exactly the same.*

## Phase 3: Create the ADK Agent (`src/agents/adk_agent.py`)

Instead of your custom `RAGAgent` class that manages history and loops manually, you will define an ADK Agent. This handles memory and model connections automatically.

**Action:** Create a new file `src/agents/adk_agent.py`.

```python
# src/agents/adk_agent.py
import os
from google.adk import Agent, Model
from src.agents.tools import search_knowledge_base

def create_nelly_agent():
    # 1. Define the Model Configuration
    # ADK abstracts the specific provider (Gemini, etc.)
    model = Model(
        model_name="gemini-2.0-flash-lite",
        parameters={
            "temperature": 0,  # Low temperature for factual RAG
        }
    )

    # 2. Define the System Instruction
    system_prompt = """You are a helpful AI assistant for the Nelly Hackathon.
    Your knowledge comes exclusively from the "search_knowledge_base" tool.
    ALWAYS use the tool to find information before answering.
    If the user asks about "Nelly", "proposals", or "hackathons", search first."""

    # 3. Initialize the Agent
    agent = Agent(
        model=model,
        system_instruction=system_prompt,
        tools=[search_knowledge_base], # Pass the decorated function directly
        # ADK handles chat history (Session) automatically
    )
    
    return agent
```

## Phase 4: Update the Entrypoint (`main.py`)

You can now delete the complex `while` loop and tool execution logic from your `main.py`. ADK provides a runner.

**Action:** Update `main.py` to use the ADK runner.

```python
# main.py (Migrated)
import logging
import argparse
from src.agents.adk_agent import create_nelly_agent
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

def run_chat_mode():
    logger.info("Initializing ADK Agent...")
    agent = create_nelly_agent()
    
    print("--- Nelly ADK Chatbot ---")
    print("Type 'exit' to quit.")

    # ADK's built-in convenience loop for testing
    # This replaces your manual 'while True' loop
    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # agent.run() handles the tool calling loop automatically!
            response = agent.run(user_input)
            print(f"\nBot: {response.text}")
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["chat"], default="chat")
    args = parser.parse_args()

    if args.mode == "chat":
        run_chat_mode()
```

## Migration Checklist

1.  [ ] **Install:** `google-adk` installed.
2.  [ ] **Tools:** `search_knowledge_base` decorated with `@tool`.
3.  [ ] **Agent:** `RAGAgent` class replaced with `adk.Agent` configuration.
4.  [ ] **Main:** `main.py` simplified to use `agent.run()`.
5.  [ ] **Verify:** Run `python main.py` and confirm the bot still finds the "Enterprise" answers.

## Key Benefits of this Migration

  * **Less Boilerplate:** No more manual `FunctionDeclaration` JSON schemas.
  * **Auto-Loop:** The `agent.run()` method automatically handles the "Model -\> Tool -\> Output -\> Model" loop.
  * **State:** ADK handles session history automatically (you can swap in Firestore later easily).

<!-- end list -->

```
```