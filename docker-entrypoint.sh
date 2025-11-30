#!/bin/bash
set -e

echo "Starting Ollama server..."
# Start Ollama server in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Pull the model if not already present
echo "Checking for model ${OLLAMA_MODEL:-llama3.1:8b-instruct-q4_K_M}..."
if ! ollama list | grep -q "${OLLAMA_MODEL:-llama3.1:8b-instruct-q4_K_M}"; then
    echo "Pulling model ${OLLAMA_MODEL:-llama3.1:8b-instruct-q4_K_M}..."
    ollama pull "${OLLAMA_MODEL:-llama3.1:8b-instruct-q4_K_M}"
else
    echo "Model already present"
fi

echo "AI Evaluator ready!"

# Keep container running and forward signals
wait $OLLAMA_PID
