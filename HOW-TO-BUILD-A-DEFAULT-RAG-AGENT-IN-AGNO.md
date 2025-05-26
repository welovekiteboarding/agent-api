# HOW-TO-BUILD-A-DEFAULT-RAG-AGENT-IN-AGNO

## 1. Base Agno Agent (No RAG)
This is the simplest Agent—no RAG, just a language model and (optionally) basic tools.

**Step-by-step:**
- Install Agno and dependencies (if you haven’t):
  ```sh
  pip install agno openai
  ```
- Import Agno’s Agent and Model:
  ```python
  from agno.agent import Agent
  from agno.models.openai import OpenAIModel
  ```
- Instantiate the Agent:
  - Define your LLM of choice (e.g., OpenAI’s GPT-3.5-turbo).
  - No tools are necessary for a minimal example.
- Run the Agent:
  - The agent simply passes text prompts to the LLM.

**Base Agent Code:**
```python
from agno.agent import Agent
from agno.models.openai import OpenAIModel

# 1. Set up the model
model = OpenAIModel(model_name="gpt-3.5-turbo")  # Replace with your preferred model

# 2. Initialize the agent (no tools needed for this base case)
agent = Agent(model=model)

# 3. Run the agent
response = agent.run("What is Agno?")
print(response)
```

---

## 2. Base Agno Agent that Uses RAG (Local Vector Store)
Here, the agent first retrieves relevant information from a vector database, then augments the LLM’s answer with the retrieved context.

**Step-by-step:**
- Install vector DB and embedding dependencies:
  ```sh
  pip install agno sentence-transformers
  ```
- Import the local vector DB Tool:
  - Agno typically provides a ready-to-use tool for local vector storage/retrieval.
- Set up the vector DB Tool:
  - Choose an embedding model (e.g., all-MiniLM-L6-v2).
  - Provide a storage location for the local database.
- Attach the Tool to the Agent:
  - The agent can incorporate multiple tools; for RAG, it needs both a vector DB tool and an LLM.
- Run the RAG Agent:
  - The agent retrieves, then generates an augmented answer.

**Base RAG Agent (Local) Code:**
```python
from agno.agent import Agent
from agno.tools.local_vectordb import LocalVectorDBTools
from agno.models.openai import OpenAIModel

# 1. Configure the embedding model and storage path for local vector DB
vectordb_tool = LocalVectorDBTools(
    embeddings_model="sentence-transformers/all-MiniLM-L6-v2",
    vector_store_path="./local_vectordb"
)

# 2. Set up the language model
model = OpenAIModel(model_name="gpt-3.5-turbo")

# 3. Initialize the RAG agent with the vector DB tool
agent = Agent(
    tools=[vectordb_tool],
    model=model,
)

# 4. Run a retrieval-augmented query
response = agent.run("What is quantum entanglement?")
print(response)
```

---

## 3. Base Agno Agent that Uses RAG via AstraDB (Datastax)
This agent retrieves information from one or more AstraDB-hosted databases, then generates context-grounded answers.

**Step-by-step:**
- Install required dependencies:
  ```sh
  pip install agno openai requests
  ```
- (Optional) Check for a dedicated Agno AstraDB tool.
- If not available, create your own using Agno’s Tool base class and AstraDB’s REST API.
- Implement the AstraDB Retrieval Tool:
  - This tool should:
    - Receive queries.
    - Call the AstraDB vector search REST endpoint.
    - Return relevant matched documents.
- Configure one or more AstraDB tools (one per DB):
  - Each tool is initialized with endpoint, API key, collection name, etc.
- Assemble the Agent:
  - Use these AstraDB tools (or just one, if starting simple) and the LLM.
- Run the RAG Agent:
  - The agent will fetch context from AstraDB and generate an answer.

**Base AstraDB RAG Agent Code:**
```python
from agno.agent import Agent, Tool
from agno.models.openai import OpenAIModel
import requests
from typing import List

# 1. Define a custom tool for AstraDB retrieval
class AstraDBRetrievalTool(Tool):
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

# 2. Configure tool(s) for each AstraDB
db_config = {
    "endpoint": "https://<db>.apps.astra.datastax.com",
    "api_key": "<ASTRADB_API_KEY>",
    "collection": "<collection>"
}

vectordb_tool = AstraDBRetrievalTool(**db_config)

# 3. Set up the language model
model = OpenAIModel(model_name="gpt-3.5-turbo")

# 4. Create the RAG agent with the AstraDB tool
agent = Agent(
    tools=[vectordb_tool],
    model=model,
)

# 5. Run a RAG query
response = agent.run("What is quantum entanglement?")
print(response)
```
To use multiple AstraDBs:
Repeat the tool initialization for each DB and pass all tools to the agent:
```python
tools = [AstraDBRetrievalTool(**cfg) for cfg in astra_db_configs]
agent = Agent(tools=tools, model=model)
```

---

## 4. Implementing Multi-Collection RAG in Agno using AstraDB

AstraDB is a fully managed vector database by Datastax. Agno can use it as a retrieval backend for RAG agents. This is the recommended approach for production and scalable use cases.

**How Collections Work in AstraDB**
- In AstraDB, a “collection” is essentially a table or document group under a namespace.
- Each collection can hold different kinds of knowledge (e.g., skysafari, YouTube, etc.).
- For vector search, you target a collection with your search queries.

**How to Implement Multi-Collection RAG in Agno**
- For each collection, create an AstraDBRetrievalTool instance pointed at that specific collection.
- Pass all tools to your Agno Agent. The Agent will then be able to query across all collections.

#### Example: Multi-Collection AstraDB RAG Agent

```python
from agno.agent import Agent, Tool
from agno.models.openai import OpenAIModel
import requests
from typing import List
import os

class AstraDBRetrievalTool(Tool):
    """
    Agno-compatible Tool for an AstraDB vector collection.
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
            print(f"Error querying AstraDB collection {self.collection}: {e}")
            return []

# Shared AstraDB params loaded from environment for security:
astra_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
astra_api_key = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

collection_names = [
    "skysafari",
    "starrynight",
    "starry_night_faq",
    "celestron_pdfs",
    "YouTube"
]

# Make one tool per collection:
tools = [
    AstraDBRetrievalTool(
        endpoint=astra_endpoint,
        api_key=astra_api_key,
        collection=coll
    )
    for coll in collection_names
]

# Standard LLM setup:
model = OpenAIModel(model_name="gpt-3.5-turbo")

# Agent setup with all tools:
agent = Agent(
    tools=tools,
    model=model,
)

# Test query:
response = agent.run("What is the best telescope for a beginner?")
print(response)
```

#### Key Notes & Best Practices
- **One Tool per Collection:** Each tool targets a single collection. This lets Agno's agent route or synthesize responses from multiple knowledge domains.
- **If Collections are on Different DBs:** If your collections exist in different AstraDB databases (different endpoints/API keys), repeat the process above, just use each DB’s unique parameters.
- **Routing/Combining Results:** By default, the agent queries all available tools. You can build more advanced logic (e.g., only query some tools for certain tasks, merge/score results, etc.).
- **Error Handling:** The try/except in the tool means your agent will not crash if an AstraDB query fails for one collection.

**Summary Table**

| Collection         | Tool Name             | Notes                        |
|--------------------|----------------------|------------------------------|
| skysafari          | AstraDB:skysafari    | For SkySafari data           |
| starrynight        | AstraDB:starrynight  | For Starry Night data        |
| starry_night_faq   | AstraDB:starry_night_faq | For Starry Night FAQ   |
| celestron_pdfs     | AstraDB:celestron_pdfs| Celestron manuals/guides    |
| YouTube            | AstraDB:YouTube      | YouTube transcripts/embeddings|

---

## Summary Table
| Type                 | Retrieval (RAG)      | Storage                    | When to Use                                  |
|----------------------|----------------------|----------------------------|----------------------------------------------|
| 1. Base Agent        | No                   | None                       | Simple LLM Q&A, no grounding/citations       |
| 2. RAG (Local)       | Yes (local vectordb) | Local file/db              | Prototyping, dev with your own small datasets|
| 3. RAG (Astra)       | Yes (remote AstraDB) | Managed by Datastax (cloud)| Scalability, team access, production workloads|
| 4. Multi-Collection RAG (Astra) | Yes (remote AstraDB) | Managed by Datastax (cloud)| Scalability, team access, production workloads with multiple collections|

### Typical Setup
A default RAG Agent in Agno uses a local or built-in vector store for retrieval, and a supported LLM (like OpenAI or HuggingFace models) for generation. Here’s how it generally works:

1. User provides a query.
2. Agent retrieves relevant documents from a vector database or knowledge base.
3. Agent generates an answer using the LLM, grounding the response in the retrieved context.

### Sample Code (Default RAG Agent)
```python
# agno_agent_rag_default.py
from agno.agent import Agent
from agno.tools.local_vectordb import LocalVectorDBTools
from agno.models.openai import OpenAIModel  # Or your chosen model

# Set up the local vector DB tool
vectordb_tool = LocalVectorDBTools(
    embeddings_model="sentence-transformers/all-MiniLM-L6-v2",
    vector_store_path="./local_vectordb"
)

# Set up the Agent
agent = Agent(
    tools=[vectordb_tool],
    model=OpenAIModel(model_name="gpt-3.5-turbo"),  # Example model
)

# Run Retrieval-Augmented Generation
query = "Explain quantum entanglement."
response = agent.run(query)
print(response)
```

### Pros (Default Setup)
- Simple: Easy to set up, runs locally.
- Flexible: Any decent vector DB or file-based store can be plugged in.
- Fast for small/mid-scale: Minimal network or cloud dependency.
- No hosting cost: Good for dev/test, and total control of your data.

### Cons (Default Setup)
- Scale/Performance: Not ideal for large vector stores or high concurrency.
- Redundancy/Backup: Responsibility’s on you.
- Limited Sharing: Not ideal for team or distributed apps.
- Reliability: Dependent on local environment.

---

## 2. Building a RAG Agent Using 5 AstraDBs Hosted on Datastax

### How This Changes
Instead of a local store, your agent queries multiple remote AstraDB (Datastax's managed Cassandra + vector search) databases.
- Use or create a tool integrating with AstraDB’s APIs.
- The agent can route queries across your 5 databases, or intelligently select which DB(s) to use per query.

### Sample Code (Multi-AstraDB Setup)
*Pseudocode—confirm Agno's AstraDB integration specifics as needed!*
```python
from agno.agent import Agent
from agno.tools.datastax_astra import AstraDBTools
from agno.models.openai import OpenAIModel

# Example of setting up tools for each AstraDB tenant
astra_db_tools = [
    AstraDBTools(
        api_endpoint=db["endpoint"],
        api_key=db["api_key"]
    )
    for db in list_of_astra_db_configs  # You provide 5 configs
]

agent = Agent(
    tools=astra_db_tools,
    model=OpenAIModel(model_name="gpt-3.5-turbo"),
)

query = "Explain quantum entanglement."
response = agent.run(query)
print(response)
```
*Note: Implementation details may depend on Agno’s specific tool for AstraDB. Confirm tool names, config patterns, and multi-DB routing best practices via the knowledge base as needed.*

### Pros (AstraDB)
- Scalable: Handles large datasets and search efficiently.
- Highly Available: Managed by Datastax (reliability, backups, etc.).
- Real-Time Collaboration: Good for distributed teams/products.
- Advanced Search: Use AstraDB's semantic/vector features across disparate knowledge domains.
- Security: Managed RBAC, audit, and encrypted access.

### Cons (AstraDB)
- Latency: Cloud network roundtrips may be slower than local.
- Complexity: Requires API keys, config management—especially with 5 DBs!
- Cost: AstraDB is a paid cloud service.
- Access Management: Need to coordinate user/role security.

---

## Recommendations
### For Prototyping & Small Scale:
Start with a local vector DB. It’s fast, simple, and cheap for proof of concepts, dev, and isolated analyses.

### For Production, Large Scale, or Team-Based Apps:
AstraDB is strongly preferred. Its scalability, availability, and power make it worth the network/cost complexities, especially if you need to span multiple data domains (hence five DBs).

### Hybrid:
Start local, switch to AstraDB as your needs grow, or even support both in one Agent (Agno is flexible this way).

---

## Example: Custom AstraDB Tool Pattern
```python
# agno_rag_multiastradb.py
from agno.agent import Agent, Tool
from agno.models.openai import OpenAIModel
import requests
from typing import List

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
        # Implement AstraDB REST call for vector search
        url = f"{self.endpoint}/api/rest/v2/namespaces/default/collections/{self.collection}/vector-search"
        payload = {"query": query, "topK": 5}
        headers = {"x-cassandra-token": self.api_key, "Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            hits = response.json().get("documents", [])
            return [hit["document"]["content"] for hit in hits]
        except requests.RequestException as e:
            # Error handling: return empty or log error
            print(f"Error querying AstraDB: {e}")
            return []

# -- Setup multiple AstraDB tool instances --
astra_dbs = [
    {
        "endpoint": "https://<db1>.apps.astra.datastax.com",
        "api_key": "<ASTRADB_API_KEY_1>",
        "collection": "<collection1>"
    },
    # ... repeat for all 5 databases ...
]

tools = [
    AstraDBRetrievalTool(**db_config)
    for db_config in astra_dbs
]

# -- Instantiate the Agent with the custom tools --
agent = Agent(
    tools=tools,
    model=OpenAIModel(model_name="gpt-3.5-turbo"),
)

# -- Run a RAG Query --
query = "Explain quantum entanglement."
response = agent.run(query)
print(response)
```
**Notes:**
- Update endpoint, api_key, and collection for all 5 DBs.
- You could further merge/aggregate results within the Tool, or handle “which DB to search” with custom logic.

---

## Pros vs. Cons Recap
| Approach         | Pros                                         | Cons                                         | Recommended When                   |
|------------------|----------------------------------------------|----------------------------------------------|------------------------------------|
| Default (Local)  | Simple, low-cost, full control, fast for small data sets | Not scalable, limited collaboration, infra on you | Prototyping, dev, small data       |
| AstraDB (Remote) | Scale, reliability, managed features, collaboration-ready | Cost, complexity, config security/cloud dependency | Production, scaling, distributed/teams |

---

## Preferred Recommendation
- Prototype locally. When your app is validated and data/scale needs grow, migrate to AstraDB.
- If remotely hosted reliability/scale is required from the start, build for AstraDB directly as shown above.
- Tip: Review Agno’s base Tool and Agent docs for advanced routing (e.g., dynamic DB selection)—your architecture can evolve as your requirements do!
