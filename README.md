# RAG (Retrieval Augmented Generation) System

A FastAPI-based RAG system with multi-tenant support, document management, and semantic search capabilities.

## Project Structure 

├── app/
│ ├── api/
│ │ ├── dependencies/ # Dependency injection
│ │ ├── models/ # Pydantic models
│ │ └── routes/ # API endpoints
│ ├── services/ # Business logic
│ │ ├── bulk_upload.py
│ │ ├── completion.py
│ │ ├── embedding.py
│ │ ├── rag.py
│ │ └── supabase.py
│ ├── config.py # Configuration settings
│ └── main.py # FastAPI application
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md

## Features

- Multi-tenant support
- Document management
- Semantic search
- RAG with GPT-4o-mini
- Supabase integration
- FastAPI framework
- Dependency injection
- Pydantic models
- Logging
- Error handling
- API documentation (Swagger UI)

## Prerequisites

- Python 3.10+
- Docker
- Docker Compose
- Supabase account
- OpenAI API key

## Environment Setup

1. Copy the example environment file:
```
cp .env.example .env
```
2. Update the .env file with your Supabase credentials and OpenAI API key.

## Running with Docker

1. Build and start the Docker container:
```
docker-compose up --build
```
2. Access the API documentation at http://localhost:8000/docs.

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Documents
- `POST /documents` - Create document
- `GET /documents` - List documents

### Search
- `POST /search/query` - Search documents and generate response

### Bulk Upload
- `POST /upload/csv` - Upload documents via CSV
- `POST /upload/json` - Upload documents via JSON

## License
This project is open-sourced under the MIT License - see the LICENSE file for details.

