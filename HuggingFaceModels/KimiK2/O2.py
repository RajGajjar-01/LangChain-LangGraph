from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent

load_dotenv()

@tool
def get_weather(city:str) -> dict:
    """Get current weather information for a city"""

    return {
        "city": city,
        "temperature": "25deg C",
        "condition": "Sunny"
    }

search = DuckDuckGoSearchRun()

llm = HuggingFaceEndpoint(
    repo_id="moonshotai/Kimi-K2-Instruct-0905",
    task="text-generation",
    temperature=0.6,  # Recommended by Moonshot AI
    max_new_tokens=512,
)

chat_model = ChatHuggingFace(llm=llm)
tools = [search, get_weather]

system_prompt = """You are Kimi, an intelligent AI assistant created by Moonshot AI.

You have access to:
- get_weather: Get current weather information for any city
- duckduckgo_search: Search the web for current information, news, and facts

Guidelines:
- Always use tools to provide accurate, up-to-date information
- Be concise and helpful
- Cite sources when using search results
- Think step-by-step before responding"""

agent = create_agent(
    model=chat_model,
    tools=tools,
    system_prompt=system_prompt
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Rajkot and search for latest news about Elon Musk"}]
})

print(result["messages"][-1].content)