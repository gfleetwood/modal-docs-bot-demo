import streamlit as st
import pandas as pd
import random
import openai
import time
from os import environ

from canopy.knowledge_base import KnowledgeBase
from canopy.tokenizer import Tokenizer
from canopy.models.data_models import Query
from canopy.context_engine import ContextEngine

def get_prompt_output(question, transcript):

    prompt_text = """
    The user is asking:
    
    {}
    
    The text below is the knowledge you need to answer the user's question. Only use information from what is given below, and give code examples when appropriate. 
    If the question is not related to the sources, reply "I don't know":
    
    {}
    """
    
    messages = [{"role": "system", "content": prompt_text.format(question, transcript)}]
    
    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo", messages = messages, max_tokens = 1000, temperature = 0
    )  
    
    prompt_output = response.choices[0].message.content
    
    return(prompt_output)

st.title("Modal Docs Bot Chat")
st.text("Ask questions about Modal Lab's documentation: https://modal.com/docs/examples")

Tokenizer.initialize()
kb = KnowledgeBase(index_name = environ["INDEX_NAME"])
kb.connect()
context_engine = ContextEngine(kb)

def get_db_content(question):

    result = context_engine.query([Query(text = question, top_k = 5)], max_context_tokens = 512)
    query = result.dict()["content"][0]['query']
    snippets = "\n\n".join(["source: {}\n\ntext: {}".format(x["source"], x["text"]) for x in result.dict()["content"][0]['snippets']])
    
    return((query, snippets))

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("I'm your modal bot please ask me questions"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        query, snippets = get_db_content(prompt)
        full_response = get_prompt_output(query, snippets)
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
