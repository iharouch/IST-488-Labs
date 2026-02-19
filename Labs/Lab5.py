import requests
import json
import streamlit as st
from openai import OpenAI

SYSTEM_PROMPT = """
Follow these steps STRICTLY:
1. The user will provide a location (City, State, Country).
2. If needed, call the weather tool and indicate in your response that you used it.
3. Provide a short summary of the weather information to the user.
4. Provide clothing recommendations to the user based on the weather.
5. Provide outdoor activities suggestions appropriate to the weather.
"""

#Weather function
def get_current_weather(location, api_key, units="imperial"):
    url = (
        f'https://api.openweathermap.org/data/2.5/weather'
        f'?q={location}&appid={api_key}&units={units}'
    ) # Creates URL based on parameters
    
    response = requests.get(url)

    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')
    
    data = response.json()

    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']

    return {'location': location,
            'temperature': round(temp, 2),
            'feels_like': round(feels_like, 2),
            'temp_min': round(temp_min, 2),
            'temp_max': round(temp_max, 2),
            'humidity': round(humidity, 2)}

#Tools
tools = [
    {
        "type": "function",
        "function":{
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state (e.g., New York, NY)",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this unit from the forecast location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
]
    
#Streamlit App
st.title("The 'What to Wear' Bot")
st.subheader("This application allows you to enter a location (City, State, Country) and receive clothing and outdoor activity recommendations based on the weather.")

location = st.text_input("Enter a location (City, State, Country):") # Input for user to enter location

#Create an OpenAI client
if 'client' not in st.session_state:
    st.session_state.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) # Get API key from secrets.toml file

client = st.session_state.client
weather_api_key = st.secrets["WEATHER_API_KEY"]

#Use Syracuse, NY as default if location is empty
if location == "":
    location = "Syracuse, NY"

if location:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": location}
    ]

    response = client.chat.completions.create(
        model = 'gpt-5-mini',
        messages = messages,
        tools = tools,
        tool_choice='auto'
    )

    message = response.choices[0].message

    #Check if the response from the model includes a tool call
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        weather_data = get_current_weather(arguments.get("location", "Syracuse, NY"), weather_api_key)
    
        # Include tool response in messages
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(weather_data)
        })
        messages.append({
            "role": "user",
            "content": f"What's the weather like in {arguments.get('location', 'Syracuse, NY')}?"
        })

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )

        # Stream the response to the app using `st.write_stream`.
        st.write(stream.choices[0].message.content)
    
    else: #If model doesn't use tools
        st.write(message.content)

