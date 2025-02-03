# RAG (Retrieval Augmented Generation) System

A FastAPI-based RAG system with multi-tenant support, document management, and semantic search capabilities.

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── auth.py          # Authentication dependencies
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── document.py      # Pydantic models for documents
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── bulk_upload.py   # Bulk document upload endpoints
│   │       ├── documents.py     # Document management endpoints
│   │       └── search.py        # Search and RAG endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bulk_upload.py      # Bulk upload processing
│   │   ├── completion.py       # OpenAI completion service
│   │   ├── embedding.py        # OpenAI embedding service
│   │   ├── rag.py             # RAG orchestration service
│   │   └── supabase.py        # Supabase database service
│   ├── config.py              # Application configuration
│   └── main.py               # FastAPI application entry point
├── docker/                   # Docker configuration files
├── tests/                    # Test files
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
├── docker-compose.yml      # Docker compose configuration
├── Dockerfile              # Docker build instructions
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Features

- Multi-tenant document management
- Semantic search using OpenAI embeddings
- RAG-powered question answering
- Bulk document upload (CSV/JSON)
- Authentication and authorization
- Supabase vector store integration
- FastAPI REST API
- Docker containerization
- Comprehensive logging
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

