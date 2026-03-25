import streamlit as st
from openai import OpenAI

#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

st.title("Responses API Chatbot")

prompt = st.text_input("Ask me a question!")
client = st.session_state.client

if prompt:
    response = client.responses.create(
        model="gpt-4.1",
        instructions="You are a helpful teaching assistant for an R course.",
        input=prompt
    )

    st.write(response.output_text)

    #Store response ID
    st.session_state.last_response_id = response.id

    if "last_response_id" in st.session_state:
        follow_up = st.text_input("Ask a follow-up question:", key="follow_up")
    
    if "last_response_id" in st.session_state and follow_up:
        follow_response = client.responses.create(
            model="gpt-4.1",
            instructions="You are a helpful teaching assistant for an R course.",
            input=follow_up,
            previous_response_id=st.session_state.last_response_id
        )

        st.write(follow_response.output_text)

        # Update last response variable for further follow-up questions
        st.session_state.last_response_id = follow_response.id

