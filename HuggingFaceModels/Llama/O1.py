from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id='meta-llama/Llama-3.3-70B-Instruct',
    task="text-generation",
    max_new_tokens=2048,
)

model = ChatHuggingFace(llm = llm)

print(model.invoke('Hello'))