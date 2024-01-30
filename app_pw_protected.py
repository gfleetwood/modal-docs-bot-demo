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
    
    The text below is the knowledge you need to answer the user's question. 
    Only use information from what is given below, and give code examples when appropriate. 
    Always cite the included sources. If the question is not related to the sources, reply "I don't know":
    
    {}
    """
    
    messages = [{"role": "system", "content": prompt_text.format(question, transcript)}]
    
    response = openai.chat.completions.create(
        # gpt-4-1106-preview
        # gpt-3.5-turbo
        model = "gpt-4-1106-preview", messages = messages, max_tokens = 1000, temperature = 0
    )  
    
    prompt_output = response.choices[0].message.content
    
    return(prompt_output)

def get_db_content(question):

    result = context_engine.query([Query(text = question, top_k = 5)], max_context_tokens = 512)
    query = result.dict()["content"][0]['query']
    snippets = "\n\n".join(["source: {}\n\ntext: {}".format(x["source"], x["text"]) for x in result.dict()["content"][0]['snippets']])
    sources = "Sources:\n\n" + "\n\n".join([x["source"] for x in result.dict()["content"][0]['snippets']])
    
    return((query, snippets, sources))

st.title("Modal Docs Bot Chat")
st.text("Ask questions about Modal Lab's documentation: https://modal.com/docs/examples")

Tokenizer.initialize()
kb = KnowledgeBase(index_name = 'canopy--test')
kb.connect()
context_engine = ContextEngine(kb)

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "authorized" not in st.session_state:
    st.session_state.authorized = 0
    
if "msg" not in st.session_state:
    st.session_state.msg = 'Enter password for access to bot.'

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

'''
prompt-pw, auth, result
0,0, wrong pw
0,1, access
1,0, set authorization to 1
1,1, access
'''

if prompt := st.chat_input(st.session_state.msg):

    if prompt != 'apple' and st.session_state.authorized != 1:
        message_placeholder = st.empty()
        message_placeholder.markdown('Wrong password. Try again')
    elif prompt == 'apple' and st.session_state.authorized != 1:
        st.session_state.authorized = 1
        message_placeholder = st.empty()
        message_placeholder.markdown('Access granted!')
        st.session_state.msg = 'I\'m your modal chat bot. Ask me anything!'
    elif st.session_state.authorized == 1:       
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            query, snippets, sources = get_db_content(prompt)
            full_response = get_prompt_output(query, snippets) + "\n\n" + sources
            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
