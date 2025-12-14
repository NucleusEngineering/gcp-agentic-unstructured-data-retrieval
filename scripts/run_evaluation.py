import json
import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.evaluation import EvalTask
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add 'src' to path so we can import the tool
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agents.tools import search_knowledge_base

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_REGION", "europe-west1") 
GOLDEN_DATASET = "data/golden_dataset.jsonl"
RESULTS_FILE = "eval_results.json"

def get_rag_response(question):
    """
    Simulates the Agent's RAG flow for evaluation:
    1. Search Knowledge Base (Tool)
    2. Generate Answer (Model)
    """
    try:
        # 1. RETRIEVE: Call the actual search tool
        print(f"   🔍 Searching for: {question[:30]}...")
        context = search_knowledge_base(question)
        
        # 2. GENERATE: Pass context to the model
        prompt = f"""
        You are a Medical Records Analysis Bot.
        Answer the question based EXCLUSIVELY on the provided context. 
        
        CONTEXT:
        {context}
        
        QUESTION:
        {question}
        """
        
        model = GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "Error generating response."

def run_eval():
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
    eval_df["response"] = eval_df["question"].apply(get_rag_response)

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
            "prompt": "question",
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
    run_eval()