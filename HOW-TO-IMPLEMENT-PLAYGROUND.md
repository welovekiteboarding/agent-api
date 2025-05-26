# HOW-TO-IMPLEMENT-PLAYGROUND

This document describes the key issues encountered and the solutions implemented to successfully integrate a multi-collection AstraDB RAG agent with the Agno Playground and Agent-UI.

## Summary
The goal was to make a multi-collection Retrieval-Augmented Generation (RAG) agent discoverable and functional in the Agno Playground, accessible via Agent-UI, retrieving real data from multiple AstraDB collections.

---

## Issues Encountered & Solutions Implemented

### 1. **Agent Not Discoverable in Agent-UI**
- **Issue:** The agent was not appearing in the Agent-UI.
- **Solution:** Ensured the agent was explicitly registered in the `agents` list in `playground.py` as per Agno documentation. Used the Playground pattern for agent registration.

### 2. **Tool Registration Not Recognized by Agno**
- **Issue:** Custom retrieval tools were not being called by the agent, resulting in only generic LLM answers.
- **Solution:** Replaced custom classes with function-based tools using the `@tool` decorator from `agno.tools.decorator`. Registered each collection as a separate decorated function and passed them in the agent’s `tools` list.

### 3. **Invalid Tool Names**
- **Issue:** Tools with names containing colons (e.g., `AstraDB:starrynight`) caused validation errors in Agent-UI (`tools[0].function.name` must match `^[a-zA-Z0-9_-]+$`).
- **Solution:** Renamed all tools to use only allowed characters (e.g., `astradb_starrynight`).

### 4. **Environment Variables Not Loaded**
- **Issue:** The agent could not access API keys from `.env`.
- **Solution:** Added `python-dotenv` and loaded environment variables at the top of `playground.py` with:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

### 5. **Playground Server Port Already in Use**
- **Issue:** Attempting to start the Playground server while it was already running caused an `Address already in use` error.
- **Solution:** Ensured to stop the running server (`Ctrl+C`) before restarting after code changes.

### 6. **AstraDB Retrieval Not Returning Data**
- **Issue:** The agent responded with generic information or failed to retrieve collection data.
- **Solution:**
    - Verified AstraDB endpoints, API keys, and collection names.
    - Added error logging in tool functions.
    - Ensured the request payload matched AstraDB’s API requirements.
    - Used specific queries to test retrieval.

---

## Final Working Solution
- Each AstraDB collection is exposed as a separate `@tool`-decorated function.
- All tools are registered in the agent’s `tools` list in `playground.py`.
- Environment variables are loaded at startup.
- Tool names use only valid characters.
- Playground server is restarted after changes.

---

## Troubleshooting Tips
- Check Playground server logs for errors when tools are called.
- Use specific queries that match known collection data.
- Ensure `.env` contains all required credentials and is loaded.
- Restart Playground after any code or environment changes.

---

This process ensures the agent is both discoverable and functional in Agent-UI, able to retrieve and synthesize information from multiple AstraDB collections using Agno best practices.
