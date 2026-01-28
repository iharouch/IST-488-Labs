import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Lab 2 - MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer!"
)

# Store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets.OPENAI_API_KEY

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)
client.models.list() # Validates the key by asking for the models that the key is compatible with

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)

# Provide user with options for model selection
use_advanced_model = st.sidebar.checkbox("Use advanced model (gpt-5.2)", value=False) # Checkbox that uses most advanced model if checked

if use_advanced_model:
    model_option = 'gpt-5.2'
else:
    model_option = st.sidebar.selectbox("Choose a model:", [
        'gpt-5-mini',
        'gpt-5-nano',
        'gpt-4.1',
        'gpt-5.2'
    ], index=0) # Selectbox for model choice if not automatically using advanced model with 4.1 as default

# Provide user with three options for generating a summary
summary_option = st.sidebar.radio("Choose a summary type:", [
    'Summarize the document in 100 words',
    'Summarize the document in 2 connecting paragraphs',
    'Summarize the document in 5 bullet points'
], disabled=not uploaded_file) # Disabled until the file is uploaded

if st.sidebar.button("Generate Summary", disabled=not uploaded_file):
    if uploaded_file:
        # Process the uploaded file
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {summary_option}",
            }
        ] # API call takes summary option into account

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model=model_option, # Use selected model
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)