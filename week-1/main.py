from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

print("Program started")

load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-mini")

m1 = "who is the president of the united states?"

print("Calling LLM...")

result = llm.invoke(m1)

print("LLM response:")
print(result)
print(result.content)