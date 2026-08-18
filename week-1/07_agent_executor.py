from re import A
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain.agents import create_agent  



load_dotenv()

@tool
# tool decorator is used to define a function as a tool that can be used in the LLM
def get_weather(city: str) -> str:
    """Get the current weather for a given city
    Args:
        city: The city to get the weather for (eg. New York, London, Paris)
    Returns:
        The current weather for the city (eg. sunny, rainy, cloudy)
    """

    weather_db = {
        "New York": "sunny",
        "London": "rainy",
        "Paris": "cloudy"
    }
    return weather_db.get(city, "general weather forecast: sunny")


@tool
def calculate_shipping_cost(weight_kg: float, destination: str,
                            express: bool = False) -> dict:
    """Calculate the shipping cost for a given weight and destination
    Args:
        weight_kg: The weight of the package in kilograms
        destination: The destination of the package (eg. USA, UK, France)
        express: Whether the shipping is express (eg. True, False)
    Returns:
        The shipping cost for the package with 'cost_usd' and 'shipping_days'
    """

    base_rate = {
        "india": 10.0,
        "usa": 15.0,
        "uk": 20.0,
        "france": 25.0
    }.get(destination.lower(), 10.0)

    express_fee = 5.0 if express else 0.0
    cost_usd = base_rate * weight_kg + express_fee
    shipping_days = 5 if express else 10

    return {
        "cost_usd": cost_usd,
        "shipping_days": shipping_days
    }



@tool
def write_user_name(name: str) -> str:
    """Write the user's name to the file
    Args:
        name: The name of the user to write to the file
    Returns:
        The message that the user's name has been written to the file
    """

    with open("user_names.txt", "a") as f:
        f.write(name + "\n")
    return f"User {name} has been written to the file"







tools = [get_weather, calculate_shipping_cost, write_user_name]

agent = create_agent(
    model=ChatOpenAI(model="gpt-5.4-mini"),
    tools=tools,
    system_promot = "You are a helpful assistant that can get the weather for a given city and calculate the shipping cost for a given weight and destination"
)



# result = agent.invoke({"messages":[
#     {"role":"user",
#     "content":"What is the weather in New York?"}
# ]})
# print(result)



result = agent.invoke({"messages":[
    {"role":"user",
    "content":"Write the name as rahul to the file"}
]})
print(result)


