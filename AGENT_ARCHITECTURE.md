# How the Agent Works

This document breaks down the key components of the agent, explaining how it understands user questions, searches for information, and generates answers.

## 1. Overview

The agent is built using the **Google Agent Development Kit (ADK)**. It follows a common pattern:

1.  The user's question is given to a Large Language Model (LLM).
2.  The LLM is instructed to **always** use a `search_knowledge_base` tool to find information.
3.  The tool queries a **Vertex AI Search** datastore containing your private documents.
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
def run_chat_mode():
    logger.info("Initializing ADK Chat...")
    print("--- [APP_NAME] ADK Chatbot ---")
    print("Type 'exit' to quit.")
    
    runner = InMemoryRunner(agent=agent_config)
    
    async def chat():
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            await runner.run_debug(user_input)

    asyncio.run(chat())
```

### b. Agent Configuration: `src/agents/adk_agent.py`

This file defines the agent's core identity, including its instructions, the LLM it uses, and the tools it has access to.

-   **What it does:** It creates an `Agent` configuration object. The `instruction` parameter is an important part, as it tells the model *how* to behave. It explicitly instructs the model to use the `search_knowledge_base` tool before answering any questions.

```python
# src/agents/adk_agent.py
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from src.agents.tools import search_knowledge_base
from google.genai import types

system_prompt = """
# =================================================================================================
# TODO: HACKATHON CHALLENGE (Pillar 1: Completeness) 
# ... (instructions for enhancing the persona) ...
# =================================================================================================

You are a helpful AI assistant.
Your knowledge comes exclusively from the documents provided to you via the "search_knowledge_base" tool.
You must ALWAYS use the "search_knowledge_base" tool to find information before answering any question.
Do not rely on any prior knowledge."""

model_config = Gemini(
    model="gemini-2.0-flash-lite",
)

agent_config = Agent(
    name="[app_name]_agent",
    model=model_config,
    instruction=system_prompt,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[search_knowledge_base],
)
```

### c. Tool Definition: `src/agents/tools.py`

This file defines the `search_knowledge_base` tool that the agent uses. The ADK framework automatically makes this function available to the LLM.

-   **What it does:** It defines a simple Python function that takes a `query` string. The function's docstring is important, as it's what the LLM reads to understand what the tool does. The function then calls our `VertexSearchClient` to perform the actual search.

```python
# src/agents/tools.py
from src.search.vertex_client import VertexSearchClient
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

search_client = VertexSearchClient()

def search_knowledge_base(query: str) -> str:
    """
    Searches the [APP_NAME] Hackathon knowledge base to find information and answer user questions.

    Args:
        query: A detailed search query crafted from the user's question.
    """
    logger.info(f"Tool call: search_knowledge_base with query: {query}")
    return search_client.search(query)
```

### d. Search Client: `src/search/vertex_client.py`

This component is responsible for communicating with the Google Cloud Vertex AI Search API.

-   **What it does:** It constructs a search request using the user's query and sends it directly to your specific **Data Store**. By targeting the datastore directly, we ensure that the search is strictly limited to the documents you have ingested. It then processes the response to extract the most relevant snippets or paragraphs.

```python
# src/search/vertex_client.py
class VertexSearchClient:
    def __init__(self):
        # ... initialization ...
        
        self.serving_config = self.search_client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config="default_config",
        )
        # ...

    def search(self, query: str) -> str:
        # ...
            # TODO: HACKATHON CHALLENGE for Hybrid Search or Metadata Filtering
            
            request = discoveryengine.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                # ...
            )
            response = self.search_client.search(request)

            # ... logic to extract content ...
            
            consolidated_context = "\n\n".join(context_snippets)
            return consolidated_context if consolidated_context else "No relevant documents found."
```