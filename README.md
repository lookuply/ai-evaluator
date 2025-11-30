# Lookuply AI Evaluator

AI-powered page content evaluation service for Lookuply search engine.

## Features

- **LLM-based evaluation** using Llama 3.1 8B via Ollama
- **Quality scoring** (0.0-1.0 scale) with explanation
- **Multilingual support** for all EU languages
- **Anti-gaming design** - criteria configurable via ENV variables
- **Async/await** support for high throughput

## Components

### OllamaClient

Client for interacting with Ollama API:
- Text generation with system prompts
- Health checking
- Timeout and error handling

### PageEvaluator

Evaluates web page content quality:
- Analyzes title, text, and metadata
- Returns quality score (0.0-1.0)
- Provides reasoning for score
- Supports multilingual content

## Configuration

Environment variables (see `config.py`):

```bash
# Ollama configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M
OLLAMA_TIMEOUT=60

# Evaluation criteria (server-side secrets for anti-gaming)
MIN_CONTENT_LENGTH=100
MIN_QUALITY_SCORE=0.6
MAX_AD_RATIO=0.3

# Performance
EVALUATION_CACHE_TTL=3600
```

## Development

### Setup

```bash
# Install dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest --cov=src --cov-report=term-missing

# Lint
ruff check .

# Type check
mypy src/
```

### Testing

14 tests covering:
- Ollama client (7 tests)
- Page evaluator (7 tests)

All tests use mocked LLM responses for fast, reliable testing.

## Docker Deployment

The Docker image includes:
- Python 3.13
- Ollama server
- Llama 3.1 8B model (Q4_K_M quantized, ~4.9GB)

```bash
# Build
docker build -t ai-evaluator .

# Run
docker run -p 11434:11434 \
  -e OLLAMA_MODEL=llama3.1:8b-instruct-q4_K_M \
  ai-evaluator
```

**Note**: First startup takes ~5-10 minutes to download the model.

## Usage Example

```python
from ai_evaluator.ollama_client import OllamaClient
from ai_evaluator.page_evaluator import PageEvaluator

# Initialize
ollama = OllamaClient(
    base_url="http://localhost:11434",
    model="llama3.1:8b-instruct-q4_K_M"
)
evaluator = PageEvaluator(ollama_client=ollama)

# Evaluate page
content = {
    "title": "Python Best Practices",
    "text": "This comprehensive guide covers...",
    "url": "https://example.com/python-guide",
    "language": "en"
}

result = await evaluator.evaluate(content)

print(f"Score: {result.score}")  # 0.85
print(f"Useful: {result.is_useful}")  # True
print(f"Reason: {result.reason}")  # "Well-written, informative content"
```

## Architecture

```
┌─────────────┐
│  Crawler    │
│    Node     │
└──────┬──────┘
       │ content
       ↓
┌─────────────┐      ┌──────────┐
│     AI      │─────→│  Ollama  │
│  Evaluator  │      │  Server  │
└──────┬──────┘      └──────────┘
       │ score
       ↓
┌─────────────┐
│   Search    │
│    Index    │
└─────────────┘
```

## CI/CD

GitHub Actions workflows:
- **test.yml** - Run tests on every push/PR
- **deploy.yml** - Build and deploy to Hetzner server

Deployment:
1. Push to `main` branch
2. GitHub Actions builds Docker image
3. Image deployed to server
4. Container starts Ollama and pulls model
5. Service becomes available

## Performance

- **Latency**: ~2-5 seconds per evaluation (LLM inference)
- **Throughput**: ~10-20 pages/minute (single instance)
- **Memory**: ~8GB RAM (Ollama + model + overhead)
- **Model size**: 4.9GB (Q4_K_M quantization)

## License

Part of the Lookuply project.
