# Agents

This directory contains the core logic for the AI agents, defining their behavior, tools, and system instructions.

## Files

-   `adk_agent.py`: This file configures and initializes the primary agent using the Agent Development Kit (ADK). It sets the agent's persona and instructions (`system_prompt`) and registers the tools it can use.
-   `tools.py`: This file defines the custom functions (tools) that the agent can execute. The `search_knowledge_base` function acts as the bridge between the agent and the `VertexSearchClient` to retrieve information from the knowledge base.