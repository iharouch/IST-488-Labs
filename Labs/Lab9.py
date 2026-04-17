import streamlit as st
import json 
import os
from openai import OpenAI

# Long-term Memory Chatbot
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

client = st.session_state.client

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Long-term Memory Chatbot")

# Load memories from file
def load_memories():
    file_path = "memories.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

# Save memories to file
def save_memories(memories):
    with open("memories.json", "w") as file:
        json.dump(memories, file, indent=4)

# Display memories in the sidebar
st.sidebar.title("Memories")
memories = load_memories()

if memories:
    for m in memories:
        st.sidebar.write(f"- {m}")
else:
    st.sidebar.write("No memories yet. Start chatting!")

if st.sidebar.button("Clear Memories"):
    save_memories([])
    st.rerun()

system_prompt = "You are a helpful assistant."
if memories:
    memory_str = "\n".join([f"- {m}" for m in memories])
    system_prompt += (
        "\n\nHere are things you remember about this user from past conversations:\n" + memory_str + "\nUse this information to personalize your responses."
    )

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask me anything")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.chat_message("user").write(user_input)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.messages)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    assistant_msg = response.choices[0].message.content

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_msg}
    )

    st.chat_message("assistant").write(assistant_msg)

    # Second LLM call to extract memories
    extraction_prompt = f"""
    You are a system that extracts facts about a user. Analyze this conversation and extract new facts about the user worth remembering (name, preferences, location, interests, etc.)

    Existing memories:
    ```json
    {json.dumps(memories)}
    ```

    Conversation:
    User message: {user_input}
    Assistant response: {assistant_msg}

    Return ONLY a JSON list of new facts. If no new facts, return [].
    Example: ["User's name is Ines", "User studies at Syracuse University"]
    """

    extraction_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    extracted_text = extraction_response.choices[0].message.content

    try:
        new_memories = json.loads(extracted_text)
        if new_memories:
            memories.extend(new_memories)
            memories = list(set(memories)) # removes duplicates
            save_memories(memories)
            st.rerun()
    except json.JSONDecodeError:
        pass


