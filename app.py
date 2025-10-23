import streamlit as st
from ai_response_agent import (
    stream_ai_response,
)
from prompts import INIT_PROMPT
from pre_data.info_retrieval import InfoRetrieval
from function_call import FuncCall
from ai_tools import *


st.title("Sales Ai Chatbot")

print(' - '*40)

print(" - Checking if messages are in session state...")

if "messages" not in st.session_state:
    print(" -- Messages not found in session state. Initializing...")
    st.session_state.messages = [
        {
            "role": 'system',
            "content": INIT_PROMPT
        }
    ]
    print(" - Initialization complete.\n")

print(" - Checking if info retrieval model is in session state...")
if "infoRetrieval" not in st.session_state:

    with st.spinner(text='Loading...'):
        print(" -- Loading info retrieval model...")
        st.session_state.infoRetrieval = InfoRetrieval()
        st.session_state.infoRetrieval.load_chroma_collection()
        print(" - Loading info retrieval model... Done\n")

print(" - Checking if function call is in session state...")
if "funcall" not in st.session_state:

    with st.spinner(text='Loading...'):
        print(" -- Loading funcall...")
        st.session_state.funcall = FuncCall()
        print(" - Loading funcall... Done\n")


print(" - Streaming messages...")

for msg in st.session_state.messages:
    if msg['role'] == 'system':
        continue

    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

print(" - Checking if user input is available...")
if prompt := st.chat_input("Say something!"):

    st.session_state.user_prompt = prompt

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner(text='Thinking...'):

        import re

        res_func = st.session_state.funcall.query_raven(prompt)
        print(f' -- call function = {res_func}')
        
        # Extract only the function call between backticks
        match = re.search(r'`(.+?)`', res_func)
        if match:
            func_call_str = match.group(1)
            response = eval(func_call_str)
        else:
            response = "Sorry, I could not parse the function call."
        
        print(" - Response generated.\n")
        

    with st.chat_message("assistant"):
        print(" - Streaming response...")
        stream_ai_response(response)
        print(" - Streamed response done.\n")
    print('-'*40)
