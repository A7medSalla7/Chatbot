from groq import Groq
import streamlit as st
import time

client = Groq(
    api_key="put your key"
)

# model_name = "llama-3.1-70b-versatile"
# model_name = "llama3-70b-8192"
model_name = "openai/gpt-oss-120b"
# model_name = "mixtral-8x7b-32768"


def add_msg(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})


def get_messages():
    return [
        {"role": m['role'], "content": m['content']}
        for m in st.session_state.messages
    ]


def get_response(prompt: str, role: str = 'user', rag_req: bool = False):

    if rag_req:
        rag_response(prompt)

    add_msg(role, prompt)

    chat_completion = client.chat.completions.create(
        messages=st.session_state.messages,  # type: ignore
        model=model_name,
    )

    response = chat_completion.choices[0].message.content or "No response"

    add_msg('assistant', response)

    return response


def stream_response(user_prompt: str, delay=0.005):

    response = get_response(user_prompt, rag_req=True)

    placeholder = st.empty()
    content = ""

    for word in response:
        content += word
        placeholder.markdown(content)
        time.sleep(delay)


def stream_ai_response(response: str, delay=0.001):

    placeholder = st.empty()
    content = ""

    for word in response:
        content += word
        placeholder.markdown(content)
        time.sleep(delay)


def rag_response(user_prompt: str):
    res_docs = st.session_state.infoRetrieval.query(user_prompt)

    res_docs_text = '\n'.join(res_docs)
    system_prompt = f"""
    Based on the following documents:
    {res_docs_text} 
    
    you can answer the following question if user asks you: 
    Question: "{user_prompt}". 
    """
    print(system_prompt)
    add_msg('system',  system_prompt)


def recommended_types_response(recommended_types: list[str]):
    rec_types = ', '.join(recommended_types)
    system_prompt = f"""
    After Making Some Operations 
    we found this products types are the most product types recommended to the user based on his transaction history in our bank:
    product types: {rec_types}
    
    if user asks you to recommend products based on these type:
    make him to specify which type you want to recommend and its description.
    but show the results of the recommended / recommend types to the user.
    """
    add_msg('system',  system_prompt)

