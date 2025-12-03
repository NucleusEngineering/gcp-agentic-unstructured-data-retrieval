import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool
from src.search.vertex_client import VertexSearchClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RAGAgent:
    """
    A Gemini-powered Agent for querying with a Search Tool.
    """
    def __init__(self, project_id: str, location: str):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-flash")
        self.vertex_search_client = VertexSearchClient()
        logger.info("RAGAgent initialized with Gemini 1.5 Flash model.")

    def retrieve_documents(self, query: str) -> str:
        """
        Retrieves relevant documents using the VertexSearchClient.
        This function is designed to be used as a tool for the Gemini model.

        Args:
            query (str): The search query.

        Returns:
            str: Consolidated context from retrieved documents.
        """
        logger.info(f"Tool call: retrieve_documents with query: {query}")
        return self.vertex_search_client.search(query)

    def ask(self, question: str) -> str:
        """
        Starts a chat session with the Gemini model, using the retrieve_documents tool.

        Args:
            question (str): The user's question.

        Returns:
            str: The natural language response from the Gemini model.
        """
        # Define the tool
        retrieve_documents_tool = Tool.from_function(self.retrieve_documents)

        # Start a chat session and bind the tool
        chat = self.model.start_chat(tools=[retrieve_documents_tool])

        logger.info(f"User question: {question}")
        response = chat.send_message(question)

        # Check if the model called the tool
        if response.candidates[0].content.parts[0].function_call:
            tool_response = response.candidates[0].content.parts[0].function_call
            logger.info(f"Model called tool: {tool_response.name} with args: {tool_response.args}")
            # The tool is automatically executed by the SDK when bound to the chat session
            # We just need to send the response back to the model
            response = chat.send_message(Part.from_function_response(
                name=tool_response.name,
                response=self.retrieve_documents(tool_response.args["query"])
            ))

        final_response = response.text
        logger.info(f"Agent final response: {final_response}")
        return final_response
