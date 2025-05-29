from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from typing import Dict, List

def indexed_docs(docs: Dict[str, str]) -> FAISS:
    documents = [Document(page_content=text, metadata={'ticker': ticker}) for ticker, text in docs.items()]
    model_name = 'all-MiniLM-L6-v2'
    model_kwargs = {'device': 'cpu'}
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

def rag_agent(query: str, vectorstore: FAISS, k: int = 5) -> List[Document]:
    results = vectorstore.similarity_search_with_score(query=query, k=k)
    return [Document(page_content=doc.page_content, metadata={**doc.metadata, 'score': score}) for doc, score in results]