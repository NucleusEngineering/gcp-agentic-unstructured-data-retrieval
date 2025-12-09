from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from src.agents.tools import search_knowledge_base
from google.genai import types

system_prompt = """You are a helpful AI assistant.
Your knowledge comes exclusively from the documents provided to you via the "search_knowledge_base" tool.
You must ALWAYS use the "search_knowledge_base" tool to find information before answering any question.
Do not rely on any prior knowledge."""

model_config = Gemini(
    model="gemini-2.0-flash-lite",
)

agent_config = Agent(
    name="nelly_agent",
    model=model_config,
    instruction=system_prompt,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[search_knowledge_base],
)