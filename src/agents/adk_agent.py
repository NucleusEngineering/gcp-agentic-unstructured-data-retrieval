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

# Default agent configuration (will be dynamically updated based on queries)
app_name = os.getenv("APP_NAME", "GenAI-RAG").lower().replace(" ", "_").replace("-", "_")
system_prompt = "You are a helpful assistant that provides accurate information based on the provided context."

# For backward compatibility, create a default agent config
# In practice, the dynamic agent created by medication_agent_manager should be used
agent_config = Agent(
    name=f"{app_name}_agent",
    model="gemini-2.0-flash-lite",
    instruction=system_prompt,  # Default to scheduler
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[search_knowledge_base],
)