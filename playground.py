"""
Agno Playground entrypoint for Agent-UI integration.
This script registers all agents (including the multi-collection AstraDB RAG agent) for UI discovery.
Follows Agno documentation: https://docs.agno.com/agent-ui/introduction#connect-to-local-agents
"""

from dotenv import load_dotenv
load_dotenv()
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app

# Import other agents if desired
# from agents.web_agent import get_web_agent
# from agents.finance_agent import get_finance_agent

# --- Multi-Collection AstraDB RAG Agent ---
import requests
from agno.tools.decorator import tool

astra_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
astra_api_key = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

@tool(name="astradb_skysafari", description="Query the skysafari collection in AstraDB.")
def query_skysafari(query: str) -> list[str]:
    url = f"{astra_endpoint}/api/rest/v2/namespaces/default/collections/skysafari/vector-search"
    payload = {"query": query, "topK": 5}
    headers = {"x-cassandra-token": astra_api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        hits = response.json().get("documents", [])
        return [hit["document"]["content"] for hit in hits]
    except requests.RequestException as e:
        print(f"Error querying AstraDB: {e}")
        return []

@tool(name="astradb_starrynight", description="Query the starrynight collection in AstraDB.")
def query_starrynight(query: str) -> list[str]:
    url = f"{astra_endpoint}/api/rest/v2/namespaces/default/collections/starrynight/vector-search"
    payload = {"query": query, "topK": 5}
    headers = {"x-cassandra-token": astra_api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        hits = response.json().get("documents", [])
        return [hit["document"]["content"] for hit in hits]
    except requests.RequestException as e:
        print(f"Error querying AstraDB: {e}")
        return []

@tool(name="astradb_starry_night_faq", description="Query the starry_night_faq collection in AstraDB.")
def query_starry_night_faq(query: str) -> list[str]:
    url = f"{astra_endpoint}/api/rest/v2/namespaces/default/collections/starry_night_faq/vector-search"
    payload = {"query": query, "topK": 5}
    headers = {"x-cassandra-token": astra_api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        hits = response.json().get("documents", [])
        return [hit["document"]["content"] for hit in hits]
    except requests.RequestException as e:
        print(f"Error querying AstraDB: {e}")
        return []

@tool(name="astradb_celestron_pdfs", description="Query the celestron_pdfs collection in AstraDB.")
def query_celestron_pdfs(query: str) -> list[str]:
    url = f"{astra_endpoint}/api/rest/v2/namespaces/default/collections/celestron_pdfs/vector-search"
    payload = {"query": query, "topK": 5}
    headers = {"x-cassandra-token": astra_api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        hits = response.json().get("documents", [])
        return [hit["document"]["content"] for hit in hits]
    except requests.RequestException as e:
        print(f"Error querying AstraDB: {e}")
        return []

@tool(name="astradb_youtube", description="Query the YouTube collection in AstraDB.")
def query_youtube(query: str) -> list[str]:
    url = f"{astra_endpoint}/api/rest/v2/namespaces/default/collections/YouTube/vector-search"
    payload = {"query": query, "topK": 5}
    headers = {"x-cassandra-token": astra_api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        hits = response.json().get("documents", [])
        return [hit["document"]["content"] for hit in hits]
    except requests.RequestException as e:
        print(f"Error querying AstraDB: {e}")
        return []

tools = [
    query_skysafari,
    query_starrynight,
    query_starry_night_faq,
    query_celestron_pdfs,
    query_youtube
]

multi_collection_agent = Agent(
    name="AstraDB Multi-Collection RAG Agent",
    model=OpenAIChat(id="gpt-3.5-turbo"),
    tools=tools,
    description="Retrieves and synthesizes information from multiple AstraDB collections.",
    # Add any instructions or config here if needed
)

# Register all agents for the Playground UI
agents = [multi_collection_agent]
# Optionally, add more: agents.append(get_web_agent(...)), etc.

app = Playground(agents=agents).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
