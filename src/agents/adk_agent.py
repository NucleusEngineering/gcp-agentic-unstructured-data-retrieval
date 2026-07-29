# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.adk.agents import Agent
from src.agents.tools import search_knowledge_base
from google.genai import types
import os


# TODO: HACKATHON CHALLENGE (Challenge 2, Part 1)
# The prompt below is static. Your goal is to implement a prompt router
# that dynamically selects a persona and instructions based on the user's query.
# For example, a query asking for a summary might use a "summarizer" persona,
# while a query asking for specific data points might use a "data extractor" persona.
# You can define different prompt strategies in a new module and then
# modify this agent to use a router to select one before executing the search.

system_prompt = """
You are a helpful assistant.
"""

app_name = os.getenv("APP_NAME", "GenAI-RAG").lower().replace(" ", "_").replace("-", "_")

# For a list of available models, see:
# https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
agent_config = Agent(
    name=f"{app_name}_agent",
    model="gemini-2.0-flash-lite",
    instruction=system_prompt,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[search_knowledge_base],
)