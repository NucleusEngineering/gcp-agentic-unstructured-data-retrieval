
  Migration Guide: Custom SDK to Google ADK (Enriched)

  Overview

  This document outlines the steps to migrate the current "Nelly Hackathon" agent from
   a raw vertexai SDK implementation to the Google Agent Development Kit (ADK).

  Goal: Replace manual loop orchestration and tool definitions with ADK's managed
  runtime, while preserving the custom Vertex AI Search logic. This migration will
  touch the following files:
   * src/agents/tools.py (Refactored)
   * src/agents/rag_agent.py (Deleted)
   * src/agents/adk_agent.py (New)
   * main.py (Refactored)

  Phase 1: Installation & Setup

  First, add the ADK library to your project.

   1 poetry add google-adk

  Phase 2: Adapt the Tools (src/agents/tools.py)

  In your current setup, you manually define Tool objects in the agent class. In ADK,
  you decorate functions to make them discoverable. We will also improve performance
  by initializing the VertexSearchClient only once.

  Action: Update src/agents/tools.py to use the @adk.tool decorator and a single
  client instance.

    1 # src/agents/tools.py (Migrated)
    2 from google.adk import tool
    3 from src.search.vertex_client import VertexSearchClient
    4 from src.shared.logger import setup_logger
    5 
    6 logger = setup_logger(__name__)
    7 
    8 # Initialize the client once to be reused across tool calls.
    9 # This is more efficient and prevents re-initializing on every user query.
   10 search_client = VertexSearchClient()
   11 
   12 @tool
   13 def search_knowledge_base(query: str) -> str:
   14     """
   15     Searches the Nelly Hackathon knowledge base to find information and answer
      user questions.
   16 
   17     Args:
   18         query: A detailed search query crafted from the user's question.
   19     """
   20     logger.info(f"Tool call: search_knowledge_base with query: {query}")
   21     # Reuse the existing, fixed VertexSearchClient logic!
   22     return search_client.search(query)

  Codebase-Specific Notes:
   * Performance: Your previous implementation created a new VertexSearchClient instance
      for every single query. This change creates a single, reusable instance, which is
     more efficient and will reduce the repetitive VertexSearchClient initializing...
     logs you were seeing.
   * No Change to Search Logic: Your core Enterprise Search logic in
     src/search/vertex_client.py remains untouched.

  Phase 3: Create the ADK Agent (src/agents/adk_agent.py)

  Instead of your custom RAGAgent class, you will define an ADK Agent. This handles
  memory, model connections, and the tool-calling loop automatically.

  Action: Create a new file src/agents/adk_agent.py.

    1 # src/agents/adk_agent.py
    2 from google.adk import Agent, Model
    3 from src.agents.tools import search_knowledge_base
    4 
    5 def create_nelly_agent():
    6     # 1. Define the Model Configuration
    7     # ADK abstracts the specific provider (Gemini, etc.)
    8     model = Model(
    9         model_name="gemini-2.0-flash-lite",
   10         parameters={"temperature": 0}
   11     )
   12 
   13     # 2. Define the System Instruction (reused from your RAGAgent)
   14     system_prompt = """You are a helpful AI assistant for the Nelly Hackathon.
   15     Your knowledge comes exclusively from the "search_knowledge_base" tool.
   16     ALWAYS use the tool to find information before answering.
   17     If the user asks about "Nelly", "proposals", or "hackathons", search first."""
   18 
   19     # 3. Initialize the Agent
   20     agent = Agent(
   21         model=model,
   22         system_instruction=system_prompt,
   23         tools=[search_knowledge_base], # Pass the decorated function directly
   24     )
   25 
   26     return agent

  Phase 4: Update the Entrypoint (main.py)

  This is a critical step. The original migration guide only accounted for chat mode.
  Your main.py also contains the vital ingest mode, which we must preserve.

  Action: Update main.py to use the ADK runner for chat mode while keeping the
  ingestion logic intact.

    1 # main.py (Migrated)
    2 import argparse
    3 from src.agents.adk_agent import create_nelly_agent
    4 from src.ingestion.pipeline import run_ingestion
    5 from src.shared.logger import setup_logger
    6 from src.shared.validator import validate_datastore
    7 import os
    8 
    9 logger = setup_logger(__name__)
   10 
   11 def run_chat_mode():
   12     # ADK handles the environment variables for the model automatically
   13     logger.info("Initializing ADK Agent...")
   14     agent = create_nelly_agent()
   15 
   16     print("--- Nelly ADK Chatbot ---")
   17     print("Type 'exit' to quit.")
   18 
   19     try:
   20         while True:
   21             user_input = input("\nYou: ")
   22             if user_input.lower() in ["exit", "quit"]:
   23                 break
   24 
   25             # agent.run() handles the tool calling loop automatically!
   26             response = agent.run(user_input)
   27             print(f"\nBot: {response.text}")
   28 
   29     except KeyboardInterrupt:
   30         print("\nExiting...")
   31     finally:
   32         logger.info("Chat mode finished.")
   33 
   34 def main():
   35     parser = argparse.ArgumentParser(description="Nelly RAG Agent CLI")
   36     parser.add_argument(
   37         "--mode",
   38         choices=["chat", "ingest"],
   39         required=True,
   40         help="The mode to run the application in.",
   41     )
   42     args = parser.parse_args()
   43 
   44     # Validate common environment variables
   45     project_id = os.getenv("PROJECT_ID")
   46     location = os.getenv("LOCATION")
   47     data_store_id = os.getenv("DATA_STORE_ID")
   48 
   49     if not all([project_id, location, data_store_id]):
   50         logger.critical("Error: PROJECT_ID, LOCATION, and DATA_STORE_ID must be 
      set in your .env file.")
   51         return
   52 
   53     try:
   54         validate_datastore(project_id, location, data_store_id)
   55     except ValueError as e:
   56         logger.critical(f"Datastore validation failed: {e}")
   57         return
   58     except Exception as e:
   59         logger.critical(f"An unhandled error occurred: {e}")
   60         return
   61 
   62     if args.mode == "chat":
   63         logger.info("Starting chat mode...")
   64         run_chat_mode()
   65     elif args.mode == "ingest":
   66         logger.info("Starting ingestion mode...")
   67         run_ingestion(input_dir="data/raw", output_dir="data/processed")
   68         logger.info("Ingestion mode finished.")
   69 
   70 if __name__ == "__main__":
   71     main()

  Phase 5: Cleanup

  To avoid confusion and obsolete code, you can now safely delete the old agent file.

  Action: Delete src/agents/rag_agent.py.

  Migration Checklist

   1. [ ] Install: google-adk installed via Poetry.
   2. [ ] Tools: search_knowledge_base decorated with @tool and client is reused.
   3. [ ] Agent: New src/agents/adk_agent.py created.
   4. [ ] Main: main.py refactored to use agent.run() for chat and preserve ingest mode.
   5. [ ] Cleanup: Old src/agents/rag_agent.py file deleted.
   6. [ ] Verify: Run poetry run python main.py --mode chat and confirm the bot still
      provides Enterprise-quality answers.
   7. [ ] Verify: Run poetry run python main.py --mode ingest and confirm the ingestion
      pipeline still works.

  Key Benefits of this Migration

   * Less Boilerplate: No more manual FunctionDeclaration schemas or while loops.
   * Managed State: ADK handles session history automatically.
   * Improved Performance: The VertexSearchClient is now initialized only once,
     improving efficiency.
   * Maintainability: The codebase is now cleaner and more aligned with official Google
     tooling, making it easier to maintain and extend.
