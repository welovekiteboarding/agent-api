# HOW TO CONNECT TO DATASTAX ASTRA DB WITH PYTHON (ASTRAPY)

This guide explains how to connect your Python application to a Datastax Astra DB instance using the official `astrapy` client. It covers where, how, and why to use the connection details and token, and how this integrates with your RAG agent project.

---

## 1. **Why Use `astrapy` and a Service Token?**
- **Purpose:** `astrapy` is the official Python SDK for Astra DB, providing a convenient and secure way to interact with your Astra database (CRUD, vector search, admin tasks, etc.).
- **Service Token:** Required for authentication. It provides secure, role-based access to your Astra DB from code.

---

## 2. **Where to Apply the Information**
- **Token**: Used wherever your code needs to authenticate with Astra DB (e.g., in your `.env` file or directly in code for quick tests).
- **API Endpoint**: Used to specify which Astra DB instance your application should connect to.
- **In the Agent Project:**
    - For admin/setup tasks (like listing collections, loading data, or direct vector search), use `astrapy` in scripts or utilities.
    - For production RAG queries, you may use the REST API (as in your current agent), but `astrapy` can simplify and secure code for more complex operations.

---

## 3. **How to Apply the Information**

### a. **Install the SDK**
```sh
pip install --upgrade astrapy
```

### b. **Save Your Token**
- **Best Practice:** Store your token in a `.env` file or secret manager, not directly in code.
- Example `.env` entry:
  ```env
  ASTRA_DB_APPLICATION_TOKEN=AstraCS:...your_token_here...
  ASTRA_DB_API_ENDPOINT=https://<db_id>-<region>.apps.astra.datastax.com
  ```

### c. **Sample Connection Code**
```python
from astrapy import DataAPIClient
import os

# Load from environment for security
ASTRA_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")

client = DataAPIClient(ASTRA_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_ENDPOINT)

print(f"Connected to Astra DB: {db.list_collection_names()}")
```

- **Where:**
    - Use this code in setup scripts, admin utilities, or anywhere you need direct Python access to Astra DB.
    - For your RAG agent, you might use this for advanced operations or data loading/maintenance.

### d. **Official Docs**
- [Astrapy Docs](https://docs.datastax.com/en/astra-api-docs/_attachments/python-client/astrapy/index.html)

---

## 4. **Summary Table**
| Info Needed        | Where to Use                        | Why Needed                      |
|--------------------|-------------------------------------|---------------------------------|
| Application Token  | .env file, astrapy client           | Secure DB authentication        |
| API Endpoint       | .env file, astrapy client           | Identify the DB instance        |
| astrapy SDK        | Python scripts, agent utilities     | Pythonic DB access & admin      |

---

## 5. **Next Steps**
- Add your token and endpoint to your `.env` file.
- Use the sample code to verify connection.
- Integrate `astrapy` where direct Python DB access is needed (data load, schema, admin, or advanced RAG logic).

---

**Security Note:** Never commit your token to source control! Use environment variables or secret managers.
