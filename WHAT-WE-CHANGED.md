# WHAT WE CHANGED

This document records all changes made to the default configuration, setup, or codebase that deviate from official documentation or the default state. Update this file with each change for transparency and reproducibility.

---

## [2025-05-25] Postgres Port Change for Docker Compose

**Reason:**
- The default Postgres port `5432` was already in use on the host system, causing Docker Compose to fail when starting the database container.

**Change:**
- In `compose.yaml`, changed the Postgres service host port mapping from `5432:5432` to `55432:5432`.

**Impact:**
- All connections to Postgres from the host (e.g., local tools, direct psql connections) must now use port `55432` instead of `5432`.
- No changes required for containers communicating over the Docker network (they still use `postgres:5432`).

**Action Required:**
- Update any local development tools or scripts that connect to Postgres via `localhost:5432` to use `localhost:55432`.

---



_Future changes should be documented here in the same format._
