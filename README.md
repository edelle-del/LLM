## LLM Microservices Demo

This project demonstrates a simple microservices architecture with:

- **Angular Frontend (`angular-client`)**: User-facing web app that sends prompts to the Spring Boot service.
- **Python API Gateway (`python-service`)**: Exposes an HTTP API to accept a prompt string and returns a result.
- **Java API Service (`java-llm-service`)**: Accepts prompt requests and forwards them to the Django LLM service.
- **Django LLM Service (`django-service`)**: Calls an external OpenAI-compatible LLM API and returns generated text.
- **Sample Client (`client`)**: Simple Python CLI that calls the Python API and prints the result.

All services can be run together using Docker and `docker-compose`.

### Architecture

1. The **client** sends a prompt to the **Python service** at `POST /api/generate`.
2. The **Python service** forwards the prompt to the **Java LLM service** at `POST /llm/generate`.
3. The **Java service** forwards the prompt to the **Django service** at `POST /llm/generate`.
4. The **Django service** calls the external LLM API and returns generated text.
5. The response flows back through **Java** and **Python** to the client.

### Angular to Spring Boot Flow

1. Open the Angular app at `http://localhost:4200`.
2. Enter a prompt and submit.
3. Angular calls Spring Boot at `POST http://localhost:8081/llm/generate`.
4. Spring Boot forwards to Django, then Django calls the configured LLM API.

### LLM Configuration

The Django service is configured through environment variables:

- `LLM_API_BASE_URL` (default in Docker: `https://api.groq.com/openai`)
- `LLM_API_CHAT_PATH` (default: `/v1/chat/completions`)
- `LLM_API_MODEL` (default in Docker: `llama-3.1-8b-instant`)
- `LLM_API_KEY` (required for real API calls)
- `LLM_API_MOCK_WHEN_MISSING_KEY` (default: `true`)

The Java service is configured to call Django using:

- `DJANGO_SERVICE_URL` (default in Docker: `http://django-service:8001`)
- `DJANGO_GENERATE_PATH` (default: `/llm/generate`)

If `LLM_API_KEY` is empty and `LLM_API_MOCK_WHEN_MISSING_KEY=true`, the Django service returns a mock response so the stack remains runnable for local demos.

### Requirements

- Docker and Docker Compose
- (Optional) Python 3.10+ for running the sample client outside Docker

### Running with Docker

From the `llm-microservices` directory:

```bash
docker compose up --build
```

To use a real LLM provider, set `LLM_API_KEY` in your shell before running `docker compose up --build`.

This will start:

- `angular-client` on `http://localhost:4200`
- `django-service` on `http://localhost:8001`
- `java-llm-service` on `http://localhost:8081`
- `python-service` on `http://localhost:8000`

### Testing the API directly

Once the containers are up:

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello from microservices!"}'
```

Expected JSON response:

```json
{
  "result": "...generated text from the configured LLM provider..."
}
```

### Running the sample client

1. (One-time) Create a virtual environment and install dependencies:

```bash
cd client
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt
```

2. With the Docker services running (`docker compose up`), run:

```bash
python client.py
```

3. Enter a prompt when asked. The client will:

- Call the Python API (`http://localhost:8000/api/generate`)
- Print the LLM-style response returned through the microservice chain

