from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="moonshotai/Kimi-K2-Instruct-0905",
    task="text-generation",
    temperature=0.2,  # Recommended by Moonshot AI
    max_new_tokens=2048,
)

chat_model = ChatHuggingFace(
    llm = llm
)

messages = [
    {"role": "system", "content": "You are a great teacher just like Richard Feymann, you have to teach python concepts with indepth knowledge and with multiple examples ranging from basic ones to advanced ones"},
    {"role": "user", "content": "Explain Python decorators in depth."}
]

response = chat_model.invoke(messages)
print(response.content)

# from langchain_huggingface import HuggingFaceEndpoint

# # Use automatic provider selection for best performance
# llm = HuggingFaceEndpoint(
#     repo_id="moonshotai/Kimi-K2-Instruct-0905:fastest",  # Auto-selects fastest provider
#     temperature=0.6,
#     max_new_tokens=2048,
# )
