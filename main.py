# main.py (Migrated)
import argparse
import asyncio
from google.adk.runners import InMemoryRunner
from src.agents.adk_agent import agent_config
from src.ingestion.pipeline import run_ingestion
from src.shared.logger import setup_logger
from src.shared.validator import validate_datastore
import os

logger = setup_logger(__name__)

def run_chat_mode():
    logger.info("Initializing ADK Chat...")
    print("--- Nelly ADK Chatbot ---")
    print("Type 'exit' to quit.")
    
    runner = InMemoryRunner(agent=agent_config)
    
    # Use the ADK's built-in debug runner for interactive chat
    # This handles the user input loop.
    async def chat():
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            await runner.run_debug(user_input)

    asyncio.run(chat())


def main():
    parser = argparse.ArgumentParser(description="Nelly RAG Agent CLI")
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
