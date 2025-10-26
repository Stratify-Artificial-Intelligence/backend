# Veyra - Backend

Veyra is an expert AI business mentor that helps you solve problems in your company, discover opportunities, and guides you step by step.


## Introduction & core concepts

Veyra Backend provides a REST API and background services for an AI-powered business mentor platform. It enables users to register and authenticate, create and manage business records and ideas, interact with AI-driven chat assistants tied to businesses, store and retrieve chat messages, manage subscription plans and payments, and run scheduled or long-running research workflows.

The app defines a set of core domain concepts:
- **User**: Represents an application user (an individual account). Users have roles (for example: basic, admin, service), language preferences, and may have subscription or credit balances. Typical user operations exposed by the API: create account, read profile, update profile, list users (admin), and deactivate/reactivate.
- **Business**: Represents a business or business idea owned by a user. The repo models different business stages (idea, established) and stores business metadata (name, description, team, financial fields, location, and optional assets). Typical operations: create business (idea or established), read business details, update business, list businesses for a user, and delete business (admin or owner).
- **Chat**: A conversational session tied to a business that records an interaction with an AI assistant. Chats have metadata (title, start time, external/internal IDs) and a sequence of messages. Typical operations: create chat, list chats for a business, get chat details (including messages), and archive or delete chats.
- **Message** (ChatMessage): An item in a chat representing either user input, assistant output, or system messages. Messages track sender, timestamp, content and can be published to the AI model pipeline. Typical operations: add message to a chat, stream assistant responses (when supported), list messages, and delete messages.
- **Plan & subscription**: Product definitions and subscription state that control user access tiers, monthly credits, and billing metadata. Operations include listing available plans, subscribing/unsubscribing a user, handling webhook events from the payment processor to reconcile subscription state, and administratively updating plan metadata.

Primary REST resources and typical endpoints:
- `/users` — user registration, profile retrieval, profile update, admin list/search, and role/activation management.
- `/businesses` — create / update / read / delete businesses and transition business stage (idea <-> established); listing businesses scoped to the authenticated user or admin queries.
- `/chats` — create a new chat for a business, list chats, get chat details and metadata, archive/delete chat.
- `/chats/{chat_id}/messages` — append messages, stream assistant responses where applicable, list and delete messages.
- `/plans` — public list of available plans and plan metadata.
- `/subscriptions` — actions for subscribing a user to a plan, viewing subscription status, and webhook endpoints used by the payment provider to notify the app of billing events.
- `/admin` — administrative endpoints for system maintenance, plan creation, and data reconciliation (requires admin role).
- Additional endpoints include file upload/download (signed URLs), RAG/search endpoints for knowledge retrieval, health and diagnostics endpoints used by deploy tooling and monitoring.
- The API enforces role-based access checks (admin, service, user types) and supports service tokens and impersonation flows (with explicit checks to prevent misuse). Authorization logic is implemented as dependency-injected checks so endpoints declare required roles or permission predicates.


## Integrations and external services

The application integrates with a range of external services to enable AI-driven features, authentication, payments, storage, and orchestration.

The design intentionally keeps these integrations provider-agnostic so implementations can be swapped with configuration. This is done through patterns such as adapters and factories to abstract provider-specific details away from business logic.

### AI & embeddings
The backend connects to external AI model providers for conversational assistants and to separate embedding providers that produce vector representations used by retrieval-augmented generation (RAG). The codebase separates chat/assistant models from embedding models so different providers or models can be used for each purpose.

Technologies used are:
- **OpenAI** (SDK and tokenizer utilities) — used for chat/embedding calls and tokenization utilities.
- **Anthropic** (SDK) — used as an alternative chat model provider in configuration.
- **Perplexity** (HTTP client integration) — used as a deep-research provider in some flows.
- **Pinecone** (vector index client) — used as the external vector store for embeddings and semantic retrieval.

### Identity & authentication
The system delegates authentication and identity management to a third-party identity provider. The application verifies tokens server-side, fetches user info, and optionally uses client-side SDKs to enable interactive login experiences during development. 
Token validation, impersonation checks, role-based access control, and service-user tokens are handled by thin helper/services layers so changing the identity provider requires minimal code changes.

To do so, **Firebase Authentication** is used as the identity provider in this codebase. Both server-side SDK integrations and client-side SDK injection into Swagger UI are implemented.

### Payments & subscriptions
Payment flows are implemented through an external payment processor: the integration handles product/price creation, subscription lifecycle, webhooks for asynchronous events (invoices, payments, cancellations), and mapping the external payment state to local subscription and plan models.

The external payment processor used in this codebase is **Stripe**, with SDK usage for API calls and webhook signature validation.

### File storage
The application offloads file storage to **AWS S3** (via SDK) for object storage, signed URL generation, and larger object handling to external object storage services.

### Cloud orchestration
The application delegates long-running or asynchronous tasks to cloud-based orchestration/scheduler services via small service interfaces. This allows workflows such as periodic tasks, delayed jobs, or complex state machines to be managed outside the application code.
To do so, the codebase references **AWS Step Functions and EventBridge** as orchestration services integrated.


## Technologies & dependencies
Primary runtime and framework
- Python 3.10 (project configured for Python 3.10+)
- FastAPI (`fastapi`) — ASGI web framework used to implement the REST API
- Uvicorn (`uvicorn`) — ASGI server used to run the application

Data layer
- SQLAlchemy 2.x (`sqlalchemy`) — async ORM and models
- asyncpg (`asyncpg`) — async PostgreSQL driver used by SQLAlchemy
- Alembic (`alembic`) — migration tool (migrations live in `app/alembic`)
- psycopg2-binary (`psycopg2-binary`) — Postgres adapter used in some contexts

Configuration & validation
- Pydantic v2 (`pydantic`) and `pydantic-settings` — typed settings and validation for environment configuration

AI, embeddings and vector DB
- OpenAI (`openai`) and `tiktoken` — OpenAI SDK and tokenizer utilities
- Anthropic (`anthropic`) — alternative chat model provider SDK
- Pinecone (`pinecone[asyncio]`) — vector database client used for embedding storage and queries
- Perplexity (HTTP integration via `requests`) — used as a deep-research provider in some flows
- `requests` — synchronous HTTP client used where needed

Payments, identity, storage and cloud
- Stripe (`stripe`) — payment and subscription management, webhook handling
- Firebase Admin (`firebase-admin`) — identity/integration utilities for auth flows
- Boto3 (`boto3`) — AWS SDK used for S3 and orchestration integrations (step functions, eventbridge)
- python-multipart (`python-multipart`) — form / file upload handling support

Utilities, testing and development
- Poetry (`poetry`) — dependency and packaging management (`pyproject.toml`)
- Tox (`tox`) — configured test & quality environments (see `tox.ini`)
- Pytest (`pytest`) and `pytest-asyncio` — test framework for sync and async tests
- httpx (`httpx`) — test HTTP client
- freezegun (`freezegun`) — time-freeze utility for tests
- Black (`black`) — code formatter (configured with line-length 89 and skip string normalization)
- Flake8 (`flake8`) and `flake8-quotes` — linter and quote style enforcement
- Mypy (`mypy`) — static type checking

See `pyproject.toml` for exact pinned versions and the `tox.ini` file for quality tooling configuration.


## Development: Running, seeds, and tests

### Set up the virtual environment
Check that you have pyenv
```bash
pyenv versions
```

Create a virtual environment with the Python version in `pyproject.toml`, in this case 3.10
```bash
pyenv virtualenv 3.10 veyra-backend
```

Check that the environment was created successfully
```bash
pyenv virtualenvs
```

Assign the virtual environment to the actual repo
```bash
pyenv local mvp-backend
```

Update and resolt the dependencies
```bash
poetry lock
```

Install the dependencies from the lock file
```bash
poetry install
```


### Running locally

1. Copy `.env.example` to `.env` and fill missing values (like service keys).

2. Start dependencies and the app using docker-compose (project includes a `docker-compose.yml` at the repository root).
    ```bash
    docker compose up -d
    ```
   Behavior of `prestart.sh` inside the container:
   - `prestart.sh` runs Alembic migrations (`alembic upgrade head`).
   - If `DOMAIN=localhost`, it will run `app/database/init_db.py` to seed initial data.
   - It then launches Uvicorn (with `--reload` when `DOMAIN=localhost`).

3. You can open your browser and interact with these URLs:
   - **Swagger UI documentation** (from the OpenAPI backend): http://localhost/docs
   - **PGAdmin**, PostgreSQL administration UI: http://localhost:5050

4. To check the logs, run:
    ```bash
    docker compose logs
    ```

5. To stop the stack, run:
    ```bash
    docker compose down
    ```


### Alembic migrations
Alembic is configured under `backend/app/alembic` with scripts in `backend/app/alembic/versions/`. `backend/alembic.ini` present and `script_location` points to `app/alembic`.

See instructions in [backend/app/alembic/README.md](backend/app/alembic/README.md) for more details and commands.


### Testing
If your stack is already up and you just want to run the tests, you can use:
```bash
docker compose exec backend pytest -v --doctest-modules
```


### Code quality & tooling

This project includes a small toolchain to enforce style (`black`), linting (`flake8`) and type checks (`mypy`). The configuration is present in `tox.ini` and `pyproject.toml` and uses `poetry` to install dev dependencies.
```bash
# Run all configured tox environments (may be slow because it runs install steps)
tox

# Run only the flake8 environment
tox -e flake8

# Run the black check (will fail if formatting is needed)
tox -e black-check

# Run mypy checks
tox -e mypy
```
