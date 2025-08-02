import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

# Get OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Set up LLM and embeddings
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def build_forum_agent(df):
    """Create a retriever from a CSV-loaded DataFrame with 'question', 'answer', and optional 'product' columns."""

    # Ensure required columns
    if "question" not in df.columns or "answer" not in df.columns:
        raise ValueError("DataFrame must contain 'question' and 'answer' columns.")

    docs = []
    for i, row in df.iterrows():
        q = str(row["question"]).strip()
        a = str(row["answer"]).strip()
        metadata = {}

        # Optional product filter
        if "product" in df.columns and pd.notna(row["product"]):
            metadata["product"] = row["product"].strip()

        content = f"Q: {q}\nA: {a}"
        docs.append(Document(page_content=content, metadata=metadata))

    # Split long docs
    split_docs = splitter.split_documents(docs)

    # Embed and store in FAISS (in-memory)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    retriever = vectorstore.as_retriever()

    # Build retrieval QA chain
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def ask_forum_agent(query, product=None):
    """Run a query with optional product filtering."""

    # Optional metadata filtering
    if product:
        def filter_by_product(doc):
            return doc.metadata.get("product", "").lower() == product.lower()
        retriever = forum_agent.retriever
        retriever.search_kwargs["filter"] = filter_by_product

    # Query agent
    response = forum_agent.run(query)
    return response
