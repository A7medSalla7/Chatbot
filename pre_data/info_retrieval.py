from sentence_transformers import CrossEncoder
import numpy as np
import warnings
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import pickle
import time

warnings.filterwarnings('ignore')


def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(
            f"Function {func.__name__} took {end_time - start_time} seconds to execute")
        return result
    return wrapper


class InfoRetrieval:
    def __init__(self, chroma_data_path: str = 'pre_data\\chroma_data\\collection_data.pkl'):
        self.is_collection_loaded = False
        self.chroma_collection: chromadb.Collection | None = None
        self.cross_encoder = None
        self.chroma_data_path = chroma_data_path

    def load_chroma_collection(self):

        chroma_client = chromadb.Client()
        embedding_function = SentenceTransformerEmbeddingFunction()

        chroma_collection = chroma_client.get_or_create_collection(
            name="banking-products-chroma",
            embedding_function=embedding_function
        )

        with open(self.chroma_data_path, 'rb') as file:
            data = pickle.load(file)

        # Extract IDs and documents
        new_ids = data['ids']
        token_split_texts = data['documents']

        chroma_collection.add(
            ids=new_ids,
            documents=token_split_texts
        )

        self.chroma_collection = chroma_collection
        self.cross_encoder = CrossEncoder(
            'cross-encoder/ms-marco-MiniLM-L-6-v2')

        self.is_collection_loaded = True

    def query(self, query_text: str, n_results: int = 10):
        if not self.is_collection_loaded:
            self.load_chroma_collection()

        res_docs = self.chroma_collection.query(  # type: ignore
            query_texts=[query_text],
            n_results=n_results
        )['documents'][0]

        reranked_docs = self.rerank_docs(res_docs, query_text)

        return list(reranked_docs)

    def rerank_docs(self, res_docs, query_text):

        pairs = [[query_text, doc] for doc in res_docs]
        scores = self.cross_encoder.predict(pairs)   # type: ignore

        new_sorted_indexes = np.argsort(scores)[::-1]
        new_sorted_docs = np.array(res_docs)[new_sorted_indexes]

        if len(new_sorted_docs) > 5:
            new_sorted_docs = new_sorted_docs[:5]
        return new_sorted_docs
