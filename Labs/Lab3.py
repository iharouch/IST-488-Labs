import streamlit as st
from openai import OpenAI

#Show title and description
st.title("MY Lab3 question answering chatbot")

openAI_model = st.sidebar.selectbox("Select OpenAI model",
                                    ("mini", "regular"))
if openAI_model == "mini":
    model = "gpt-4o-mini"
else:
    model = "gpt-4o"

#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if 'messages' not in st.session_state:
    st.session_state['messages'] = \
        [{"role": "assistant", "content": "How can I help you?"}]
    
for msg in st.session_state.messages:
    #st.chat_message(msg["role"]).write(msg["content"])
    #with st.chat_message(msg["role"]):
    #    st.write(msg["content"])
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What do you need help with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model,
        messages = st.session_state.messages,
        stream = True
    )

    with st.chat_messages("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})