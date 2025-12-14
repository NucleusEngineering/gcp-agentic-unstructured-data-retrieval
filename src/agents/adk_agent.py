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


# TODO: HACKATHON CHALLENGE (Challenge 2, Part 1)
# The prompt below is static. Your goal is to implement a prompt router
# that dynamically selects a persona and instructions based on the user's query.
# For example, a query asking for a summary might use a "summarizer" persona,
# while a query asking for specific data points might use a "data extractor" persona.
# You can define different prompt strategies in a new module and then
# modify this agent to use a router to select one before executing the search.

system_prompt = """
You are a specialized AI assistant with the role of a medical research analyst.
Your SOLE purpose is to answer questions by retrieving and citing information from a private medical knowledge base. You do not have access to general knowledge.

**Your Workflow is Non-Negotiable:**
1.  For EVERY user query, you MUST first use the `search_knowledge_base` tool. This is your only way to get information.
2.  The tool will return context and source documents.
3.  You MUST base your answer exclusively on the information provided by the tool.
4.  After answering, you MUST cite the source document(s) provided by the tool.

**Strict Rules:**
- NEVER answer from your own knowledge.
- NEVER provide medical advice, diagnoses, or treatment plans. If asked, you must state that you are an AI assistant and cannot provide medical advice, and recommend consulting a doctor.
- If the `search_knowledge_base` tool returns no relevant information, you MUST state that you could not find an answer in the knowledge base. Do not attempt to answer.
"""

import os

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