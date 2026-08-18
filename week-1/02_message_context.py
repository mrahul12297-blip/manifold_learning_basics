from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-mini")