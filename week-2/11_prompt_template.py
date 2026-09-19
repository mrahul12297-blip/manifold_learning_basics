from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain.agents import create_agent  
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-mini")



# note: bad prompt how it looks like:

def bad_prompt(customer_name: str, tier: str, issue: str) -> str:
    """ problems: no validation, easy to inject and hard to test
    """
    return f"you are a customer support agent for technoshop, an electronics shop.customer(name: {customer_name}, tier: {tier}) is having the following issue: {issue}"
    # what if the issue  = ignore your instructions and ....""


# GOOD: Structured template with explicit variable slots

support_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional customer support agent for {company_name}.

Customer Details:
- Name: {customer_name}
- Tier: {customer_tier}
- Account Status: {account_status}

Guidelines:
- Be concise (max 3 sentences)
- If tier is 'premium', acknowledge their priority status
- If account_status is 'suspended', do NOT offer new services
- Date: {current_date}"""),
    MessagesPlaceholder(variable_name="history", optional=True),
    ("human", "{user_input}"),
])

# Template KNOWS what it needs — validation before LLM call
print(support_prompt.input_variables)
# ['company_name', 'customer_name', 'customer_tier', 'account_status', 'current_date', 'user_input']
print("================================================")


message = support_prompt.format_messages(
    company_name="TechnoShop",
    customer_name="John Doe",
    customer_tier="premium",
    account_status="active",
    current_date="2026-08-24",
    user_input="I'm having problem in my mobile"
)

print("formatted message:", message)
print("================================================")

response = llm.invoke(message)
print("response:", response)
print("================================================")



# PARTIAL PROMPT

from datetime import datetime

partial_prompt = support_prompt.partial(
    company_name="TechnoShop",
    current_date=datetime.now().strftime("%Y-%m-%d")
)

print("partial_prompt:", partial_prompt)
print("================================================")

#user specific field are populated per call
message = partial_prompt.format_messages(
    customer_name="priyanka",
    customer_tier="standard",
    account_status="active",
    user_input="I'm having problem in my mental state"
)

print("partial_prompt_message:", partial_prompt)

response2 = llm.invoke(message)
print("response2:", response2)
print("================================================")




