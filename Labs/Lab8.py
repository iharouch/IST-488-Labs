import streamlit as st
import requests
from openai import OpenAI
import base64

#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "url_response" not in st.session_state:
    st.session_state.url_response = None

if "upload_response" not in st.session_state:
    st.session_state.upload_response = None

st.title("Image Captioning Bot")
st.caption("Provide the bot with either an image URL or an image file and it will generate a description and captions for it!")

st.subheader("Image URL Input")
image_url = st.text_input("Enter an image URL (the URL must lead directly to the image to avoid any errors):")

if st.button("Generate Captions"):
    if image_url:
        url_response = st.session_state.client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": url, "detail": "auto"}},
                        {"type": "text", "text":"Describe the image in at least 3 sentences. Write five different captions for this image."
                         "Captions must vary in length, minimum one word but no longer than two sentences."
                         "Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."}]
                         }]
        )
        st.session_state.url_response = url_response
    else:
        st.warning("Please enter an image URL.")

if st.session_state.url_response:
    st.image(st.session_state.url_response)
    st.write(st.session_state.url_response)

st.subheader("Image File Input")
image_file = st.file_uploader("Upload an image file:", type=["jpg", "jpeg", "png", "webp", "gif"])

if st.button("Generate Captions for Uploaded Image"):
    if image_file:
        b64 = base64.b64encode(image_file.read()).decode("utf-8")
        mime = image_file.type #e.g. "image/png"
        data_uri = f"data:{mime};base64,{b64}"

        upload_response = st.session_state.client.chat.completions.create(
            model="gpt-4.1-mini",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri, "detail": "auto"}},
                        {"type": "text", "text":"Describe the image in at least 3 sentences. Write five different captions for this image."
                         "Captions must vary in length, minimum one word but no longer than two sentences."
                         "Captions should vary in tone, such as, but not limited to funny, intellectual, and aesthetic."}]
                         }]
        )
        st.session_state.upload_response = upload_response

if st.session_state.upload_response:
    st.image(st.session_state.upload_response)
    st.write(st.session_state.upload_response)
