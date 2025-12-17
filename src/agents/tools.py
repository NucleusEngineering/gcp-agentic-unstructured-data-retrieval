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
from src.search.vertex_client import VertexSearchClient
from src.shared.logger import setup_logger

# Import all medical database tools
from src.database.tools import (
    get_patient_medications,
    count_patient_medications,
    search_patients_by_medication,
    get_patient_doctor,
    get_all_patients,
    get_patient_count,
    get_patient_diagnosis,
    get_patient_treatment_plan,
    get_patient_visit_date
)

logger = setup_logger(__name__)

search_client = VertexSearchClient()

def search_knowledge_base(query: str) -> str:
    """Searches the knowledge base to find information to answer user questions.

    Args:
        query: A detailed search query crafted from the user's question.
    """
    logger.info(f"Tool call: search_knowledge_base with query: {query}")
    return search_client.search(query)

# All medical database tools are automatically available through imports
# The ADK agent will discover these tools via the @tool decorators
