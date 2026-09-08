# AI-Powered Multi-Agent Smart Agriculture Marketplace

[![Status](https://img.shields.io/badge/status-active%20development-2ea44f)](#development-status)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async%20API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

> An ongoing, production-oriented AI engineering project that combines multi-agent decision support, machine learning, computer vision, retrieval-augmented generation, and a direct farm-to-market marketplace.

## Project overview

The platform is being engineered to help farmers make data-informed decisions and sell agricultural products directly to wholesalers and large-scale buyers. Its target architecture combines a secure cloud-native API, specialized AI agents, predictive models, agricultural knowledge retrieval, and marketplace workflows in one system.

The current release establishes the backend foundation: asynchronous FastAPI services, PostgreSQL persistence, database migrations, JWT authentication, CRUD APIs, and a reproducible Docker environment. The AI agents, marketplace UI, machine-learning services, cloud deployment, and production observability are being delivered incrementally.

## Development status

| Capability | Status | Scope |
| --- | --- | --- |
| FastAPI backend foundation | Implemented | Async API structure, validation, and interactive API documentation |
| PostgreSQL data layer | Implemented | Users, chat history, and forecast history |
| SQLAlchemy and Alembic | Implemented | Async persistence and version-controlled schema migrations |
| JWT authentication | Implemented | Registration, login, access tokens, and protected endpoints |
| Docker environment | Implemented | FastAPI and PostgreSQL start through Docker Compose |
| Weather agent and MCP tools | Next | Location-aware weather analysis through an external weather API |
| LangGraph multi-agent system | Planned | Supervisor-agent orchestration and specialized agent workflows |
| Smart marketplace | Planned | Product listings, buyers, wholesalers, and direct trading workflows |
| Price forecasting | Planned | XGBoost-based agricultural market price prediction |
| Plant disease diagnosis | Planned | YOLO11 image-based disease detection |
| Agricultural RAG | Planned | Qdrant retrieval over manuals, publications, and cultivation guides |
| Frontend application | Planned | Farmer and buyer experiences built with Next.js |
| MLOps and cloud delivery | Planned | GitHub Actions, AWS deployment, and scalable inference services |
| Agent observability | Planned | LangSmith tracing, debugging, and evaluation |

## Target platform capabilities

### Multi-agent agricultural intelligence

A LangGraph supervisor will coordinate specialized agents and route each farmer request to the appropriate capability:

- **Weather Agent:** gathers weather data and provides location-aware farming insights through MCP-based tool calling.
- **Crop Recommendation Agent:** combines soil, climate, season, and historical information to recommend suitable crops.
- **Market Intelligence Agent:** uses XGBoost to estimate future agricultural prices and support selling decisions.
- **Plant Disease Agent:** uses YOLO11 to detect likely crop diseases from uploaded plant images.
- **Knowledge Agent:** retrieves evidence from agricultural manuals, research publications, and cultivation guidelines.

### Direct farm-to-market marketplace

The planned marketplace will allow farmers to list products, review current and forecasted prices, and connect directly with wholesalers and large-scale buyers. The objective is to improve price transparency and reduce unnecessary dependency on intermediaries.

### Retrieval-augmented recommendations

Agricultural documents will be embedded and indexed in Qdrant. The retrieval pipeline will provide relevant context to the agents so recommendations can be grounded in domain material instead of relying only on a model's internal knowledge.

### Production-oriented AI delivery

Application and inference services will be containerized with Docker, validated through GitHub Actions, and deployed to AWS. LangSmith will provide traces for agent decisions, tool calls, latency, failures, and multi-agent execution paths.

## Target architecture

```mermaid
flowchart LR
    U[Farmers and Buyers] --> WEB[Next.js Web Application]
    WEB --> API[FastAPI API]
    API --> AUTH[JWT Authentication]
    API --> MARKET[Marketplace Services]
    API --> SUP[LangGraph Supervisor]

    SUP --> WEATHER[Weather Agent]
    SUP --> CROP[Crop Recommendation Agent]
    SUP --> PRICE[Market Forecast Agent]
    SUP --> DISEASE[Plant Disease Agent]
    SUP --> KNOWLEDGE[Knowledge Agent]

    WEATHER --> WAPI[Weather API via MCP]
    PRICE --> XGB[XGBoost Model]
    DISEASE --> YOLO[YOLO11 Model]
    KNOWLEDGE --> QDRANT[Qdrant Vector Database]

    AUTH --> PG[(PostgreSQL)]
    MARKET --> PG
    API --> PG
    SUP --> LANGSMITH[LangSmith Observability]

    API -. containerized deployment .-> AWS[AWS]
```

Dashed and AI-specific paths represent the target architecture and will be activated as their roadmap phases are completed.

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, asynchronous request handling |
| Data | PostgreSQL, SQLAlchemy, Alembic, asyncpg |
| Agent orchestration | LangGraph, MCP, tool calling |
| Retrieval | Qdrant, embeddings, RAG |
| Machine learning | XGBoost, feature engineering, price forecasting |
| Computer vision | YOLO11, image preprocessing, disease detection |
| Frontend | Next.js, TypeScript |
| Security | JWT authentication, password hashing, protected APIs |
| Infrastructure | Docker, Docker Compose, AWS |
| Delivery and observability | GitHub Actions, automated testing, LangSmith |

## Current backend capabilities

- User, chat-history, and forecast-history CRUD operations
- PostgreSQL access through asynchronous SQLAlchemy sessions
- Alembic database migrations
- Password hashing and JWT access-token authentication
- Protected authenticated-user endpoints
- Pydantic request and response validation
- Swagger UI and OpenAPI documentation
- Docker Compose startup with a PostgreSQL health check

The API documentation is available at `http://127.0.0.1:8000/docs` while the application is running.

## Repository structure

```text
ai-farming-agent/
|-- backend/
|   |-- agents/           # Specialized AI agents
|   |-- api/              # FastAPI route modules
|   |-- core/             # Configuration and security
|   |-- database/         # Async database engine and sessions
|   |-- graph/            # LangGraph workflows and orchestration
|   |-- models/           # SQLAlchemy database models
|   |-- schemas/          # Pydantic request/response models
|   |-- services/         # Application and CRUD services
|   |-- tools/            # MCP and agent tools
|   |-- alembic/          # Database migrations
|   |-- Dockerfile
|   `-- main.py
|-- frontend/             # Planned Next.js application
|-- docs/                 # Learning and architecture documentation
|-- docker-compose.yml
`-- README.md
```

## Run locally with Docker

### Prerequisites

- Git
- Docker Desktop with Docker Compose

### 1. Clone the repository

```powershell
git clone https://github.com/PiyumalRathnayake/ai-farming-agent.git
cd ai-farming-agent
```

### 2. Configure the backend

Create `backend/.env` and provide development values:

```env
DATABASE_URL=postgresql+asyncpg://farmer:farmer_password@postgres:5432/ai_farming
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Never commit the real `.env` file or production secrets.

### 3. Start the platform

```powershell
docker compose up --build
```

Docker Compose starts PostgreSQL, waits for its health check, applies Alembic migrations, and launches FastAPI.

### 4. Explore the API

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Stop the services with:

```powershell
docker compose down
```

## API foundation

| Area | Endpoints |
| --- | --- |
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Users | Create, list, read, update, and delete through `/users` |
| Chat history | CRUD operations through `/chat-history` |
| Forecast history | CRUD operations through `/forecast-history` |
| Health check | `GET /` returns `Hello AI Farmer` |
| Chat placeholder | `POST /chat` returns a static response until agent integration |

## Engineering focus

This project is intended to demonstrate practical AI engineering across the full product lifecycle:

- Designing modular, asynchronous REST APIs
- Securing APIs with password hashing and JWT authentication
- Managing relational schema evolution with Alembic
- Building model-driven agents with clear tool boundaries
- Orchestrating multi-agent workflows with LangGraph
- Combining predictive ML, computer vision, and RAG in one platform
- Containerizing services and automating CI/CD
- Deploying and observing AI workloads in a cloud environment

## Roadmap

- [x] FastAPI project foundation
- [x] PostgreSQL CRUD and Alembic migrations
- [x] JWT registration, login, and protected routes
- [x] Dockerized FastAPI and PostgreSQL services
- [ ] MCP-powered Weather Agent
- [ ] LangGraph supervisor and agent routing
- [ ] Crop recommendation workflow
- [ ] XGBoost market-price forecasting pipeline
- [ ] YOLO11 plant-disease diagnosis service
- [ ] Qdrant agricultural RAG pipeline
- [ ] Next.js farmer and buyer marketplace
- [ ] Automated test and deployment workflows with GitHub Actions
- [ ] AWS infrastructure and production deployment
- [ ] LangSmith tracing, evaluation, and monitoring

## Professional summary

**AI-Powered Multi-Agent Smart Agriculture Marketplace Platform | Ongoing**

Engineering a cloud-native platform that combines specialized AI agents, predictive machine learning, computer vision, retrieval-augmented generation, and direct agricultural trading. The system is designed around a LangGraph supervisor architecture with weather, crop-recommendation, market-forecasting, plant-disease, and agricultural-knowledge agents. Its implemented foundation includes an asynchronous FastAPI backend, PostgreSQL persistence, SQLAlchemy, Alembic migrations, JWT authentication, and Docker Compose. Planned delivery includes a Next.js marketplace, Qdrant-backed RAG, XGBoost price forecasting, YOLO11 disease diagnosis, GitHub Actions CI/CD, AWS deployment, and LangSmith observability.

---

Built as an ongoing AI engineering portfolio project focused on reliable APIs, agentic system design, applied machine learning, and production-ready delivery.
