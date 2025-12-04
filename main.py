import argparse
import os
from dotenv import load_dotenv
from src.ingestion.pipeline import run_ingestion
from src.agents.rag_agent import RAGAgent
from src.shared.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="RAG System CLI")
    parser.add_argument("--mode", type=str, required=True, choices=["ingest", "chat"], help="Mode to run: 'ingest' or 'chat'")
    args = parser.parse_args()

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")

    if not all([project_id, location]):
        logger.error("Missing PROJECT_ID or LOCATION environment variables.")
        raise ValueError("PROJECT_ID and LOCATION must be set in the .env file.")

    if args.mode == "ingest":
        logger.info("Starting ingestion mode...")
        input_dir = "data/raw"
        output_dir = "data/processed"
        run_ingestion(input_dir, output_dir)
        logger.info("Ingestion mode finished.")
    elif args.mode == "chat":
        logger.info("Starting chat mode...")
        agent = RAGAgent(project_id=project_id, location=location)
        print("\n--- RAG Chatbot ---\nType 'exit' to quit.\n")
        while True:
            question = input("You: ")
            if question.lower() == 'exit':
                break
            response = agent.ask(question)
            print(f"Bot: {response}")
        logger.info("Chat mode finished.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"An unhandled error occurred: {e}")
