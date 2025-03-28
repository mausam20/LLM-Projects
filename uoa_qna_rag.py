from dotenv import load_dotenv
import os
import json

import openai
import faiss
import numpy as np
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import gradio as gr


load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")


# Open and read the JSON file
with open("faq_data.json", "r", encoding="utf-8") as file:
    faq_data = json.load(file)



# Initialize OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

# Create embeddings for each FAQ answer
faq_embeddings = [embeddings.embed_text(faq['answer']) for faq in faq_data]

# Convert the embeddings into a numpy array
embedding_vectors = np.array(faq_embeddings)

# Initialize FAISS index
dimension = len(embedding_vectors[0])  # Embedding size
index = faiss.IndexFlatL2(dimension)  # L2 distance metric (Euclidean)

# Add the FAQ embeddings to the index
index.add(embedding_vectors)

# You may also want to store the corresponding FAQ metadata (question, answer) in a separate list
faq_metadata = [{"question": faq['question'], "answer": faq['answer']} for faq in faq_data]

# Create a FAISS vector store with your embeddings and metadata
faiss_store = FAISS(embedding_function=embeddings.embed_text, index=index, metadata=faq_metadata)

# Initialize OpenAI model
llm = OpenAI()

# Create a RetrievalQA chain using the retriever (FAISS) and OpenAI model
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=faiss_store.as_retriever())

# Define the Gradio function
def ask_question(query):
    response = qa_chain.run(query)
    return response

# Build Gradio UI
iface = gr.Interface(
    fn=ask_question,
    inputs=gr.Textbox(label="Ask a Question"),
    outputs=gr.Textbox(label="Answer"),
    title="University of Arizona FAQ Chatbot",
    description="Ask any questions about admissions, financial aid, and more!"
)

# Launch Gradio App
iface.launch()