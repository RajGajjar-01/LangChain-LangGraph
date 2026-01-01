import os
from itertools import cycle

# List of tokens from different accounts
HF_TOKENS = [
    os.environ["HF_TOKEN_1"],
    os.environ["HF_TOKEN_2"],
    os.environ["HF_TOKEN_3"],
    os.environ["HF_TOKEN_4"],
    os.environ["HF_TOKEN_5"],
]

# Create a token rotator
token_pool = cycle(HF_TOKENS)

# Use next token for each request
from langchain_huggingface import HuggingFaceEndpoint

def get_llm():
    return HuggingFaceEndpoint(
        repo_id="moonshotai/Kimi-K2-Instruct-0905",
        huggingfacehub_api_token=next(token_pool),
        temperature=0.6
    )
