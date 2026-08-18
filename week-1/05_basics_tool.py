from langchain_core.tools import tool

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
    return weather_db.get(city.lower(), "general weather forecast: sunny")

llm_openai = ChatOpenAI(model="gpt-5.4-mini")

message  = [
    SystemMessage(content="You are a helpful assistant that can get the weather for a given city"),
    HumanMessage(content="What is the weather in New York?")
]



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


    base_rate = {india: 10.0, usa: 15.0, uk: 20.0, france: 25.0}.get(destination.lower(), 10.0)
    express_fee = 5.0 if express else 0.0
    cost_usd = base_rate * weight_kg + express_fee
    shipping_days = 5 if express else 10
    return {cost_usd: cost_usd, shipping_days: shipping_days}

  


print("--------------------------------")
print("tool name", get_weather.name)
print("tool description", get_weather.description)
print("tool parameters", get_weather.parameters)
print("tool schema", get_weather.args_schema.model_json_schema())
print("--------------------------------")
print("tool name", calculate_shipping_cost.name)
print("tool description", calculate_shipping_cost.description)
print("tool parameters", calculate_shipping_cost.parameters)
print("tool schema", calculate_shipping_cost.args_schema.model_json_schema())
print("--------------------------------")

