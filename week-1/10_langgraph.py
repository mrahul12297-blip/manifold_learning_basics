from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. Define State
class SimpleState(TypedDict):
    city: str
    weather: str
    booking: str

# 2. Define Nodes
def check_weather_node(state):
    return {"weather": "sunny"}

def book_node(state):
    return {"booking": "confirmed"}

# 3. Build Graph
workflow = StateGraph(SimpleState)
workflow.add_node("check_weather", check_weather_node)
workflow.add_node("book", book_node)

# 4. Add Edges
workflow.set_entry_point("check_weather")
workflow.add_edge("check_weather", "book")
workflow.add_edge("book", END)

# 5. Compile & Run
app = workflow.compile()

#export the graph to a png file
app.get_graph().draw_mermaid_png(output_file_path="weather_app.png")
result = app.invoke({"city": "Bangalore"})
print(result)







































# from typing import TypedDict

# # 💡 Think of State as: A database that moves with your workflow. Each step can read it, update it, and pass it forward

# class TravelState(TypedDict):
#     city: str              # Where the user wants to go
#     weather: str           # Weather info
#     budget: float          # User's budget
#     booking: dict          # Booking details
#     user_approved: bool    # Did user approve?



# # Nodes = Functions That Do Work
# # Each node receives state, does something, and returns state updates.
# #💡 Node Pattern: Read state → Do work → Return updates. That's it!

# def check_weather_node(state: TravelState):
#     """Node that checks weather"""
#     city = state["city"]
#     weather = get_weather(city)  # Call your tool
#     return {"weather": weather}  # Update state

# def check_budget_node(state: TravelState):
#     """Node that validates budget"""
#     if state["budget"] < 10000:
#         return {"error": "Budget too low"}
#     return {"budget_ok": True}

# def book_flight_node(state: TravelState):
#     """Node that books the flight"""
#     booking = book_flight(state["city"])
#     return {"booking": booking}



# # Edges = Flow Control
# #Edges connect nodes. They can be normal (always go to B) or conditional (go to B or C based on state).

# workflow.add_edge("check_weather", "book_flight")
# # Always: check_weather → book_flight



# def should_book(state: TravelState) -> str:
#     """Decide where to go next"""
#     if state["weather"] == "sunny":
#         return "book_flight"
#     else:
#         return "suggest_alternative"

# workflow.add_conditional_edges(
#     "check_weather",           # From this node
#     should_book,               # Use this function to decide
#     {
#         "book_flight": "book_flight",           # If returns "book_flight"
#         "suggest_alternative": "suggest_alternative"  # If returns "suggest_alternative"
#     }
# )