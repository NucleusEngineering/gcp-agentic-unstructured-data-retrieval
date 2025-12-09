# src/agents/adk_agent.py
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from src.agents.tools import search_knowledge_base
from google.generativeai import types

# 2. Define the System Instruction (reused from your RAGAgent)
system_prompt = """You are a helpful AI assistant for the Nelly Hackathon.
Your knowledge comes exclusively from the "search_knowledge_base" tool.
ALWAYS use the tool to find information before answering.
If the user asks about "Nelly", "proposals", or "hackathons", search first."""

# 1. Define the Model Configuration
# ADK abstracts the specific provider (Gemini, etc.)
model_config = Gemini(
    model="gemini-2.0-flash-lite",
)

# 3. Initialize the Agent
agent_config = Agent(
    name="nelly_agent",
    model=model_config,
    instruction=system_prompt,
    generate_content_config=types.GenerationConfig(temperature=0),
    tools=[search_knowledge_base], # Pass the decorated function directly
)