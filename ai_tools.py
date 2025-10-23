from ai_response_agent import (
    get_response,
    recommended_types_response
)
import streamlit as st
import re
import nltk
from nltk.corpus import stopwords
from custom_rec_sys import CustomRecSys


stop_words = set(stopwords.words('english'))


def advanced_string_search(statement: str, big_string: str) -> bool:
    # Function to clean text by removing non-alphabetical characters

    # Normalize and clean the strings
    normalized_statement = statement.strip().lower()
    normalized_big_string = big_string.strip().lower()

    # Split the normalized and cleaned statement into individual words
    words = normalized_statement.split()

    # Check if all words are present in the big string (in any order)
    res = [re.search(re.escape(word), normalized_big_string) for word in words]

    print('-'*50)
    print(f"words: {words}")
    print(f"res: {res}")

    ratio = res.count(None) / len(words)
    print(f"ratio: {ratio}")
    print('-'*50)
    return ratio < 0.5


def clean_text(text: str) -> str:
    stop_words = set(stopwords.words('english'))

    # Clean the text by removing non-alphabetical characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Split the text into words
    words = cleaned_text.split()

    # Filter out the stopwords
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Join the filtered words back into a single string
    return ' '.join(filtered_words)


def is_question_answered(user_prompt: str) -> bool:

    clean_user_prompt = clean_text(user_prompt)
    for msg in st.session_state.messages:
        clean_big_msg = clean_text(msg['content'])
        if advanced_string_search(clean_user_prompt, clean_big_msg):
            return True

    return False


user_id = 558398

def get_user_id(): return user_id


def recommend_product_based_on_historical_behavior(user_id: int):
    """
    Recommend a product based on user historical behavior.

    Args:
        user_id (int): The ID of the user for whom to recommend a product.

    Returns:
        The response to the user's prompt, based on the recommended product.
    """

    if is_question_answered(user_prompt=st.session_state.user_prompt):
        print("The question has been answered before")
        return get_response(st.session_state.user_prompt, rag_req=False)

    if "rec_sys" not in st.session_state:
        print(" -- rec_sys not found in session state. Initializing...")
        st.session_state.rec_sys = CustomRecSys("qty")
        print(" - Initialization complete.\n")

    rec_prod_types = st.session_state.rec_sys.recommend_products_types(
        get_user_id())
    print(rec_prod_types)
    recommended_types_response(rec_prod_types)
    return get_response(st.session_state.user_prompt, rag_req=False)


def fetch_and_filter_products(user_prompt: str | None = None):

    if is_question_answered(user_prompt=st.session_state.user_prompt):

        print("The question has been answered before")
        return get_response(st.session_state.user_prompt, rag_req=False)

    return get_response(st.session_state.user_prompt, rag_req=True)


def give_normal_response(user_prompt: str | None = None):
    return get_response(st.session_state.user_prompt, rag_req=False)
