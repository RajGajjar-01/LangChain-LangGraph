# Langchain + Langgraph Examples

A small collection of examples demonstrating integration between LangChain, Langgraph, and different models. This repository contains notebooks and example scripts for running local experiments and model endpoints.

## How to Initialize the Repo

### Using UV (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Install dependencies
uv pip install -e .

# Or sync dependencies (if you have a uv.lock file)
uv sync
```
