import os
import json
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI

# Load OpenAI key from .env file or environment
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ You must set your OpenAI API key in a .env file or environment variable.")

# === Load Q&A Pairs ===
qa_docs = []

with open("bottlehead_qna.jsonl", "r") as f:
    for line in f:
        entry = json.loads(line)
        content = f"Q: {entry['question']}\nA: {entry['answer']}"
        metadata = {
            "product": entry["product"],
            "topic_id": entry["topic_id"],
            "url": entry["url"]
        }
        qa_docs.append(Document(page_content=content, metadata=metadata))

# === Create Vector Index ===
from langchain.text_splitter import RecursiveCharacterTextSplitter

print("🔍 Splitting and embedding documents...")

# Split long Q&A entries into smaller chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

chunked_docs = splitter.split_documents(qa_docs)

embeddings = OpenAIEmbeddings(api_key=openai_api_key)
db = FAISS.from_documents(chunked_docs, embeddings)
retriever = db.as_retriever()

# === Build the QA Agent ===
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(api_key=openai_api_key, temperature=0),
    retriever=retriever,
    return_source_documents=True
)

# === Interface ===
def ask_forum_agent(query: str):
    result = qa(query)
    answer = result["result"]
    source = result["source_documents"][0].metadata
    print("\n🧠 Answer:\n", answer)
    print("\n📚 Source Info:")
    print(f"Product: {source.get('product')}")
    print(f"URL: {source.get('url')}")
    print(f"Topic ID: {source.get('topic_id')}")

# === Optional: Run interactively ===
if __name__ == "__main__":
    while True:
        user_query = input("\nAsk a question about Bottlehead (or 'exit'): ")
        if user_query.strip().lower() in {"exit", "quit"}:
            break
        ask_forum_agent(user_query)

# === Agent function with optional product filter ===
def ask_forum_agent(query: str, product: str = None):
    # Optionally filter documents by product
    if product:
        matching_docs = [doc for doc in qa_docs if doc.metadata.get("product", "").lower() == product.lower()]
        split_docs = splitter.split_documents(matching_docs)
    else:
        split_docs = chunked_docs

    # Rebuild retriever from filtered docs
    local_db = FAISS.from_documents(split_docs, embeddings)
    local_retriever = local_db.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(api_key=openai_api_key, temperature=0),
        retriever=local_retriever,
        return_source_documents=True
    )

    result = qa_chain(query)
    answer = result["result"]
    source = result["source_documents"][0].metadata
    return {
        "answer": answer,
        "product": source.get("product", "Unknown"),
        "url": source.get("url", "N/A"),
        "topic_id": source.get("topic_id")
    }

    if not split_docs:
        return {
            "answer": "No matching forum entries found for this product.",
            "product": product or "All",
            "url": "N/A",
            "topic_id": "N/A"
        }

# === Optional: Terminal interface ===
if __name__ == "__main__":
    while True:
        user_query = input("\nAsk a question (or 'exit'): ")
        if user_query.strip().lower() in {"exit", "quit"}:
            break
        product = input("Filter by product (or press Enter to search all): ").strip()
        response = ask_forum_agent(user_query, product if product else None)

        print("\n🧠 Answer:\n", response["answer"])
        print("\n📚 Source Info:")
        print(f"Product: {response['product']}")
        print(f"URL: {response['url']}")