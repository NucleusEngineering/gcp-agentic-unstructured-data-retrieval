# How the Nelly Hackathon Agent Works

This document breaks down the key components of the agent, explaining how it understands user questions, searches for information, and generates answers.

## 1. Overview

The agent is built using the **Google Agent Development Kit (ADK)**. It follows a simple but powerful pattern:

1.  The user's question is given to a Large Language Model (LLM).
2.  The LLM is instructed to **always** use a `search_knowledge_base` tool to find information.
3.  The tool queries a **Vertex AI Search** datastore containing your private documents (the "Nelly Hackathon Proposal" and "Shopping cart" PDFs).
4.  The search results are returned to the LLM as context.
5.  The LLM uses this context to generate a final, user-facing answer.

This ensures the agent's knowledge is strictly limited to the documents you have provided.

---

## 2. Key Files & Code Snippets

### a. Entrypoint: `main.py`

This file is responsible for starting the application. When run in `chat` mode, it initializes and runs the ADK's interactive chat loop.

-   **What it does:** It uses the `InMemoryRunner` from the ADK, which is a simple way to run an agent locally for testing and development. It passes our agent's configuration to the runner and starts an asynchronous chat session that handles user input.

```python
# main.py

import asyncio
from google.adk.runners import InMemoryRunner
from src.agents.adk_agent import agent_config
# ... other imports

def run_chat_mode():
    logger.info("Initializing ADK Chat...")
    print("--- Nelly ADK Chatbot ---")
    print("Type 'exit' to quit.")
    
    # 1. The runner is initialized with our agent's configuration
    runner = InMemoryRunner(agent=agent_config)
    
    # 2. An async chat loop is started to handle user input
    async def chat():
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            # 3. The runner's run_debug method processes the input
            await runner.run_debug(user_input)

    asyncio.run(chat())
```

### b. Agent Configuration: `src/agents/adk_agent.py`

This file defines the agent's core identity, including its instructions, the LLM it uses, and the tools it has access to.

-   **What it does:** It creates an `Agent` configuration object. The `instruction` parameter is the most critical part, as it tells the model *how* to behave. It explicitly instructs the model to use the `search_knowledge_base` tool before answering any questions.

```python
# src/agents/adk_agent.py

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from src.agents.tools import search_knowledge_base
from google.generativeai import types

# 1. The system prompt defines the agent's rules and persona
system_prompt = """You are a helpful AI assistant for the Nelly Hackathon.
Your knowledge comes exclusively from the "search_knowledge_base" tool.
ALWAYS use the tool to find information before answering.
If the user asks about "Nelly", "proposals", or "hackathons", search first."""

# 2. The Gemini model is configured
model_config = Gemini(
    model="gemini-2.0-flash-lite",
)

# 3. The final agent configuration is assembled
agent_config = Agent(
    name="nelly_agent",
    model=model_config,
    instruction=system_prompt,
    generate_content_config=types.GenerationConfig(temperature=0),
    tools=[search_knowledge_base], # The search tool is attached here
)
```

### c. Tool Definition: `src/agents/tools.py`

This file defines the `search_knowledge_base` tool that the agent uses. The ADK framework automatically makes this function available to the LLM.

-   **What it does:** It defines a simple Python function that takes a `query` string. The function's docstring is very important, as it's what the LLM reads to understand what the tool does. The function then calls our `VertexSearchClient` to perform the actual search.

```python
# src/agents/tools.py

from google.adk.tools.function_tool import FunctionTool
from src.search.vertex_client import VertexSearchClient
# ... other imports

search_client = VertexSearchClient()

def _search_knowledge_base(query: str) -> str:
    """
    Searches the Nelly Hackathon knowledge base to find information and answer user questions.

    Args:
        query: A detailed search query crafted from the user's question.
    """
    logger.info(f"Tool call: search_knowledge_base with query: {query}")
    return search_client.search(query)

# The function is wrapped in a FunctionTool object for the ADK
search_knowledge_base = FunctionTool(func=_search_knowledge_base)
```

### d. Search Client: `src/search/vertex_client.py`

This is the lowest-level component, responsible for communicating with the Google Cloud Vertex AI Search API.

-   **What it does:** It constructs a search request using the user's query and sends it directly to your specific **Data Store**. By targeting the datastore directly (instead of a broader "Engine"), we ensure that the search is strictly limited to the documents you have ingested. It then processes the response to extract the most relevant snippets or paragraphs.

```python
# src/search/vertex_client.py

class VertexSearchClient:
    def __init__(self):
        # ... initialization ...
        
        # 1. The serving_config path is built to target the specific data store
        self.serving_config = self.search_client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_config",
        )
        # ...

    def search(self, query: str) -> str:
        # ...
            # 2. The request is created with the datastore-specific serving_config
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=5,
                content_search_spec=content_search_spec,
            )
            # 3. The search client sends the request
            response = self.search_client.search(request)

            # 4. The response is processed to extract text snippets
            context_snippets = []
            for result in response.results:
                # ... logic to extract content ...
            
            consolidated_context = "\n\n".join(context_snippets)
            return consolidated_context if consolidated_context else "No relevant documents found."
```