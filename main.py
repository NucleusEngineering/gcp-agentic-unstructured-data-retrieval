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
# main.py (Migrated)
import argparse
import asyncio
from google.adk.runners import InMemoryRunner
from src.agents.adk_agent import build_agent_for_query
from src.ingestion.pipeline import run_ingestion
from src.shared.logger import setup_logger
from src.shared.validator import validate_datastore
import os

logger = setup_logger(__name__)
app_name = os.getenv("APP_NAME", "GenAI-RAG")


def run_chat_mode():
    logger.info("Initializing ADK Chat...")

    print(f"--- {app_name} ADK Chatbot ---")
    print("Type 'exit' to quit.")

    # Use the ADK's built-in debug runner for interactive chat
    # This handles the user input loop.
    async def chat():
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # This is not ideal but works for this demo
            agent_config = build_agent_for_query(user_input)
            runner = InMemoryRunner(agent=agent_config)
            await runner.run_debug(user_input)

    asyncio.run(chat())


def main():
    parser = argparse.ArgumentParser(description=f"{app_name} RAG Agent CLI")
    parser.add_argument(
        "--mode",
        choices=["chat", "ingest"],
        required=True,
        help="The mode to run the application in.",
    )
    args = parser.parse_args()

    # Validate common environment variables
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")
    data_store_id = os.getenv("DATA_STORE_ID")
    # The ADK runner will automatically pick up the VERTEX_AI_REGION
    if not all([project_id, location, data_store_id, os.getenv("VERTEX_AI_REGION")]):
        logger.critical("Error: PROJECT_ID, LOCATION, VERTEX_AI_REGION and DATA_STORE_ID must be set in your .env file.")
        return

    try:
        validate_datastore(project_id, location, data_store_id)
    except ValueError as e:
        logger.critical(f"Datastore validation failed: {e}")
        return
    except Exception as e:
        logger.critical(f"An unhandled error occurred: {e}")
        return

    if args.mode == "chat":
        logger.info("Starting chat mode...")
        run_chat_mode()
    elif args.mode == "ingest":
        logger.info("Starting ingestion mode...")
        run_ingestion(input_dir="data/raw", output_dir="data/processed")
        logger.info("Ingestion mode finished.")

if __name__ == "__main__":
    main()
