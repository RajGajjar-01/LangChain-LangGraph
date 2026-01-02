from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="moonshotai/Kimi-K2-Instruct-0905",
    task="text-generation",
    temperature=0.6,  # Recommended by Moonshot AI
    max_new_tokens=4096,
)

chat_model = ChatHuggingFace(
    llm=llm
)

print(chat_model.invoke('What is spacex?').content)