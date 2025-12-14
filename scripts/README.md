# Evaluating the RAG Agent

This directory contains the script for evaluating the performance of the RAG agent. The primary goal of this evaluation is to provide a reliable, automated measure of the agent's ability to answer questions accurately and safely based on the provided documents.

## The Challenge: Fixing the Evaluation Harness

Currently, the `run_evaluation.py` script does **not** test the agent in a true 1-to-1 fashion. Instead of importing and running the actual ADK agent from `src/agents/adk_agent.py`, it **simulates** the agent's logic.

### Why is this a Problem?

This is a common anti-pattern in software testing for several critical reasons:

1.  **False Confidence:** The simulation can produce high scores that give a false sense of security, while the real agent might fail in interactive use. As we discovered, the simulated agent scored well, but the real agent with a "bad" prompt would refuse to answer questions.
2.  **Code Divergence:** The logic in the evaluation script and the logic in the agent are separate. Any changes made to the agent's prompt or configuration will not be reflected in the evaluation, making the test results meaningless over time.
3.  **Incomplete Simulation:** The simulation only tests the "happy path" and fails to capture the complex decision-making of the real agent, such as its choice of whether or not to use a tool.

## The Task

Your task is to refactor the `run_evaluation.py` script to correctly evaluate the agent. This involves:

1.  **Importing the Agent:** Modify the script to import the fully configured `agent_config` object from `src/agents/adk_agent.py`.
2.  **Running the Agent:** Use the ADK's `InMemoryRunner` or a similar mechanism to execute the agent for each question in the dataset. This will involve handling asynchronous code.
3.  **Capturing the Output:** Capture the final text response from the agent and pass it to the Vertex AI Evaluation service.

By completing this task, you will create a reliable test harness that accurately measures the performance of the agent, ensuring that any improvements to the prompt are correctly reflected in the evaluation scores.