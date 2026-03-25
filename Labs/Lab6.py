import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

#Add title and caption to app
st.title("Responses API Chatbot")
st.caption("This bot has web search enabled.")

user_input = st.text_input("Ask me a question!") #User input
client = st.session_state.client

#Create sidebar with checkbox for structured mode
structured_mode = st.sidebar.checkbox("Return structured summary")

#Define the desired structure
class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str


if user_input:
    if structured_mode: #Use structured mode
        response = client.responses.parse(
            model="gpt-4.1",
            instructions="You are a helpful research assistant. Cite your sources.", #Set persona
            input=user_input,
            tools=[{"type": "web_search_preview"}], #Have web search available
            text_format=ResearchSummary
        )

        result = response.output_parsed

        st.write(result.main_answer)

        st.subheader("Key Facts")
        for fact in result.key_facts:
            st.write(f"- {fact}")

        st.caption(result.source_hint)
    
    else: #Use regular paragraph mode
        response = client.responses.create(
            model="gpt-4.1",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=user_input,
            tools=[{"type": "web_search_preview"}]
        )

        st.write(response.output_text)

    #Store response ID
    st.session_state.last_response_id = response.id

if "last_response_id" in st.session_state:
    follow_up = st.text_input("Ask a follow-up question:", key="follow_up")
    
    if follow_up:
        if structured_mode:
            follow_response = client.responses.parse(
                model="gpt-4.1",
                instructions="You are a helpful research assistant. Cite your sources.",
                input=follow_up,
                tools=[{"type": "web_search_preview"}],
                previous_response_id=st.session_state.last_response_id,
                text_format=ResearchSummary
            )

            result = follow_response.output_parsed

            st.write(result.main_answer)

            st.subheader("Key Facts")
            for fact in result.key_facts:
                st.write(f"- {fact}")

            st.caption(result.source_hint)

        else:
            follow_response = client.responses.create(
                model="gpt-4.1",
                instructions="You are a helpful research assistant. Cite your sources.",
                input=follow_up,
                tools=[{"type": "web_search_preview"}],
                previous_response_id=st.session_state.last_response_id
            )

            st.write(follow_response.output_text)

        # Update response id for follow-up questions
        st.session_state.last_response_id = follow_response.id

