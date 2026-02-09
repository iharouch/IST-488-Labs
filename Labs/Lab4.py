import streamlit as st
from openai import OpenAI
import sys
import chromadb
from pathlib import Path
import fitz

# A fix for working with ChromaDB on Streamlit
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

#Create ChromaDB client and collection
if 'Lab4_VectorDB' not in st.session_state:
    chroma_client = chromadb.PersistentClient(path="./ChromaDB_for_Lab")
    st.session_state.Lab4_VectorDB = chroma_client.get_or_create_collection(name="Lab4Collection")

collection = st.session_state.Lab4_VectorDB 

### Using Chroma DB with OpenAI Embeddings ###
#Create an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

#A function that will add documents to collection
def add_to_collection(collection, text, file_name):
    """
    Collection = collection, already defined
    text = extarcted text from PDF
    file_name = name of the PDF file
    Embeddings inserted into the collection from OpenAI
    """
    #Create an embedding
    client = st.session_state.client
    response = client.embeddings.create(
        input = text,
        model = "text-embedding-3-small"
    )

    #Get the embedding vector
    embedding = response.data[0].embedding

    #Add embedding and document to ChromaDB
    collection.add(
        documents = [text],
        ids = file_name,
        embeddings = [embedding]
    )

### Extract text from PDF ###
def extract_text_from_pdf(file_path):
    """
    file_path = path to PDF file
    returns extracted text from PDF
    """
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

### Populate collection with PDFs ###
def load_pdfs_to_collection(folder_path, collection):
    """
    folder_path = path to folder containing PDFs
    collection = ChromaDB collection
    """
    pdf_files = Path(folder_path).glob("*.pdf")
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        add_to_collection(collection, text, pdf_file.stem)

#Check if collection is empty and load PDFs
if st.session_state.Lab4_VectorDB.count() == 0:
    loaded = load_pdfs_to_collection("./Labs/Lab-04-Data/", st.session_state.Lab4_VectorDB)

### Main App ###
st.title("Lab 4: Chatbot using RAG")

### Querying A Collection -- Only used for testing ###
topic = st.sidebar.text_input("Topic", placeholder="Type your topic (e.g. GenAI)...")

if topic:
    client = st.session_state.client
    response = client.embeddings.create(
        input = topic,
        model = "text-embedding-3-small"
    )

    #Get the embedding vector
    query_embedding = response.data[0].embedding

    #Get the text related to this question (this prompt)
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results=3 #The number of closest documents to return
    )

    #Display the results
    st.subheader(f'Results for: {topic}')

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]

        st.write(f'**{i+1}. {doc_id}**')

else:
    st.info('Enter a topic in the sidebar to search the collection.')