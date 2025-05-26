from agno.agent import Agent, Tool
from agno.models.openai import OpenAIModel
import requests
from typing import List
import os  # For loading environment variables

class AstraDBRetrievalTool(Tool):
    """
    Agno-compatible Tool for retrieval from a single AstraDB vector DB.
    """
    def __init__(self, endpoint: str, api_key: str, collection: str):
        super().__init__(name=f"AstraDB:{collection}")
        self.endpoint = endpoint
        self.api_key = api_key
        self.collection = collection

    def run(self, query: str) -> List[str]:
        url = f"{self.endpoint}/api/rest/v2/namespaces/default/collections/{self.collection}/vector-search"
        payload = {"query": query, "topK": 5}
        headers = {"x-cassandra-token": self.api_key, "Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            hits = response.json().get("documents", [])
            return [hit["document"]["content"] for hit in hits]
        except requests.RequestException as e:
            print(f"Error querying AstraDB: {e}")
            return []

# --- Multi-Collection RAG Setup ---
# Load AstraDB endpoint and API key from environment variables for security
astra_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
astra_api_key = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

# List all collections you want to use
collection_names = [
    "skysafari",
    "starrynight",
    "starry_night_faq",
    "celestron_pdfs",
    "YouTube"
]

# Instantiate one tool per collection
tools = [
    AstraDBRetrievalTool(
        endpoint=astra_endpoint,
        api_key=astra_api_key,
        collection=coll
    )
    for coll in collection_names
]

# Set up the language model
model = OpenAIModel(model_name="gpt-3.5-turbo")

# Pass all tools to the Agent for multi-collection RAG
agent = Agent(
    tools=tools,
    model=model,
)

def main():
    # Example query
    query = "What is the best telescope for a beginner?"
    response = agent.run(query)
    print(response)

if __name__ == "__main__":
    main()
