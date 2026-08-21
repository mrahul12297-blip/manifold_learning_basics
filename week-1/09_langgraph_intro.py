from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class Support_Agent_State(TypedDict):
    """ shared state for the agent
    every node reads this and write back to it
    """

    user_message: str
    customer_tier: str
    issue_category: str
    response: str

# defining the nodes

def classify_issue(state: Support_Agent_State) -> Support_Agent_State:
    """ classify the issue into a category 
    Reads: user_message
    Writes: issue_category """

    message = state["user_message"]
    if any(word in message for word in ["billing", "payment", "invoice", "price", "cost"]):
        category = "billing"
    elif any(word in message for word in ["shipping", "delivery", "tracking", "order", "product"]):
        category = "shipping"
    else:
        category = "technical"

    return {"issue_category": category}



def look_up_customer_tier(state: Support_Agent_State) -> Support_Agent_State:
    """ 
    node: look up the customer tier 
    Reads: user_message
    Writes: customer_tier """


    category = state["issue_category"]
    if category == "billing":
        tier = "gold"
    elif category == "shipping":
        tier = "silver"
    else:
        tier = "bronze"
    return {"customer_tier": tier}




# no need to focus much on this file, it is half done.