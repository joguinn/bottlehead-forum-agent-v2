# forum_agent.py
import streamlit as st
import os
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Load OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Set up LLM
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

# Load FAISS index (assumes it's stored in "faiss_index" folder)
@st.cache_resource
def load_agent():
    try:
        db = FAISS.load_local("faiss_index", embeddings=None, allow_dangerous_deserialization=True)
        retriever = db.as_retriever()
        return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    except Exception as e:
        st.error(f"❌ Error loading FAISS index: {e}")
        return None

forum_agent = load_agent()

def ask_forum_agent(query, product=None):
    if not forum_agent:
        return "⚠️ Forum agent is not available."

    # Optional filtering (handled manually)
    if product:
        retriever = forum_agent.retriever
        retriever.search_kwargs["filter"] = lambda doc: doc.metadata.get("product", "").lower() == product.lower()

    return forum_agent.run(query)
