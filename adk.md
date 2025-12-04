Here is a comprehensive guide to the Google Agent Development Kit (ADK). You can feed this directly into your CLI or use it as a context file (e.g., `docs/adk_framework_guide.md`) to ground your coding assistant in the specific patterns and best practices of the framework.

***

# Google Agent Development Kit (ADK) Framework Guide

## 1. Overview
The **Agent Development Kit (ADK)** is Google's modular, open-source framework designed to simplify the end-to-end development of intelligent AI agents. Unlike simple LLM wrappers, ADK provides a structured approach to building production-ready systems that can reason, act, and persist state.

It is designed to be **model-agnostic** (optimized for Gemini/Vertex AI but supports others via LiteLLM) and **deployment-agnostic** (run locally, on Cloud Run, or Vertex AI Agent Engine).

## 2. Core Architecture
ADK decouples the agent's components to ensure modularity and testability.

### 2.1. Key Components
*   **Agents:** The "brains" that handle reasoning and orchestration. They do not execute code themselves but decide *which* tools to call.
*   **Tools:** The "hands" of the agent. These are deterministic Python functions that interact with the outside world (APIs, databases, search).
*   **Memory/State:** Manages the context of the conversation. ADK handles session state automatically, allowing agents to remember past interactions.
*   **Runtimes:** The execution environment that manages the agent lifecycle (e.g., a local CLI loop, a FastAPI server, or the Vertex AI Agent Engine).

## 3. Best Practices for Agent Development

### 3.1. Tool Definition (The "Contract")
The quality of an agent depends heavily on how tools are defined. The LLM uses the function signature and docstring to understand *when* and *how* to use a tool.

*   **Descriptive Naming:** Use `verb_noun` syntax (e.g., `search_knowledge_base` is better than `search` or `get_data`).
*   **Type Hinting:** **Mandatory**. You must type-hint all arguments and return values (e.g., `def calculate_tax(amount: float) -> float:`).
*   **Docstrings:** Write clear, concise docstrings describing what the tool does and what the arguments represent. This is the "prompt" the model sees for the tool.

### 3.2. Agent Design Patterns
*   **Single Responsibility:** Avoid creating one "God Agent" that does everything. If an agent needs to handle Billing, Tech Support, and Sales, break it down into three specialized agents and use a routing mechanism.
*   **Separation of Logic:** Keep your `agent.py` (definition) separate from your `main.py` (runtime/entry point).
*   **Sequential Execution:** For mutative actions (creating tickets, sending emails), force sequential execution to prevent race conditions.

## 4. Recommended Project Structure
Adopt this standard structure to keep your project compatible with ADK tooling and easy to navigate.

```text
project_root/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── support_agent.py    # Specialized agent logic
│   │   └── tools.py            # Tools specific to this agent
│   ├── shared/
│   │   └── utils.py            # Shared utilities (logger, config)
├── main.py                     # CLI Entry point / Runtime
├── requirements.txt
└── .env                        # Environment variables (API Keys, Project ID)
```

## 5. Implementation Reference (Python)

Below is a canonical example of defining an agent and a tool using ADK patterns.

### 5.1. Defining a Tool (`src/agents/tools.py`)

```python
from typing import Dict

def search_product_database(product_name: str, category: str = "general") -> Dict[str, str]:
    """
    Searches the internal product database for details and availability.
    
    Args:
        product_name: The fuzzy name of the product to find (e.g., "Pixel 9").
        category: Optional category filter (e.g., "electronics", "clothing").
        
    Returns:
        A dictionary containing product details, price, and stock status.
    """
    # [Simulated Logic]
    return {
        "name": product_name,
        "price": "799.99",
        "stock": "In Stock",
        "category": category
    }
```

### 5.2. Defining the Agent (`src/agents/support_agent.py`)

```python
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Tool
from src.agents.tools import search_product_database

class SupportAgent:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        # 1. Initialize Vertex AI
        vertexai.init()
        
        # 2. Wrap functions as Tools
        self.tools = Tool.from_function(search_product_database)
        
        # 3. Initialize Model with Tools
        self.model = GenerativeModel(
            model_name,
            tools=[self.tools],
        )
        
        # 4. Start Chat Session (Memory)
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def ask(self, user_query: str) -> str:
        """Sends a query to the agent and returns the natural language response."""
        response = self.chat.send_message(user_query)
        return response.text
```

### 5.3. The Runtime / CLI (`main.py`)

```python
import os
from src.agents.support_agent import SupportAgent

def main():
    agent = SupportAgent()
    print("🤖 Agent Ready! (Type 'exit' to quit)")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        try:
            response = agent.ask(user_input)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

## 6. Testing & Debugging
*   **Local CLI:** Always build a simple CLI loop (like above) to test the "conversation flow" before deploying to a web UI.
*   **Logging:** Inspect the raw `response.candidates` to see if the model *attempted* to call a tool but failed (e.g., due to missing arguments).
*   **Safety Settings:** Be aware that default safety settings might block certain responses. You may need to adjust `safety_settings` in the `GenerativeModel` config for enterprise use cases.