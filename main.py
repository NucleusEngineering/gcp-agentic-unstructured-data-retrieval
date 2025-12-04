import argparse
import os
from dotenv import load_dotenv
from src.ingestion.pipeline import run_ingestion
from src.agents.rag_agent import RAGAgent
from src.shared.logger import setup_logger
from src.shared.validator import validate_datastore

logger = setup_logger(__name__)
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="RAG System CLI")
    parser.add_argument("--mode", type=str, required=True, choices=["ingest", "chat"], help="Mode to run: 'ingest' or 'chat'")
    args = parser.parse_args()

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION") # This is the Discovery Engine multi-region ('us', 'eu')
    vertex_ai_region = os.getenv("VERTEX_AI_REGION") # This is the Vertex AI region (e.g., 'us-central1')
    data_store_id = os.getenv("DATA_STORE_ID")

    if not all([project_id, location, vertex_ai_region, data_store_id]):
        logger.error("Missing one or more environment variables.")
        raise ValueError("PROJECT_ID, LOCATION, VERTEX_AI_REGION, and DATA_STORE_ID must be set in the .env file.")

    if args.mode == "ingest":
        logger.info("Starting ingestion mode...")
        input_dir = "data/raw"
        output_dir = "data/processed"
        run_ingestion(input_dir, output_dir)
        logger.info("Ingestion mode finished.")
    elif args.mode == "chat":
        # Validate the datastore before starting the agent
        validate_datastore(project_id, location, data_store_id)
        
        logger.info("Starting chat mode...")
        agent = RAGAgent(project_id=project_id, vertex_ai_region=vertex_ai_region)
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
