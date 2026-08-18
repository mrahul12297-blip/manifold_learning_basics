from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import time
from langchain_core.exceptions import OutputParserException




load_dotenv()

llm_openai = ChatOpenAI(model="gpt-5.4-mini")

#pattern 1: try-except block

# pattern 2 : fallback message

def safe_invoke(message, fallback_message = "I am sorry, I cannot answer that question."):
    try:
        response = llm_openai.invoke(message)
        return response.content
    except Exception as e:
        print(f"Error: LLM call failed")
        return fallback_message

print(safe_invoke([HumanMessage(content="What is the capital of France?")]))
