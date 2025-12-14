import json
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.evaluation import EvalTask
import os
import sys
from dotenv import load_dotenv
import uuid
from google.genai import types

# Load environment variables
load_dotenv()

# Add 'src' to path so we can import the tool
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agents.adk_agent import system_prompt
from src.agents.tools import search_knowledge_base
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from src.agents.adk_agent import agent_config, app_name
import asyncio

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_REGION", "europe-west1") 
GOLDEN_DATASET = "data/processed/golden_dataset.jsonl"
RESULTS_FILE = "data/processed/eval_results.json"
USER_ID = "eval_user_123"


async def get_agent_response(question: str) -> str:
    """
    Uses google.adk.runners.Runner to get a text response from the agent.
    """
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session_id = f"{app_name}-{uuid.uuid4().hex[:8]}"
    runner = Runner(
        agent=agent_config,
        app_name=app_name,
        session_service=session_service,
        artifact_service=artifact_service,
    )
    await session_service.create_session(
        app_name=app_name, user_id=USER_ID, session_id=session_id
    )
    try:
        print(f"   🗣️ Asking agent: {question[:30]}...")
        final_response_text = "Error: No response received."
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=question)]
            ),
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                    break  # Exit loop once final response is found
        return final_response_text.strip()
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return f"Error generating response: {e}"


async def main():
    print(f"🚀 Initializing Vertex AI in {LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Load Data
    data = []
    if not os.path.exists(GOLDEN_DATASET):
        print(f"❌ Dataset not found: {GOLDEN_DATASET}. Run 'scripts/generate_golden_dataset.py' first.")
        return

    with open(GOLDEN_DATASET, "r") as f:
        for line in f: 
            data.append(json.loads(line))
    
    # Use 5 rows for a quick test (remove .head(5) for a full run)
    eval_df = pd.DataFrame(data).head(5) 
    
    # 2. Get Real Model Predictions
    print(f"🤖 Generating responses for {len(eval_df)} questions...")
    questions = eval_df["question"].tolist()
    responses = await asyncio.gather(*[get_agent_response(q) for q in questions])
    eval_df["response"] = responses

    # 3. Define Metrics
    metrics = [
        "groundedness", 
        "instruction_following", 
        "safety" 
    ]

    # 4. Run Evaluation
    print("📊 Running Vertex AI Evaluation...")
    eval_task = EvalTask(
        dataset=eval_df,
        metrics=metrics,
        metric_column_mapping={
            "prompt": "context",
        },
        experiment="rag-mvp-eval-002"
    )
    
    result = eval_task.evaluate()

    # 5. Output Results
    print("\n--- Evaluation Summary ---")
    print(result.summary_metrics)
    
    result.metrics_table.to_json(RESULTS_FILE, orient="records", lines=True)
    print(f"✅ Detailed results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    asyncio.run(main())