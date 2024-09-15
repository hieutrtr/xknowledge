from langchain.vectorstores import Milvus
from langchain.embeddings import OpenAIEmbeddings
   
class MilvusHandler:
    def __init__(self, collection_name, uri, embedding_size):
        self.collection_name = collection_name
        self.uri = uri
        self.embedding_size = embedding_size
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Milvus(self.embeddings, uri=self.uri, collection_name=self.collection_name, embedding_size=self.embedding_size)
    
    def store_embeddings(self, texts):
        self.vectorstore.add_texts(texts)
    
    def retrieve_documents(self, query, k=5):
        return self.vectorstore.similarity_search(query, k=k)