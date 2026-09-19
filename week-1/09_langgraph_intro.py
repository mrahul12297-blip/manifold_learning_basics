from typing import TypedDict, Annotated, Sequence
from operator import add  # add is a function that adds a message to the list, conversation history(accumulates)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
import json


load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)


# ==============state schema==============

class Support_State(TypedDict):

    messages: Annotated[list[BaseMessage], add]  # add is a function that adds a message to the list, conversation history(accumulates)
    customer_id: str
    customer_tier: str        # 'premium' | 'standard'
    issue_category: str       # 'billing' | 'shipping' | 'technical' | 'general'
    ticket_id: str
    final_response: str


# ===============tools===============

@tool
def get_customer_tier(customer_id: str) -> str:
    """
    look up a customer's tier (premium or standard) based on the customer id

    Args:
        customer_id: Customer ID string

    Returns:
        'premium' or 'standard'
    """

    premium_customers = ["CUST-001", "CUST-003", "CUST-007"]

    return "premium" if customer_id.upper() in premium_customers else "standard"


@tool
def create_ticket(customer_id: str, issue: str, priority: str) -> str:
    """
    create a support ticket

    Args:
        customer_id: Customer ID string
        issue: Issue description string
        priority: Priority level string (low, normal, high)

    Returns:
        Ticket ID
    """

    import random

    ticket_id = f"TICKET-{random.randint(1000, 9999)}"

    print(
        f"Ticket created: {ticket_id} for customer {customer_id} "
        f"with issue: {issue} and priority: {priority}"
    )

    return ticket_id


# ================nodes===============

def extract_customer_id(state: Support_State) -> dict:
    """extract the customer id from the latest message"""

    last_message = state["messages"][-1].content

    # simple extraction - in production use regex or NLP
    import re

    match = re.search(r'CUST-\d+', last_message.upper())
    customer_id = match.group(0) if match else 'customer-unknown'

    print(f"Extracted customer id: {customer_id}")
    return {"customer_id": customer_id}


def lookup_tier(state: Support_State) -> dict:
    """ lookup customer tier via tool """

    tier = get_customer_tier.invoke({
        "customer_id": state["customer_id"]
    })

    print(f"Customer tier: {tier}")

    return {"customer_tier": tier}


def clasify_with_llm(state: Support_State) -> dict:
    """ use the llm to classify the issue """

    last_message = state["messages"][-1].content

    classification_prompt = [

        SystemMessage(
            content="classify their customer support issue into exactly one category: billing, shipping, technical, general. return only the category name nothing else."
        ),

        HumanMessage(
            content=f"Issue: {last_message}"
        ),

    ]

    response = llm.invoke(classification_prompt)
    category = response.content.strip().lower()

    # validate the category
    valid = ["billing", "shipping", "technical", "general"]

    if category not in valid:
        category = "general"

    print(f"Classified issue category: {category}")
    return {"issue_category": category}


def handle_premium_path(state: Support_State) -> dict:
    """ premium customer path - priority handling """

    ticket_id = create_ticket.invoke({
        "customer_id": state["customer_id"],
        "issue": state["issue_category"],
        "priority": "high"
    })

    response_message = [

        SystemMessage(
            content="You are a customer support agent. You are helping a premium customer with a high priority issue. Be warm, personalised, Maximum 3 sentences."
        ),

        HumanMessage(
            content=f"""
Customer_issue: {state["messages"][-1].content}

Issue_category: {state["issue_category"]}

ticket_id: {ticket_id}

Tell the customer their priority ticket has been created and they will receive a response within 24 hours.
"""
        )

    ]

    response = llm.invoke(response_message)

    print("[premium_path] generated premium response")
    return {
        "ticket_id": ticket_id,
        "final_response": response.content,
        "messages": [AIMessage(content=response.content)],
    }


def handle_standard_path(state: Support_State) -> dict:
    """ standard customer path - normal SLA. """

    ticket_id = create_ticket.invoke({
        "customer_id": state["customer_id"],
        "issue": state["issue_category"],
        "priority": "normal"
    })

    response_message = [

        SystemMessage(
            content="You are a customer support agent. You are helping a standard customer with a normal priority issue. Be warm, personalised, Maximum 3 sentences."
        ),

        HumanMessage(
            content=f"""
Customer_issue: {state["messages"][-1].content}

Issue_category: {state["issue_category"]}

ticket_id: {ticket_id}

Tell the customer their ticket has been created and they will receive a response within 48 hours.
"""
        )

    ]

    response = llm.invoke(response_message)

    print("[standard_path] generated standard response")

    return {
        "ticket_id": ticket_id,
        "final_response": response.content,
        "messages": [AIMessage(content=response.content)],
    }


# ========================= conditional routing graph =========================

def route_by_customer_tier(state: Support_State) -> str:

    if state["customer_tier"] == "premium":
        return "handle_premium_path"

    return "handle_standard_path"


# ========================= build graph =========================

builder = StateGraph(Support_State)

builder.add_node("extract_customer_id", extract_customer_id)
builder.add_node("lookup_tier", lookup_tier)
builder.add_node("clasify_with_llm", clasify_with_llm)
builder.add_node("handle_premium_path", handle_premium_path)
builder.add_node("handle_standard_path", handle_standard_path)

builder.add_edge(START, "extract_customer_id")
builder.add_edge("extract_customer_id", "lookup_tier")
builder.add_edge("lookup_tier", "clasify_with_llm")

builder.add_conditional_edges(
    "clasify_with_llm",
    route_by_customer_tier,
    {
        "handle_premium_path": "handle_premium_path",
        "handle_standard_path": "handle_standard_path",
    }
)

builder.add_edge("handle_premium_path", END)
builder.add_edge("handle_standard_path", END)
graph = builder.compile()


# ==========================run=========================

print("=" * 60)
print("Test: premium customer with high priority issue")
print("=" * 60)

initial_state = {

    "messages": [
        HumanMessage(
            content="I'm CUST-001, a premium customer and I have a high priority issue with my account."
        )
    ],

    "customer_id": "cust-001",
    "customer_tier": "premium",
    "issue_category": "billing",
    "ticket_id": "",
    "final_response": "",

}

result = graph.invoke(initial_state)
print(f"\nFINAL_RESPONSE: {result['final_response']}")
print(f"\nTICKET_ID: {result['ticket_id']}")
print(f"\ncustomer_tier: {result['customer_tier']}")
print(f"\nissue_category: {result['issue_category']}")
print("\n" + "=" * 60)