import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool, FunctionDeclaration
from src.agents.tools import retrieve_documents
from src.shared.logger import setup_logger

logger = setup_logger(__name__)

class RAGAgent:
    """
    A Gemini-powered Agent for querying with a Search Tool, following ADK patterns with
    manual tool definition for Vertex AI SDK compatibility.
    """
    def __init__(self, project_id: str, vertex_ai_region: str, model_name: str = "gemini-2.0-flash-lite"):
        # 1. Initialize Vertex AI with a specific GCP region
        vertexai.init(project=project_id, location=vertex_ai_region)
        
        # 2. Manually define the tool as per Vertex AI SDK requirements
        retrieve_documents_tool = Tool(
            function_declarations=[
                FunctionDeclaration(
                    name="retrieve_documents",
                    description="Retrieves relevant documents from the knowledge base.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant documents."
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
        )
        
        # 3. Initialize Model with Tools
        self.model = GenerativeModel(
            model_name,
            tools=[retrieve_documents_tool],
        )
        
        # 4. Start Chat Session
        self.chat = self.model.start_chat()
        logger.info(f"RAGAgent initialized with {model_name} model.")

    def ask(self, question: str) -> str:
        """
        Sends a query to the agent and returns the natural language response.
        """
        logger.info(f"User question: {question}")
        response = self.chat.send_message(question)
        
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            logger.info(f"Model called tool: {function_call.name} with args: {function_call.args}")
            
            if function_call.name == "retrieve_documents":
                tool_result = retrieve_documents(query=function_call.args["query"])
                
                response = self.chat.send_message(
                    Part.from_function_response(
                        name=function_call.name,
                        response={"content": tool_result}
                    )
                )

        final_response = response.text
        logger.info(f"Agent final response: {final_response}")
        return final_response