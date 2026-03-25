import streamlit as st
from openai import OpenAI

#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

st.title("Responses API Chatbot")
prompt = st.text_input("Ask me a question!")
client = st.session_state.client

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a helpful teaching assistant for an R course.",
    input=prompt
)

print(response.output_text)
