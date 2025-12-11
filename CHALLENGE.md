
# Hackathon Challenge Guide: 

Welcome to the challenge. This guide outlines opportunities to re-engineer parts of the system. Your success will be evaluated on three pillars:



1.  **Completeness:** Did you find and solve the code gaps (TODOs)?

2.  **Extensibility:** Can your pipeline handle more than just PDFs?

3.  **Creativity (ADK):** Can you implement a Multi-Agent system or advanced workflow pattern?



-----



## Pillar 1: Completeness (The Code Hunt)



Your first task is to find the `# TODO: HACKATHON CHALLENGE` flags hidden in the codebase and implement the missing logic.



**Target Files & Concepts:**

*   `src/ingestion/chunker.py`: The current chunker uses a basic fixed size. Your goal is to make it context-aware.
    *   **Semantic Chunking:** Instead of splitting text by a fixed number of characters, this method groups text based on its meaning or topic. This ensures that related sentences and ideas are kept together, providing better context for the agent.
    *   **Recursive Chunking:** This technique intelligently splits large documents by recursively working through a list of separators (e.g., paragraphs, then sentences, then words). This helps preserve the document's hierarchical structure.

*   `src/search/vertex_client.py`: The current search is good but not great. Your goal is to make it more precise.
    *   **Hybrid Search:** This approach combines the best of both worlds: traditional keyword-based search (great for acronyms and specific terms) and modern vector search (great for understanding context and meaning). The result is a more accurate and relevant set of search results.
    *   **Metadata Filtering:** This allows the system to narrow down the search space *before* executing the query. For example, you could filter to only include documents created in the last year or those written by a specific author. This makes the search faster and the results more focused.

*   `src/agents/rag_agent.py`: The agent is generic. Your goal is to give it clear guardrails and a personality.
    *   **Persona:** This defines the agent's character and style. Is it a formal medical expert, a friendly assistant, or a concise summarizer? A clear persona makes the agent's responses more consistent and predictable.
    *   **System Instructions:** These are the hard rules the agent must follow. For example: "Always cite your sources," "Never provide a diagnosis," or "Keep your answers to three sentences or less." This is crucial for ensuring the agent behaves safely and responsibly.



-----



## Pillar 2: Extensibility (The "New Data" Challenge)



The current pipeline only supports PDFs. In the real world, medical data comes in text files, CSVs, and emails.



**Your Goal:**

Modify the ingestion pipeline to support a new format.



**Where to Hack:**



1.  **`src/ingestion/parser.py`**:



      * **Current State:** Only has `parse_pdf`.

            * **Challenge:** Implement `parse_other_format(file_path)`.

        ```python

        def parse_other_format(file_path: str) -> str:

            # TODO: HACKATHON CHALLENGE (Pillar 2)

            # Implement logic to read other files than pdf.

            pass
        ```

2.  **`src/ingestion/pipeline.py`**:



      * **Current State:** `glob(os.path.join(input_dir, "*.pdf"))`

      * **Challenge:** Update the pipeline to find other files than pdf and route them to your new parser.



    <!-- end list -->



        ```python

        # src/ingestion/pipeline.py



        def run_ingestion(input_dir, output_dir):

            # TODO: HACKATHON CHALLENGE (Pillar 2)

            # 1. Glob for *.other_format files as well as *.pdf

            # 2. If file ends with .other_format, call parse_other_format() instead of parse_pdf()

            ...

        ```



-----



## Pillar 3: Creativity (The Agent-to-Agent Flow)



This is an advanced challenge. A single agent is often overwhelmed. We want you to design a **Multi-Agent System** where specialized agents collaborate to solve a problem.



**Your Goal:**

Build a creative workflow where agents **talk to each other**, **execute tools**, and **write to external systems**. Do not just build a chatbot that summarizes text. Build a system that takes action.



**The Workflow Requirements:**

1.  **Agent-to-Agent:** One agent must delegate work to another (e.g., a "Manager" telling a "Worker" what to do).

2.  **Tooling:** Agents must use tools (search, calculation, or custom Python functions).

3.  **External Write:** The system must "do" something with the result (e.g., save a file, send a mock email, or update a status).



**Simple Design Ideas (Holistic Flows):**



* **The "Maker-Checker" Flow (Quality Control):**

    * **Agent A (The Writer):** Drafts a response based on the search results.

    * **Agent B (The Auditor):** Reviews that draft against the source text. If it passes, Agent B **executes a tool** to save the final report to a file. If it fails, it sends it back to Agent A.

* **The "Triage" Flow (Delegation):**

    * **Agent A (The Receptionist):** Identifies user intent. If the user wants to "Search," it calls **Agent B (The Researcher)**. If the user wants to "Book," it calls **Agent C (The Scheduler)**.

    * **Action:** The sub-agent performs the specific tool call and returns the result to the Receptionist.

* **The "Drafter-Approver" Flow (Human-in-the-Loop):**

    * **Agent A:** Formulates a plan to "Send a Referral."

    * **Stop:** It pauses and asks the user (you) for confirmation.

    * **Action:** Only upon your "Yes," the agent **writes** the referral to a text file or calls a mock API.



**Resources:**

For code templates and implementation details, refer to the official ADK Python Agents:

👉 **[Google ADK Python Agents Samples](https://github.com/google/adk-samples/tree/main/python/agents)**

-----



## Evaluation Checklist (For Judges)



Use this rubric to score the teams:



| Category | Criteria | Points (0-5) |
| :--- | :--- | :--- |
| **Ingestion** | Did they fix the `chunker.py` TODOs (Semantic/Recursive)? | |
| **Data Types** | Can the system successfully ingest and search a file with a different format? | |
| **Search** | Did they implement Filtering or Hybrid Search in `vertex_client.py`? | |
| **Architecture** | **(x2 Multiplier)** Is there a functioning Advanced ADK Pattern (Router, Auditor, etc.)? | |
| **Stability** | Does the system run without crashing? | |

**Total Score:** ___ / 30
