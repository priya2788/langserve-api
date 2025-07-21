# langserve-api/main.py
import os
from fastapi import FastAPI
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langserve import add_routes
from dotenv import load_dotenv
import requests

load_dotenv()

# API tools
@Tool
def get_weather(city: str) -> str:
    return requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}"
        f"&appid={os.getenv('OPENWEATHERMAP_API_KEY')}&units=metric"
    ).json()

@Tool
def get_news(topic: str) -> str:
    return requests.get(
        f"https://newsapi.org/v2/everything?q={topic}"
        f"&apiKey={os.getenv('NEWSAPI_API_KEY')}"
    ).json()

@Tool
def get_definition(word: str) -> str:
    return requests.get(
        f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    ).json()

tools = [get_weather, get_news, get_definition]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Use tools to answer questions about weather, news, or word definitions. 
    Always respond clearly and concisely, using only the data from the tools. Do not make up information."""),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])
llm = AzureOpenAI(
    azure_deployment="GPTO4_training",
     api_base=str(url),
     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
     api_version=os.getenv("AZURE_OPENAI_VERSION"),
     max_retries=2,
 )
#llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

app = FastAPI()
add_routes(app, agent_executor, path="/chat")
