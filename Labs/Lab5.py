import requests
import streamlit as st

def get_current_weather(location, api_key, units="imperial"):
    location = st.input("Enter a location (City, State, Country):") # Input for user to enter location
    api_key = st.secrets["WEATHER_API_KEY"] # Get API key from secrets.toml file
    
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

