# Sequential Flow of the Infrastructure Layer

## 📌 Introduction
This document details, from a technical and design perspective (Clean Architecture), the sequential workflow that occurs within the `src/infrastructure/` directory.

The single and primary responsibility of this layer is to **set the stage**: configure the web server, establish and validate connections with external agents (Databases and Cache), and assemble the application before it is executed.

---

## 📥 1. Sequence Inputs
The process within `infrastructure` does not occur in isolation. It is triggered and fueled by external stimuli:

1. **Environment Variables (`.env`):** These are the raw materials. They provide the credentials, ports, and hosts needed to connect the services.
2. **Entry Point (`src/main.py`):** This is the starter trigger. `main.py` invokes the infrastructure, requesting it to build the application (typically by calling `create_application()`).

---

## ⚙️ 2. Internal Sequential Flow

Once `main.py` triggers the build process, the infrastructure layer executes the following chronological steps:

### Step 2.1: Configuration Loading and Validation (`setting.py`)
Before instantiating anything, the system reads the "rules of the game" using `pydantic_settings`.
* **PostgreSQL:** The file `infrastructure.db.postgres.setting` maps the Postgres environment variables and dynamically builds the connection URL (`get_postgres_url`).
* **Redis:** The file `infrastructure.db.redis.setting` does the same, ensuring the correct structure of the URI for the in-memory engine.

### Step 2.2: Connection Clients Preparation (`connection.py`)
With the URLs ready, the artifacts that will communicate with the data engines are prepared:
* **For PostgreSQL:** In `infrastructure.db.postgres.connection`, the SQLAlchemy `engine` (the main motor), the session factory (`session_local`), and the dependency injector (`get_db()`) are created.
* **For Redis:** In `infrastructure.db.redis.connection`, `redis_client` (the asynchronous client for the cache) is instantiated.

### Step 2.3: Server Structural Assembly (`server/setting.py`)
The backbone of the HTTP API begins to be assembled:
* The `FastAPI` class is instantiated, receiving the project metadata (title, description, version).
* The lifecycle manager (`lifespan`) is attached to it.
* **(External Interaction):** The server includes the router coming from the `presentation` layer. This is the only functional outward dependency of the infrastructure; it couples the exposure logic (endpoints) to the web server.

### Step 2.4: Lifecycle Management (`server/lifespan.py`)
Before declaring that the application is ready, the `lifespan` acts as a security guard in three phases:
1. **Startup:**
   - Executes a `SELECT 1` to ensure PostgreSQL is responding.
   - Executes a `.ping()` to confirm Redis is alive.
   - Stores the `engine` and the `redis_client` in `app.state` so they are globally available.
2. **Execution (`yield`):** The process pauses, and the server becomes "Ready to receive requests".
3. **Shutdown:** If the server receives a shutdown command, this script comes back into action to destroy the Postgres connection pool (`engine.dispose()`) and asynchronously close Redis (`redis_client.aclose()`), guaranteeing no orphan processes or memory leaks remain.

### Step 2.5: Final Wrapper (`server/server.py`)
The `create_application()` function wraps the entire previous process into a unified and clean step.

---

## 📤 3. Sequence Outputs
The cycle ends when the infrastructure returns its final product:

* **Ready Application:** It returns the fully assembled `FastAPI` instance back to `main.py`. This instance already has its DB and Cache connections validated, contains the global configuration, the injected presentation routes, and its lifecycle manager tied to the instance.
* **Assigned Execution:** From this moment on, the flow exits the `infrastructure` layer, and the responsibility of bringing up the listening port and routing network traffic falls on the ASGI server (such as Uvicorn), which was originally called from the project root.
